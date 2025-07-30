
import json
from typing import Any, Dict
from client.auth import check_auth
from models.locations import Location
from utils.response import build_response

cors_headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS"
}

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    claims = check_auth(event)
    org_id = claims.get('org_id')
    if not org_id:
        return build_response(403, {'error': 'Missing organization (org_id claim) in token'}, headers=cors_headers)

    method = event.get('httpMethod', 'GET')
    path_params = event.get('pathParameters') or {}
    location_id = path_params.get('locationId') if path_params else None

    if method == 'GET':
        if location_id:
            item = Location.get(org_id, location_id)
            if not item:
                return build_response(404, {'error': 'Location not found'}, headers=cors_headers)
            return build_response(200, item, headers=cors_headers)
        else:
            items = Location.list(org_id)
            return build_response(200, items, headers=cors_headers)

    elif method == 'POST':
        import uuid
        body = json.loads(event.get('body', '{}'))
        if 'locationId' not in body:
            body['locationId'] = str(uuid.uuid4())
        body['org_id'] = org_id
        Location.create(org_id, body)
        return build_response(201, {'message': 'Location created', 'id': body['locationId']}, headers=cors_headers)

    elif method == 'PUT':
        if not location_id:
            return build_response(400, {'error': 'Missing location id in path'}, headers=cors_headers)
        body = json.loads(event.get('body', '{}'))
        Location.update(org_id, location_id, body)
        return build_response(200, {'message': 'Location updated', 'id': location_id}, headers=cors_headers)

    elif method == 'DELETE':
        if not location_id:
            return build_response(400, {'error': 'Missing location id in path'}, headers=cors_headers)
        Location.delete(org_id, location_id)
        return build_response(204, {}, headers=cors_headers)

    else:
        return build_response(405, {'error': 'Method not allowed'}, headers=cors_headers)
