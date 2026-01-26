import json
from aws_lambda_typing.events import APIGatewayProxyEvent
from aws_lambda_typing.context import Context as LambdaContext
from aws_lambda_typing.responses import APIGatewayProxyResponse
from EventCoord.launchdarkly.flags import Flags
from EventCoord.models.volunteers import Volunteer
from EventCoord.utils.response import build_response
from EventCoord.utils.handler import CORS_HEADERS, get_claims, get_logger, init_tracing

init_tracing()
logger = get_logger(__name__)


def lambda_handler(
    event: APIGatewayProxyEvent,
    context: LambdaContext
) -> APIGatewayProxyResponse:
    logger.debug(f"Volunteers event: {event}")
    logger.debug(f"Volunteers context: {context}")
    claims = get_claims(event)
    logger.debug(f"Claims: {claims}")
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
    volunteer_id = path_params.get('volunteerId') if path_params else None
    resource_path = event.get('resource', '') or event.get('path', '')

    if method == 'GET':
        if volunteer_id:
            item = Volunteer.get(org_id, volunteer_id)
            if not item:
                return build_response(
                    404,
                    {'error': 'Volunteer not found'},
                    headers=CORS_HEADERS
                )
            return build_response(200, item, headers=CORS_HEADERS)
        else:
            items = Volunteer.list(org_id)
            return build_response(200, items, headers=CORS_HEADERS)

    elif method == 'POST':
        if volunteer_id:
            return build_response(
                405,
                {'error': 'Method not allowed: use PUT to update volunteer'},
                headers=CORS_HEADERS
            )
        import uuid
        body = json.loads(event.get('body', '{}'))
        item = Volunteer.create(org_id, body)
        return build_response(
            201,
            {'message': 'Volunteer created', 'id': item['volunteerId']},
            headers=CORS_HEADERS
        )

    elif method == 'PUT':
        if not volunteer_id:
            return build_response(
                400,
                {'error': 'Missing volunteer id in path'},
                headers=CORS_HEADERS
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
            headers=CORS_HEADERS
        )

    elif method == 'DELETE':
        if not volunteer_id:
            return build_response(
                400,
                {'error': 'Missing volunteer id in path'},
                headers=CORS_HEADERS
            )
        if not flags.has_admin_access():
            return build_response(
                403,
                {'error': 'Admin privileges required for delete'},
                headers=CORS_HEADERS
            )
        Volunteer.delete(org_id, volunteer_id)
        return build_response(204, {}, headers=CORS_HEADERS)

    else:
        return build_response(405, {'error': 'Method not allowed'}, headers=CORS_HEADERS)
