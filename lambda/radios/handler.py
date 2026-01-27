import base64
import json
from EventCoord.utils.types import APIGatewayProxyEvent
from aws_lambda_typing.context import Context as LambdaContext
from EventCoord.utils.types import APIGatewayProxyResponse
from EventCoord.launchdarkly.flags import Flags
from EventCoord.models.radios import Radio
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
    resource_path = event.get('resource', '') or event.get('path', '')

    if method == 'GET':
        if resource_path.endswith('/export'):
            items = Radio.list(org_id)
            csv_body = items_to_csv(items, exclude_fields={'org_id', 'radioId'})
            headers = {
                **CORS_HEADERS,
                'Content-Type': 'text/csv; charset=utf-8',
                'Content-Disposition': 'attachment; filename="radios.csv"',
            }
            return build_response(200, csv_body, headers=headers)
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
            existing = Radio.list(org_id)
            existing_map = {}
            for item in existing:
                key = build_natural_key(item, ['serialNumber'])
                if key:
                    existing_map[key] = item
            created = updated = skipped = 0
            errors = []
            for index, row in enumerate(rows, start=2):
                row.pop('org_id', None)
                row.pop('radioId', None)
                key = build_natural_key(row, ['serialNumber'])
                if not key:
                    skipped += 1
                    errors.append({'row': index, 'error': 'Missing serialNumber'})
                    continue
                existing_item = existing_map.get(key)
                if existing_item:
                    updates = prune_empty_fields(row)
                    if not updates:
                        skipped += 1
                        continue
                    merged = {**existing_item, **updates}
                    merged.pop('org_id', None)
                    merged.pop('radioId', None)
                    Radio.update(org_id, existing_item['radioId'], merged)
                    updated += 1
                else:
                    created_item = Radio.create(org_id, row)
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
