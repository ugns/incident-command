import os
import uuid
import boto3
import json
from EventCoord.utils.types import APIGatewayProxyEvent
from aws_lambda_typing.context import Context as LambdaContext
from EventCoord.utils.types import APIGatewayProxyResponse
from EventCoord.launchdarkly.flags import Flags
from EventCoord.models.organizations import Organization
from EventCoord.utils.response import build_response
from EventCoord.utils.handler import CORS_HEADERS, get_claims, get_logger, init_tracing

init_tracing()
logger = get_logger(__name__)


def lambda_handler(
    event: APIGatewayProxyEvent,
    context: LambdaContext
) -> APIGatewayProxyResponse:
    logger.debug(f"Organizations event: {event}")
    logger.debug(f"Organizations context: {context}")
    claims = get_claims(event)
    flags = Flags(claims)
    method = event.get('httpMethod', 'GET')
    path_params = event.get('pathParameters') or {}
    org_id = path_params.get('org_id') if path_params else None
    aud = path_params.get('aud') if path_params else None

    if method == 'GET':
        if org_id:
            org = Organization.get_by_org_id(org_id)
            if not org:
                return build_response(
                    404,
                    {'error': 'Organization not found'},
                    headers=CORS_HEADERS
                )
            return build_response(200, org, headers=CORS_HEADERS)
        elif aud:
            org = Organization.get_by_aud(aud)
            if not org:
                return build_response(
                    404,
                    {'error': 'Organization not found'},
                    headers=CORS_HEADERS
                )
            return build_response(200, org, headers=CORS_HEADERS)
        else:
            items = Organization.list_all()
            return build_response(200, items, headers=CORS_HEADERS)

    elif method == 'POST':
        body = json.loads(event.get('body') or '{}')
        if not flags.has_super_admin_access():
            return build_response(
                403,
                {'error': 'Super Admin privileges required for create'},
                headers=CORS_HEADERS
            )

        aud = body.get('aud')
        name = body.get('name')
        if not aud or not name:
            return build_response(
                400,
                {'error': 'Missing aud or name in request body'},
                headers=CORS_HEADERS
            )
        org = Organization.create(aud, name)
        return build_response(201, org, headers=CORS_HEADERS)

    elif method == 'PUT':
        if not org_id:
            return build_response(
                400,
                {'error': 'Missing org_id in path'},
                headers=CORS_HEADERS
            )
        if not flags.has_super_admin_access():
            return build_response(
                403,
                {'error': 'Super Admin privileges required for update'},
                headers=CORS_HEADERS
            )
        body = json.loads(event.get('body') or '{}')
        updates = {k: v for k, v in body.items() if k in (
            'aud', 'name', 'hd', 'notes')}
        if not updates:
            return build_response(
                400,
                {'error': 'No valid fields to update'},
                headers=CORS_HEADERS
            )
        org = Organization.update(org_id, updates)
        if not org:
            return build_response(
                404,
                {'error': 'Organization not found'},
                headers=CORS_HEADERS
            )
        return build_response(200, org, headers=CORS_HEADERS)

    elif method == 'DELETE':
        if not org_id:
            return build_response(
                400,
                {'error': 'Missing org_id in path'},
                headers=CORS_HEADERS
            )
        if not flags.has_super_admin_access():
            return build_response(
                403,
                {'error': 'Super Admin privileges required for delete'},
                headers=CORS_HEADERS
            )
        Organization.delete(org_id)
        return build_response(204, {}, headers=CORS_HEADERS)

    else:
        return build_response(405, {'error': 'Method not allowed'}, headers=CORS_HEADERS)
