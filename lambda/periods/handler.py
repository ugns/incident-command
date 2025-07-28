import json
import logging
from boto3.dynamodb.conditions import Key
from typing import Any, Dict
from shared.models.periods import Period
from shared.client.auth import check_auth
from shared.launchdarkly.flags import Flags

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

cors_headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS"
}


def build_response(status_code: int, body: Any) -> Dict[str, Any]:
    return {
        'statusCode': status_code,
        'headers': cors_headers,
        'body': json.dumps(body)
    }


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    claims = check_auth(event)
    org_id = claims.get('org_id')
    if not org_id:
        return build_response(403, {'error': 'Missing organization (org_id claim) in token'})

    method = event.get('httpMethod', 'GET')
    path_params = event.get('pathParameters') or {}
    period_id = path_params.get('periodId') if path_params else None

    if method == 'GET':
        if period_id:
            item = Period.get_period(period_id)
            if not item or item.get('org_id') != org_id:
                return build_response(404, {'error': 'Period not found'})
            return build_response(200, item)
        else:
            items = [item for item in Period.list_periods()
                     if item.get('org_id') == org_id]
            return build_response(200, items)

    elif method == 'POST':
        # Create a new ICS-214 period
        import uuid
        body = json.loads(event.get('body', '{}'))
        if 'periodId' not in body:
            body['periodId'] = str(uuid.uuid4())
        body['org_id'] = org_id
        Period.create_period(body)
        return build_response(201, {'message': 'Period created', 'id': body['periodId']})

    elif method == 'PUT':
        # Update an existing ICS-214 period
        if not period_id:
            return build_response(400, {'error': 'Missing period id in path'})
        body = json.loads(event.get('body', '{}'))
        body['periodId'] = period_id
        body['org_id'] = org_id
        Period.update_period(period_id, body)
        return build_response(200, {'message': 'Period updated', 'id': period_id})

    elif method == 'DELETE':
        # RBAC: Only allow admin users to delete
        if not period_id:
            return build_response(400, {'error': 'Missing period id in path'})
        if not Flags.has_admin_access(claims):
            return build_response(403, {'error': 'Admin privileges required for delete'})
        Period.delete_period(period_id)
        return build_response(204, {})

    else:
        return build_response(405, {'error': 'Method not allowed'})
