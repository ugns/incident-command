import json
from EventCoord.utils.types import APIGatewayProxyEvent
from aws_lambda_typing.context import Context as LambdaContext
from EventCoord.utils.types import APIGatewayProxyResponse
from EventCoord.launchdarkly.flags import Flags
from EventCoord.models.radios import Radio
from EventCoord.utils.response import build_response
from EventCoord.utils.handler import CORS_HEADERS, get_claims, get_logger, init_tracing

init_tracing()
logger = get_logger(__name__)


def lambda_handler(
    event: APIGatewayProxyEvent,
    context: LambdaContext
) -> APIGatewayProxyResponse:
    logger.debug(f"Radios event: {event}")
    logger.debug(f"Radios context: {context}")
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
    radio_id = path_params.get('radioId') if path_params else None

    if method == 'GET':
        if radio_id:
            item = Radio.get(org_id, radio_id)
            if not item:
                return build_response(
                    404,
                    {'error': 'Radio not found'},
                    headers=CORS_HEADERS
                )
            return build_response(200, item, headers=CORS_HEADERS)
        else:
            items = Radio.list(org_id)
            return build_response(200, items, headers=CORS_HEADERS)

    elif method == 'POST':
        import uuid
        body = json.loads(event.get('body') or '{}')
        if 'radioId' not in body:
            body['radioId'] = str(uuid.uuid4())
        body['org_id'] = org_id
        Radio.create(org_id, body)
        return build_response(
            201,
            {'message': 'Radio created', 'id': body['radioId']},
            headers=CORS_HEADERS
        )

    elif method == 'PUT':
        if not radio_id:
            return build_response(
                400,
                {'error': 'Missing radio id in path'},
                headers=CORS_HEADERS
            )
        body = json.loads(event.get('body') or '{}')
        Radio.update(org_id, radio_id, body)
        return build_response(
            200,
            {'message': 'Radio updated', 'id': radio_id},
            headers=CORS_HEADERS
        )

    elif method == 'DELETE':
        if not radio_id:
            return build_response(
                400,
                {'error': 'Missing radio id in path'},
                headers=CORS_HEADERS
            )
        if not flags.has_admin_access():
            return build_response(
                403,
                {'error': 'Admin privileges required for delete'},
                headers=CORS_HEADERS
            )
        Radio.delete(org_id, radio_id)
        return build_response(204, {}, headers=CORS_HEADERS)

    else:
        return build_response(405, {'error': 'Method not allowed'}, headers=CORS_HEADERS)
