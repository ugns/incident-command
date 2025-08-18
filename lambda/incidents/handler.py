import json
import logging
import os
from aws_lambda_typing.events import APIGatewayProxyEventV2
from aws_lambda_typing.context import Context as LambdaContext
from aws_lambda_typing.responses import APIGatewayProxyResponseV2
from EventCoord.launchdarkly.flags import Flags
from EventCoord.models.incidents import Incident
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
    logger.debug(f"Incidents event: {event}")
    logger.debug(f"Incidents context: {context}")
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
    incident_id = path_params.get('incidentId') if path_params else None

    if method == 'GET':
        if incident_id:
            item = Incident.get(org_id, incident_id)
            if not item:
                return build_response(
                    404,
                    {'error': 'Incident not found'},
                    headers=cors_headers
                )
            return build_response(200, item, headers=cors_headers)
        else:
            items = Incident.list(org_id)
            return build_response(200, items, headers=cors_headers)

    elif method == 'POST':
        import uuid
        body = json.loads(event.get('body', '{}'))
        if 'incidentId' not in body:
            body['incidentId'] = str(uuid.uuid4())
        body['org_id'] = org_id
        Incident.create(org_id, body)
        return build_response(
            201,
            {'message': 'Incident created', 'id': body['incidentId']},
            headers=cors_headers
        )

    elif method == 'PUT':
        if not incident_id:
            return build_response(
                400,
                {'error': 'Missing incident id in path'},
                headers=cors_headers
            )
        body = json.loads(event.get('body', '{}'))
        Incident.update(org_id, incident_id, body)
        return build_response(
            200,
            {'message': 'Incident updated', 'id': incident_id},
            headers=cors_headers
        )

    elif method == 'DELETE':
        if not incident_id:
            return build_response(
                400,
                {'error': 'Missing incident id in path'},
                headers=cors_headers
            )
        if not flags.has_admin_access():
            return build_response(
                403,
                {'error': 'Admin privileges required for delete'},
                headers=cors_headers
            )
        Incident.delete(org_id, incident_id)
        return build_response(204, {}, headers=cors_headers)

    else:
        return build_response(405, {'error': 'Method not allowed'}, headers=cors_headers)
