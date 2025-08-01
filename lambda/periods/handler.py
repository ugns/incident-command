import os
import uuid
import json
import logging
from boto3.dynamodb.conditions import Key
from typing import Any, Dict
from client.auth import check_auth
from launchdarkly.flags import Flags
from models.periods import Period
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
    org_id = claims.get('org_id')
    if not org_id:
        return {
            'statusCode': 403,
            'headers': cors_headers,
            'body': json.dumps({'error': 'Missing organization (org_id claim) in token'}, headers=cors_headers)
        }

    method = event.get('httpMethod', 'GET')
    path_params = event.get('pathParameters') or {}
    period_id = path_params.get('periodId') if path_params else None

    if method == 'GET':
        if period_id:
            item = Period.get_period(period_id)
            if not item or item.get('org_id') != org_id:
                return build_response(404, {'error': 'Period not found'}, headers=cors_headers)
            return build_response(200, item, headers=cors_headers)
        else:
            items = Period.list(org_id)
            return build_response(200, items, headers=cors_headers)

    elif method == 'POST':
        # Create a new ICS-214 period
        import uuid
        body = json.loads(event.get('body', '{}'))
        if 'periodId' not in body:
            body['periodId'] = str(uuid.uuid4())
        if 'incidentId' not in body:
            return build_response(400, {'error': 'Missing incidentId in request body'}, headers=cors_headers)
        incident_id = body['incidentId']
        body['org_id'] = org_id
        Period.create(org_id, incident_id, body)
        return build_response(201, {'message': 'Period created', 'id': body['periodId']}, headers=cors_headers)

    elif method == 'PUT':
        # Update an existing ICS-214 period
        if not period_id:
            return build_response(400, {'error': 'Missing period id in path'}, headers=cors_headers)
        body = json.loads(event.get('body', '{}'))
        Period.update(org_id, period_id, body)
        return build_response(200, {'message': 'Period updated', 'id': period_id}, headers=cors_headers)

    elif method == 'DELETE':
        if not period_id:
            return build_response(400, {'error': 'Missing period id in path'}, headers=cors_headers)
        Period.delete(org_id, period_id)
        return build_response(204, {}, headers=cors_headers)

    else:
        return build_response(405, {'error': 'Method not allowed'}, headers=cors_headers)
