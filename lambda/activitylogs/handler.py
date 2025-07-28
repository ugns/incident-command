import json
from boto3.dynamodb.conditions import Key
from typing import Any, Dict
from client.auth import check_auth
from launchdarkly.flags import Flags
from models.activitylogs import ActivityLog

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
    log_id = path_params.get('logId') if path_params else None
    volunteer_id = path_params.get('volunteerId') if path_params else None

    if method == 'GET':
        if log_id:
            item = ActivityLog.get_activity_log(log_id)
            if not item or item.get('org_id') != org_id:
                return build_response(404, {'error': 'Activity log not found'})
            return build_response(200, item)
        # volunteer_id query is not implemented in model.py, keep direct query for now
        elif volunteer_id:
            # TODO: Move this query to model.py if needed
            from .model import table
            resp = table.query(
                IndexName='VolunteerIdIndex',
                KeyConditionExpression=Key('org_id').eq(
                    org_id) & Key('volunteerId').eq(volunteer_id)
            )
            return build_response(200, resp.get('Items', []))
        else:
            # List all logs for org
            items = [item for item in ActivityLog.list_activity_logs(
            ) if item.get('org_id') == org_id]
            return build_response(200, items)

    elif method == 'POST':
        import uuid
        from datetime import datetime, timezone
        body = json.loads(event.get('body', '{}'))
        if 'logId' not in body:
            body['logId'] = str(uuid.uuid4())
        if 'periodId' not in body or not body['periodId']:
            return build_response(400, {'error': 'Missing required field: periodId'})
        if 'timestamp' not in body or not body['timestamp']:
            body['timestamp'] = datetime.now(
                timezone.utc).isoformat().replace('+00:00', 'Z')
        body['org_id'] = org_id
        ActivityLog.create_activity_log(body)
        return build_response(201, {'message': 'Activity log created', 'id': body['logId']})

    elif method == 'PUT':
        if not log_id:
            return build_response(400, {'error': 'Missing activity log id in path'})
        from datetime import datetime, timezone
        body = json.loads(event.get('body', '{}'))
        body['logId'] = log_id
        if 'periodId' not in body or not body['periodId']:
            return build_response(400, {'error': 'Missing required field: periodId'})
        if 'timestamp' not in body or not body['timestamp']:
            body['timestamp'] = datetime.now(
                timezone.utc).isoformat().replace('+00:00', 'Z')
        body['org_id'] = org_id
        ActivityLog.update_activity_log(log_id, body)
        return build_response(200, {'message': 'Activity log updated', 'id': log_id})

    elif method == 'DELETE':
        if not log_id:
            return build_response(400, {'error': 'Missing activity log id in path'})
        if not Flags.has_admin_access(claims):
            return build_response(403, {'error': 'Admin privileges required for delete'})
        ActivityLog.delete_activity_log(log_id)
        return build_response(204, {})

    else:
        return build_response(405, {'error': 'Method not allowed'})
