import json
import logging
import os
from aws_lambda_typing.events import APIGatewayProxyEventV2
from aws_lambda_typing.context import Context as LambdaContext
from aws_lambda_typing.responses import APIGatewayProxyResponseV2
from EventCoord.launchdarkly.flags import Flags
from EventCoord.models.units import Unit
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
    logger.debug(f"Units event: {event}")
    logger.debug(f"Units context: {context}")
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
    unit_id = path_params.get('unitId') if path_params else None

    if method == 'GET':
        if unit_id:
            item = Unit.get(org_id, unit_id)
            if not item:
                return build_response(
                    404,
                    {'error': 'Unit not found'},
                    headers=cors_headers
                )
            return build_response(200, item, headers=cors_headers)
        else:
            items = Unit.list(org_id)
            return build_response(200, items, headers=cors_headers)

    elif method == 'POST':
        import uuid
        body = json.loads(event.get('body', '{}'))
        if 'unitId' not in body:
            body['unitId'] = str(uuid.uuid4())
        body['org_id'] = org_id
        Unit.create(org_id, body)
        return build_response(
            201,
            {'message': 'Unit created', 'id': body['unitId']},
            headers=cors_headers
        )

    elif method == 'PUT':
        if not unit_id:
            return build_response(
                400,
                {'error': 'Missing unit id in path'},
                headers=cors_headers
            )
        body = json.loads(event.get('body', '{}'))
        Unit.update(org_id, unit_id, body)
        return build_response(
            200,
            {'message': 'Unit updated', 'id': unit_id},
            headers=cors_headers
        )

    elif method == 'DELETE':
        if not unit_id:
            return build_response(
                400,
                {'error': 'Missing unit id in path'},
                headers=cors_headers
            )
        if not flags.has_admin_access():
            return build_response(
                403,
                {'error': 'Admin privileges required for delete'},
                headers=cors_headers
            )
        Unit.delete(org_id, unit_id)
        return build_response(204, {}, headers=cors_headers)

    else:
        return build_response(405, {'error': 'Method not allowed'}, headers=cors_headers)
