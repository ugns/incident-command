import json
import logging
import os
from aws_lambda_typing.events import APIGatewayProxyEventV2
from aws_lambda_typing.context import Context as LambdaContext
from aws_lambda_typing.responses import APIGatewayProxyResponseV2
from EventCoord.launchdarkly.flags import Flags
from EventCoord.models.activitylogs import ActivityLog
from EventCoord.utils.response import build_response
from aws_xray_sdk.core import patch_all, xray_recorder

patch_all()  # Automatically patches boto3, requests, etc.

xray_recorder.configure(service='incident-cmd')

# Setup logging
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s %(name)s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logging.getLogger().setLevel(LOG_LEVEL)

cors_headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS"
}


def lambda_handler(
    event: APIGatewayProxyEventV2,
    context: LambdaContext
) -> APIGatewayProxyResponseV2:
    claims = event.get('requestContext', {}).get('authorizer', {})
    if claims is None:
        claims = {}
    elif not isinstance(claims, dict):
        try:
            claims = dict(claims)
        except Exception:
            claims = {}
    flags = Flags(claims)
    org_id = claims.get('org_id')
    if not org_id:
        return build_response(
            403,
            {'error': 'Missing organization (org_id claim) in token'},
            headers=cors_headers
        )

    method = event.get('httpMethod', 'GET')
    path_params = event.get('pathParameters') or {}
    log_id = path_params.get('logId') if path_params else None
    volunteer_id = path_params.get('volunteerId') if path_params else None
    period_id = path_params.get('periodId') if path_params else None

    if method == 'GET':
        if log_id:
            item = ActivityLog.get(org_id, log_id)
            if not item or item.get('org_id') != org_id:
                return build_response(
                    404,
                    {'error': 'Activity log not found'},
                    headers=cors_headers
                )
            return build_response(200, item, headers=cors_headers)
        elif volunteer_id:
            items = ActivityLog.list_by_volunteer(org_id, volunteer_id)
            return build_response(200, items, headers=cors_headers)
        elif period_id:
            items = ActivityLog.list_by_period(org_id, period_id)
            return build_response(200, items, headers=cors_headers)
        else:
            items = ActivityLog.list(org_id)
            return build_response(200, items, headers=cors_headers)

    elif method == 'POST':
        import uuid
        from datetime import datetime, timezone
        body = json.loads(event.get('body', '{}'))
        if 'logId' not in body:
            body['logId'] = str(uuid.uuid4())
        if 'periodId' not in body or not body['periodId']:
            return build_response(
                400,
                {'error': 'Missing required field: periodId'},
                headers=cors_headers
            )
        if 'timestamp' not in body or not body['timestamp']:
            body['timestamp'] = datetime.now(
                timezone.utc).isoformat().replace('+00:00', 'Z')
        body['org_id'] = org_id
        ActivityLog.create(org_id, body)
        return build_response(
            201,
            {'message': 'Activity log created', 'id': body['logId']},
            headers=cors_headers
        )

    elif method == 'PUT':
        if not log_id:
            return build_response(
                400,
                {'error': 'Missing activity log id in path'},
                headers=cors_headers
            )
        from datetime import datetime, timezone
        body = json.loads(event.get('body', '{}'))
        body['logId'] = log_id
        if 'periodId' not in body or not body['periodId']:
            return build_response(
                400,
                {'error': 'Missing required field: periodId'},
                headers=cors_headers
            )
        if 'timestamp' not in body or not body['timestamp']:
            body['timestamp'] = datetime.now(
                timezone.utc).isoformat().replace('+00:00', 'Z')
        body['org_id'] = org_id
        ActivityLog.update(org_id, log_id, body)
        return build_response(
            200,
            {'message': 'Activity log updated', 'id': log_id},
            headers=cors_headers
        )

    elif method == 'DELETE':
        if not log_id:
            return build_response(
                400,
                {'error': 'Missing activity log id in path'},
                headers=cors_headers
            )
        if not flags.has_super_admin_access():
            return build_response(
                403,
                {'error': 'Admin privileges required for delete'},
                headers=cors_headers
            )
        ActivityLog.delete(org_id, log_id)
        return build_response(204, {}, headers=cors_headers)

    else:
        return build_response(405, {'error': 'Method not allowed'}, headers=cors_headers)
