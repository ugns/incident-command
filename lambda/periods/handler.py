import json
from EventCoord.utils.types import APIGatewayProxyEvent
from aws_lambda_typing.context import Context as LambdaContext
from EventCoord.utils.types import APIGatewayProxyResponse
from EventCoord.launchdarkly.flags import Flags
from EventCoord.models.periods import Period
from EventCoord.utils.csv_export import items_to_csv
from EventCoord.utils.response import build_response
from EventCoord.utils.handler import CORS_HEADERS, get_claims, get_logger, init_tracing

init_tracing()
logger = get_logger(__name__)


def lambda_handler(
    event: APIGatewayProxyEvent,
    context: LambdaContext
) -> APIGatewayProxyResponse:
    logger.debug(f"Periods event: {event}")
    logger.debug(f"Periods context: {context}")
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
    period_id = path_params.get('periodId') if path_params else None
    resource_path = event.get('resource', '') or event.get('path', '')

    if method == 'GET':
        if resource_path.endswith('/export'):
            items = Period.list(org_id)
            csv_body = items_to_csv(items, exclude_fields={'org_id', 'periodId'})
            headers = {
                **CORS_HEADERS,
                'Content-Type': 'text/csv; charset=utf-8',
                'Content-Disposition': 'attachment; filename="periods.csv"',
            }
            return build_response(200, csv_body, headers=headers)
        if period_id:
            item = Period.get(org_id, period_id)
            if not item or item.get('org_id') != org_id:
                return build_response(
                    404,
                    {'error': 'Period not found'},
                    headers=CORS_HEADERS
                )
            return build_response(200, item, headers=CORS_HEADERS)
        else:
            items = Period.list(org_id)
            return build_response(200, items, headers=CORS_HEADERS)

    elif method == 'POST':
        # Create a new ICS-214 period
        import uuid
        body = json.loads(event.get('body') or '{}')
        if 'periodId' not in body:
            body['periodId'] = str(uuid.uuid4())
        if 'incidentId' not in body:
            return build_response(
                400,
                {'error': 'Missing incidentId in request body'},
                headers=CORS_HEADERS
            )
        incident_id = body['incidentId']
        body['org_id'] = org_id
        Period.create(org_id, incident_id, body)
        return build_response(
            201,
            {'message': 'Period created', 'id': body['periodId']},
            headers=CORS_HEADERS
        )

    elif method == 'PUT':
        # Update an existing ICS-214 period
        if not period_id:
            return build_response(
                400,
                {'error': 'Missing period id in path'},
                headers=CORS_HEADERS
            )
        body = json.loads(event.get('body') or '{}')
        Period.update(org_id, period_id, body)
        return build_response(
            200,
            {'message': 'Period updated', 'id': period_id},
            headers=CORS_HEADERS
        )

    elif method == 'DELETE':
        if not period_id:
            return build_response(
                400,
                {'error': 'Missing period id in path'},
                headers=CORS_HEADERS
            )
        if not flags.has_admin_access():
            return build_response(
                403,
                {'error': 'Admin privileges required for delete'},
                headers=CORS_HEADERS
            )
        Period.delete(org_id, period_id)
        return build_response(204, {}, headers=CORS_HEADERS)

    else:
        return build_response(405, {'error': 'Method not allowed'}, headers=CORS_HEADERS)
