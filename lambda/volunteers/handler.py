import base64
import json
from EventCoord.utils.types import APIGatewayProxyEvent
from aws_lambda_typing.context import Context as LambdaContext
from EventCoord.utils.types import APIGatewayProxyResponse
from EventCoord.launchdarkly.flags import Flags
from EventCoord.models.volunteers import Volunteer
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
        if resource_path.endswith('/export'):
            items = Volunteer.list(org_id)
            csv_body = items_to_csv(items, exclude_fields={'org_id', 'volunteerId'})
            headers = {
                **CORS_HEADERS,
                'Content-Type': 'text/csv; charset=utf-8',
                'Content-Disposition': 'attachment; filename="volunteers.csv"',
            }
            return build_response(200, csv_body, headers=headers)
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
            existing = Volunteer.list(org_id)
            existing_map = {}
            for item in existing:
                key = build_natural_key(item, ['email'])
                if key:
                    existing_map[key] = item
            created = updated = skipped = 0
            errors = []
            for index, row in enumerate(rows, start=2):
                row.pop('org_id', None)
                row.pop('volunteerId', None)
                key = build_natural_key(row, ['email'])
                if not key:
                    skipped += 1
                    errors.append({'row': index, 'error': 'Missing email'})
                    continue
                existing_item = existing_map.get(key)
                if existing_item:
                    updates = prune_empty_fields(row)
                    if not updates:
                        skipped += 1
                        continue
                    merged = {**existing_item, **updates}
                    merged.pop('org_id', None)
                    merged.pop('volunteerId', None)
                    Volunteer.update(org_id, existing_item['volunteerId'], merged)
                    updated += 1
                else:
                    created_item = Volunteer.create(org_id, row)
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
        if volunteer_id:
            return build_response(
                405,
                {'error': 'Method not allowed: use PUT to update volunteer'},
                headers=CORS_HEADERS
            )
        import uuid
        body = json.loads(event.get('body') or '{}')
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
        body = json.loads(event.get('body') or '{}')
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
