import json
from EventCoord.utils.types import APIGatewayProxyEvent
from aws_lambda_typing.context import Context as LambdaContext
from EventCoord.utils.types import APIGatewayProxyResponse
from EventCoord.launchdarkly.flags import Flags
from EventCoord.models.activitylogs import ActivityLog
from EventCoord.utils.response import build_response
from EventCoord.utils.handler import CORS_HEADERS, get_claims, get_logger, init_tracing

init_tracing()
logger = get_logger(__name__)


def lambda_handler(
    event: APIGatewayProxyEvent,
    context: LambdaContext
) -> APIGatewayProxyResponse:
    logger.debug(f"Authorizer event: {event}")
    logger.debug(f"Authorizer context: {context}")
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
    log_id = path_params.get('logId') if path_params else None
    volunteer_id = path_params.get('volunteerId') if path_params else None
    period_id = path_params.get('periodId') if path_params else None

    if method == 'GET':
        if log_id:
            item = ActivityLog.get(org_id, log_id)
            if not item or item.get('org_id') != org_id:
                return build_response(
                    404,
                    {'error': 'Activity log not found'},
                    headers=CORS_HEADERS
                )
            return build_response(200, item, headers=CORS_HEADERS)
        elif volunteer_id:
            items = ActivityLog.list_by_volunteer(org_id, volunteer_id)
            return build_response(200, items, headers=CORS_HEADERS)
        elif period_id:
            items = ActivityLog.list_by_period(org_id, period_id)
            return build_response(200, items, headers=CORS_HEADERS)
        else:
            items = ActivityLog.list(org_id)
            return build_response(200, items, headers=CORS_HEADERS)

    elif method == 'POST':
        import uuid
        from datetime import datetime, timezone
        body = json.loads(event.get('body', '{}'))
        if 'logId' not in body:
            body['logId'] = str(uuid.uuid4())
        if 'periodId' not in body or not body['periodId']:
            return build_response(
                400,
                {'error': 'Missing required field: periodId'},
                headers=CORS_HEADERS
            )
        if 'timestamp' not in body or not body['timestamp']:
            body['timestamp'] = datetime.now(
                timezone.utc).isoformat().replace('+00:00', 'Z')
        body['org_id'] = org_id
        ActivityLog.create(org_id, body)
        return build_response(
            201,
            {'message': 'Activity log created', 'id': body['logId']},
            headers=CORS_HEADERS
        )

    elif method == 'PUT':
        if not log_id:
            return build_response(
                400,
                {'error': 'Missing activity log id in path'},
                headers=CORS_HEADERS
            )
        from datetime import datetime, timezone
        body = json.loads(event.get('body', '{}'))
        body['logId'] = log_id
        if 'periodId' not in body or not body['periodId']:
            return build_response(
                400,
                {'error': 'Missing required field: periodId'},
                headers=CORS_HEADERS
            )
        if 'timestamp' not in body or not body['timestamp']:
            body['timestamp'] = datetime.now(
                timezone.utc).isoformat().replace('+00:00', 'Z')
        body['org_id'] = org_id
        ActivityLog.update(org_id, log_id, body)
        return build_response(
            200,
            {'message': 'Activity log updated', 'id': log_id},
            headers=CORS_HEADERS
        )

    elif method == 'DELETE':
        if not log_id:
            return build_response(
                400,
                {'error': 'Missing activity log id in path'},
                headers=CORS_HEADERS
            )
        if not flags.has_super_admin_access():
            return build_response(
                403,
                {'error': 'Admin privileges required for delete'},
                headers=CORS_HEADERS
            )
        ActivityLog.delete(org_id, log_id)
        return build_response(204, {}, headers=CORS_HEADERS)

    else:
        return build_response(405, {'error': 'Method not allowed'}, headers=CORS_HEADERS)
