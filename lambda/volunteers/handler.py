import json
import logging
import os
from aws_lambda_typing.events import APIGatewayProxyEventV2
from aws_lambda_typing.context import Context as LambdaContext
from aws_lambda_typing.responses import APIGatewayProxyResponseV2
from EventCoord.launchdarkly.flags import Flags
from EventCoord.models.volunteers import Volunteer
from EventCoord.utils.response import build_response, decode_claims
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
    logger.debug(f"Volunteers event: {event}")
    logger.debug(f"Volunteers context: {context}")
    claims = decode_claims(event)
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
    volunteer_id = path_params.get('volunteerId') if path_params else None
    resource_path = event.get('resource', '') or event.get('path', '')

    if method == 'GET':
        if volunteer_id:
            item = Volunteer.get(org_id, volunteer_id)
            if not item:
                return build_response(
                    404,
                    {'error': 'Volunteer not found'},
                    headers=cors_headers
                )
            return build_response(200, item, headers=cors_headers)
        else:
            items = Volunteer.list(org_id)
            return build_response(200, items, headers=cors_headers)

    elif method == 'POST':
        if volunteer_id:
            return build_response(
                405,
                {'error': 'Method not allowed: use PUT to update volunteer'},
                headers=cors_headers
            )
        import uuid
        body = json.loads(event.get('body', '{}'))
        item = Volunteer.create(org_id, body)
        return build_response(
            201,
            {'message': 'Volunteer created', 'id': item['volunteerId']},
            headers=cors_headers
        )

    elif method == 'PUT':
        if not volunteer_id:
            return build_response(
                400,
                {'error': 'Missing volunteer id in path'},
                headers=cors_headers
            )
        body = json.loads(event.get('body', '{}'))
        body['volunteerId'] = volunteer_id
        body['org_id'] = org_id
        if '/checkin' in resource_path:
            body['status'] = 'checked_in'
        elif '/checkout' in resource_path:
            body['status'] = 'checked_out'
        elif '/dispatch' in resource_path:
            body['status'] = 'dispatched'
        Volunteer.update(org_id, volunteer_id, body)
        return build_response(
            200,
            {'message': 'Volunteer updated', 'id': volunteer_id},
            headers=cors_headers
        )

    elif method == 'DELETE':
        if not volunteer_id:
            return build_response(
                400,
                {'error': 'Missing volunteer id in path'},
                headers=cors_headers
            )
        if not flags.has_admin_access():
            return build_response(
                403,
                {'error': 'Admin privileges required for delete'},
                headers=cors_headers
            )
        Volunteer.delete(org_id, volunteer_id)
        return build_response(204, {}, headers=cors_headers)

    else:
        return build_response(405, {'error': 'Method not allowed'}, headers=cors_headers)
