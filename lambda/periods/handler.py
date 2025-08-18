import os
import json
import logging
from aws_lambda_typing.events import APIGatewayProxyEventV2
from aws_lambda_typing.context import Context as LambdaContext
from aws_lambda_typing.responses import APIGatewayProxyResponseV2
from EventCoord.launchdarkly.flags import Flags
from EventCoord.models.periods import Period
from EventCoord.utils.response import build_response
from aws_xray_sdk.core import patch_all, xray_recorder

patch_all()  # Automatically patches boto3, requests, etc.

xray_recorder.configure(service='incident-cmd')

# Setup logging
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s %(name)s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logging.getLogger().setLevel(LOG_LEVEL)

cors_headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS"
}


def lambda_handler(
    event: APIGatewayProxyEventV2,
    context: LambdaContext
) -> APIGatewayProxyResponseV2:
    claims = event.get('requestContext', {}).get('authorizer', {})
    if claims is None:
        claims = {}
    elif not isinstance(claims, dict):
        try:
            claims = dict(claims)
        except Exception:
            claims = {}
    flags = Flags(claims)
    org_id = claims.get('org_id')
    if not org_id:
        return build_response(
            403,
            {'error': 'Missing organization (org_id claim) in token'},
            headers=cors_headers
        )

    method = event.get('httpMethod', 'GET')
    path_params = event.get('pathParameters') or {}
    period_id = path_params.get('periodId') if path_params else None

    if method == 'GET':
        if period_id:
            item = Period.get(org_id, period_id)
            if not item or item.get('org_id') != org_id:
                return build_response(
                    404,
                    {'error': 'Period not found'},
                    headers=cors_headers
                )
            return build_response(200, item, headers=cors_headers)
        else:
            items = Period.list(org_id)
            return build_response(200, items, headers=cors_headers)

    elif method == 'POST':
        # Create a new ICS-214 period
        import uuid
        body = json.loads(event.get('body', '{}'))
        if 'periodId' not in body:
            body['periodId'] = str(uuid.uuid4())
        if 'incidentId' not in body:
            return build_response(
                400,
                {'error': 'Missing incidentId in request body'},
                headers=cors_headers
            )
        incident_id = body['incidentId']
        body['org_id'] = org_id
        Period.create(org_id, incident_id, body)
        return build_response(
            201,
            {'message': 'Period created', 'id': body['periodId']},
            headers=cors_headers
        )

    elif method == 'PUT':
        # Update an existing ICS-214 period
        if not period_id:
            return build_response(
                400,
                {'error': 'Missing period id in path'},
                headers=cors_headers
            )
        body = json.loads(event.get('body', '{}'))
        Period.update(org_id, period_id, body)
        return build_response(
            200,
            {'message': 'Period updated', 'id': period_id},
            headers=cors_headers
        )

    elif method == 'DELETE':
        if not period_id:
            return build_response(
                400,
                {'error': 'Missing period id in path'},
                headers=cors_headers
            )
        if not flags.has_admin_access():
            return build_response(
                403,
                {'error': 'Admin privileges required for delete'},
                headers=cors_headers
            )
        Period.delete(org_id, period_id)
        return build_response(204, {}, headers=cors_headers)

    else:
        return build_response(405, {'error': 'Method not allowed'}, headers=cors_headers)
