import json
import logging
import os
from aws_lambda_typing.events import APIGatewayProxyEventV2
from aws_lambda_typing.context import Context as LambdaContext
from aws_lambda_typing.responses import APIGatewayProxyResponseV2
from EventCoord.launchdarkly.flags import Flags
from EventCoord.models.radios import Radio
from EventCoord.utils.response import build_response
from aws_xray_sdk.core import patch_all, xray_recorder

patch_all()  # Automatically patches boto3, requests, etc.

xray_recorder.configure(service='incident-cmd')

# Setup logging
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger(__name__)
logging.getLogger("EventCoord.client.auth").setLevel(LOG_LEVEL)

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
    radio_id = path_params.get('radioId') if path_params else None

    if method == 'GET':
        if radio_id:
            item = Radio.get(org_id, radio_id)
            if not item:
                return build_response(
                    404,
                    {'error': 'Radio not found'},
                    headers=cors_headers
                )
            return build_response(200, item, headers=cors_headers)
        else:
            items = Radio.list(org_id)
            return build_response(200, items, headers=cors_headers)

    elif method == 'POST':
        import uuid
        body = json.loads(event.get('body', '{}'))
        if 'radioId' not in body:
            body['radioId'] = str(uuid.uuid4())
        body['org_id'] = org_id
        Radio.create(org_id, body)
        return build_response(
            201,
            {'message': 'Radio created', 'id': body['radioId']},
            headers=cors_headers
        )

    elif method == 'PUT':
        if not radio_id:
            return build_response(
                400,
                {'error': 'Missing radio id in path'},
                headers=cors_headers
            )
        body = json.loads(event.get('body', '{}'))
        Radio.update(org_id, radio_id, body)
        return build_response(
            200,
            {'message': 'Radio updated', 'id': radio_id},
            headers=cors_headers
        )

    elif method == 'DELETE':
        if not radio_id:
            return build_response(
                400,
                {'error': 'Missing radio id in path'},
                headers=cors_headers
            )
        if not flags.has_admin_access():
            return build_response(
                403,
                {'error': 'Admin privileges required for delete'},
                headers=cors_headers
            )
        Radio.delete(org_id, radio_id)
        return build_response(204, {}, headers=cors_headers)

    else:
        return build_response(405, {'error': 'Method not allowed'}, headers=cors_headers)
