import json
from EventCoord.utils.types import APIGatewayProxyEvent
from aws_lambda_typing.context import Context as LambdaContext
from EventCoord.utils.types import APIGatewayProxyResponse
from EventCoord.launchdarkly.flags import Flags
from EventCoord.models.units import Unit
from EventCoord.utils.response import build_response
from EventCoord.utils.handler import CORS_HEADERS, get_claims, get_logger, init_tracing

init_tracing()
logger = get_logger(__name__)


def lambda_handler(
    event: APIGatewayProxyEvent,
    context: LambdaContext
) -> APIGatewayProxyResponse:
    logger.debug(f"Units event: {event}")
    logger.debug(f"Units context: {context}")
    claims = get_claims(event)
    flags = Flags(claims)
    org_id = claims.get('org_id')
    if not org_id:
        return build_response(
            403,
            {'error': 'Missing organization (org_id claim) in token'},
            headers=CORS_HEADERS
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
                    headers=CORS_HEADERS
                )
            return build_response(200, item, headers=CORS_HEADERS)
        else:
            items = Unit.list(org_id)
            return build_response(200, items, headers=CORS_HEADERS)

    elif method == 'POST':
        import uuid
        body = json.loads(event.get('body') or '{}')
        if 'unitId' not in body:
            body['unitId'] = str(uuid.uuid4())
        body['org_id'] = org_id
        Unit.create(org_id, body)
        return build_response(
            201,
            {'message': 'Unit created', 'id': body['unitId']},
            headers=CORS_HEADERS
        )

    elif method == 'PUT':
        if not unit_id:
            return build_response(
                400,
                {'error': 'Missing unit id in path'},
                headers=CORS_HEADERS
            )
        body = json.loads(event.get('body') or '{}')
        Unit.update(org_id, unit_id, body)
        return build_response(
            200,
            {'message': 'Unit updated', 'id': unit_id},
            headers=CORS_HEADERS
        )

    elif method == 'DELETE':
        if not unit_id:
            return build_response(
                400,
                {'error': 'Missing unit id in path'},
                headers=CORS_HEADERS
            )
        if not flags.has_admin_access():
            return build_response(
                403,
                {'error': 'Admin privileges required for delete'},
                headers=CORS_HEADERS
            )
        Unit.delete(org_id, unit_id)
        return build_response(204, {}, headers=CORS_HEADERS)

    else:
        return build_response(405, {'error': 'Method not allowed'}, headers=CORS_HEADERS)
