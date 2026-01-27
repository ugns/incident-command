import base64
import json
from EventCoord.utils.types import APIGatewayProxyEvent
from aws_lambda_typing.context import Context as LambdaContext
from EventCoord.utils.types import APIGatewayProxyResponse
from EventCoord.launchdarkly.flags import Flags
from EventCoord.models.periods import Period
from EventCoord.utils.csv_export import items_to_csv
from EventCoord.utils.csv_import import build_natural_key, parse_csv_rows, prune_empty_fields
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
        if resource_path.endswith('/import'):
            body = event.get('body') or ''
            if event.get('isBase64Encoded') and body:
                body = base64.b64decode(body).decode('utf-8')
            if not body:
                return build_response(
                    400,
                    {'error': 'Missing CSV body'},
                    headers=CORS_HEADERS
                )
            rows = parse_csv_rows(body)
            existing = Period.list(org_id)
            existing_map = {}
            for item in existing:
                key = build_natural_key(item, ['name', 'startTime'])
                if key:
                    existing_map[key] = item
            created = updated = skipped = 0
            errors = []
            for index, row in enumerate(rows, start=2):
                row.pop('org_id', None)
                row.pop('periodId', None)
                key = build_natural_key(row, ['name', 'startTime'])
                if not key:
                    skipped += 1
                    errors.append({'row': index, 'error': 'Missing name or startTime'})
                    continue
                existing_item = existing_map.get(key)
                if existing_item:
                    updates = prune_empty_fields(row)
                    if not updates:
                        skipped += 1
                        continue
                    merged = {**existing_item, **updates}
                    merged.pop('org_id', None)
                    merged.pop('periodId', None)
                    Period.update(org_id, existing_item['periodId'], merged)
                    updated += 1
                else:
                    if not row.get('incidentId'):
                        skipped += 1
                        errors.append({'row': index, 'error': 'Missing incidentId'})
                        continue
                    created_item = Period.create(org_id, row['incidentId'], row)
                    created += 1
                    existing_map[key] = created_item
            return build_response(
                200,
                {
                    'created': created,
                    'updated': updated,
                    'skipped': skipped,
                    'errors': errors,
                },
                headers=CORS_HEADERS
            )
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
