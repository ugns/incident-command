import json
import logging
from typing import Any, Dict
from organizations.model import Organization
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
    method = event.get('httpMethod', 'GET')
    path_params = event.get('pathParameters') or {}
    org_id = path_params.get('org_id') if path_params else None
    aud = path_params.get('aud') if path_params else None

    if method == 'GET':
        if org_id:
            org = Organization.get_by_org_id(org_id)
            if not org:
                return build_response(404, {'error': 'Organization not found'})
            return build_response(200, org)
        elif aud:
            org = Organization.get_by_aud(aud)
            if not org:
                return build_response(404, {'error': 'Organization not found'})
            return build_response(200, org)
        else:
            return build_response(400, {'error': 'Missing org_id or aud in path'})

    elif method == 'POST':
        body = json.loads(event.get('body', '{}'))
        aud = body.get('aud')
        name = body.get('name')
        if not aud or not name:
            return build_response(400, {'error': 'Missing aud or name in request body'})
        org = Organization.create(aud, name)
        return build_response(201, org)

    elif method == 'PUT':
        if not org_id:
            return build_response(400, {'error': 'Missing org_id in path'})
        body = json.loads(event.get('body', '{}'))
        updates = {k: v for k, v in body.items() if k in ('aud', 'name')}
        if not updates:
            return build_response(400, {'error': 'No valid fields to update'})
        org = Organization.update(org_id, updates)
        if not org:
            return build_response(404, {'error': 'Organization not found'})
        return build_response(200, org)

    elif method == 'DELETE':
        if not org_id:
            return build_response(400, {'error': 'Missing org_id in path'})
        if not Flags.has_admin_access(claims):
          return build_response(403, {'error': 'Admin privileges required for delete'})        
        Organization.delete(org_id)
        return build_response(204, {})

    else:
        return build_response(405, {'error': 'Method not allowed'})
