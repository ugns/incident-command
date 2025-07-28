import json
import logging
from typing import Any, Dict
from shared.models.volunteers import Volunteer
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
    volunteer_id = path_params.get('volunteerId') if path_params else None
    resource_path = event.get('resource', '') or event.get('path', '')

    if method == 'GET':
        if volunteer_id:
            item = Volunteer.get(org_id, volunteer_id)
            if not item:
                return build_response(404, {'error': 'Volunteer not found'})
            return build_response(200, item)
        else:
            items = Volunteer.list(org_id)
            return build_response(200, items)

    elif method == 'POST':
        if volunteer_id:
            return build_response(405, {'error': 'Method not allowed: use PUT to update volunteer'})
        import uuid
        body = json.loads(event.get('body', '{}'))
        item = Volunteer.create(org_id, body)
        return build_response(201, {'message': 'Volunteer created', 'id': item['volunteerId']})

    elif method == 'PUT':
        if not volunteer_id:
            return build_response(400, {'error': 'Missing volunteer id in path'})
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
        return build_response(200, {'message': 'Volunteer updated', 'id': volunteer_id})

    elif method == 'DELETE':
        if not volunteer_id:
            return build_response(400, {'error': 'Missing volunteer id in path'})
        if not Flags.has_admin_access(claims):
            return build_response(403, {'error': 'Admin privileges required for delete'})
        Volunteer.delete(org_id, volunteer_id)
        return build_response(204, {})

    else:
        return build_response(405, {'error': 'Method not allowed'})
