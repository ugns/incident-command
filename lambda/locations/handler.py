import json
from EventCoord.utils.types import APIGatewayProxyEvent
from aws_lambda_typing.context import Context as LambdaContext
from EventCoord.utils.types import APIGatewayProxyResponse
from EventCoord.launchdarkly.flags import Flags
from EventCoord.models.locations import Location
from EventCoord.utils.response import build_response
from EventCoord.utils.handler import CORS_HEADERS, get_claims, get_logger, init_tracing

init_tracing()
logger = get_logger(__name__)


def lambda_handler(
    event: APIGatewayProxyEvent,
    context: LambdaContext
) -> APIGatewayProxyResponse:
    logger.debug(f"Locations event: {event}")
    logger.debug(f"Locations context: {context}")
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
    location_id = path_params.get('locationId') if path_params else None

    if method == 'GET':
        if location_id:
            item = Location.get(org_id, location_id)
            if not item:
                return build_response(
                    404,
                    {'error': 'Location not found'},
                    headers=CORS_HEADERS
                )
            return build_response(200, item, headers=CORS_HEADERS)
        else:
            items = Location.list(org_id)
            return build_response(200, items, headers=CORS_HEADERS)

    elif method == 'POST':
        import uuid
        body = json.loads(event.get('body', '{}'))
        if 'locationId' not in body:
            body['locationId'] = str(uuid.uuid4())
        body['org_id'] = org_id
        Location.create(org_id, body)
        return build_response(
            201,
            {'message': 'Location created', 'id': body['locationId']},
            headers=CORS_HEADERS
        )

    elif method == 'PUT':
        if not location_id:
            return build_response(
                400,
                {'error': 'Missing location id in path'},
                headers=CORS_HEADERS
            )
        body = json.loads(event.get('body', '{}'))
        Location.update(org_id, location_id, body)
        return build_response(
            200,
            {'message': 'Location updated', 'id': location_id},
            headers=CORS_HEADERS
        )

    elif method == 'DELETE':
        if not location_id:
            return build_response(
                400,
                {'error': 'Missing location id in path'},
                headers=CORS_HEADERS
            )
        if not flags.has_admin_access():
            return build_response(
                403,
                {'error': 'Admin privileges required for delete'},
                headers=CORS_HEADERS
            )
        Location.delete(org_id, location_id)
        return build_response(204, {}, headers=CORS_HEADERS)

    else:
        return build_response(405, {'error': 'Method not allowed'}, headers=CORS_HEADERS)
