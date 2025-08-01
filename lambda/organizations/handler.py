import os
import uuid
import boto3
import json
import logging
from typing import Any, Dict
from client.auth import check_auth
from launchdarkly.flags import Flags
from models.organizations import Organization
from utils.response import build_response

# Setup logging
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger(__name__)

cors_headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS"
}


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    claims = check_auth(event)
    flags = Flags(claims)
    method = event.get('httpMethod', 'GET')
    path_params = event.get('pathParameters') or {}
    org_id = path_params.get('org_id') if path_params else None
    aud = path_params.get('aud') if path_params else None

    if method == 'GET':
        if org_id:
            org = Organization.get_by_org_id(org_id)
            if not org:
                return build_response(404, {'error': 'Organization not found'}, headers=cors_headers)
            return build_response(200, org, headers=cors_headers)
        elif aud:
            org = Organization.get_by_aud(aud)
            if not org:
                return build_response(404, {'error': 'Organization not found'}, headers=cors_headers)
            return build_response(200, org, headers=cors_headers)
        else:
            items = Organization.list_all()
            return build_response(200, items, headers=cors_headers)

    elif method == 'POST':
        body = json.loads(event.get('body', '{}'))
        if not flags.has_super_admin_access():
            return build_response(403, {'error': 'Super Admin privileges required for create'}, headers=cors_headers)

        aud = body.get('aud')
        name = body.get('name')
        if not aud or not name:
            return build_response(400, {'error': 'Missing aud or name in request body'}, headers=cors_headers)
        org = Organization.create(aud, name)
        return build_response(201, org, headers=cors_headers)

    elif method == 'PUT':
        if not org_id:
            return build_response(400, {'error': 'Missing org_id in path'}, headers=cors_headers)
        if not flags.has_super_admin_access():
            return build_response(403, {'error': 'Super Admin privileges required for update'}, headers=cors_headers)
        body = json.loads(event.get('body', '{}'))
        updates = {k: v for k, v in body.items() if k in ('aud', 'name', 'hd', 'notes')}
        if not updates:
            return build_response(400, {'error': 'No valid fields to update'}, headers=cors_headers)
        org = Organization.update(org_id, updates)
        if not org:
            return build_response(404, {'error': 'Organization not found'}, headers=cors_headers)
        return build_response(200, org, headers=cors_headers)

    elif method == 'DELETE':
        if not org_id:
            return build_response(400, {'error': 'Missing org_id in path'}, headers=cors_headers)
        if not flags.has_super_admin_access():
            return build_response(403, {'error': 'Super Admin privileges required for delete'}, headers=cors_headers)
        Organization.delete(org_id)
        return build_response(204, {}, headers=cors_headers)

    else:
        return build_response(405, {'error': 'Method not allowed'}, headers=cors_headers)
