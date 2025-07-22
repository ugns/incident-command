import json
import os
import boto3
from boto3.dynamodb.conditions import Key
from client.auth import check_auth
from typing import Any, Dict
from pypdf import PdfReader, PdfWriter
import base64
import io

dynamodb = boto3.resource('dynamodb')
table: Any = dynamodb.Table(os.environ.get('ICS214_PERIODS_TABLE', 'ics214_periods'))  # type: ignore
cors_headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS"
}

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    claims = check_auth(event)
    method = event.get('httpMethod', 'GET')
    path_params = event.get('pathParameters') or {}
    period_id = path_params.get('periodId') if path_params else None

    if method == 'GET':
        if period_id:
            # Get ICS-214 period metadata
            resp = table.get_item(Key={'org_id': claims.get('hd'), 'periodId': period_id})
            period = resp.get('Item')
            if not period:
                return {
                    'statusCode': 404,
                    'headers': cors_headers,
                    'body': json.dumps({'error': 'ICS-214 period not found'})
                }

            # Fetch activity logs for this period (assume activity_logs table, same org_id, periodId)
            activitylogs_table: Any = dynamodb.Table(os.environ.get('ACTIVITY_LOGS_TABLE', 'activity_logs'))  # type: ignore
            logs_resp = activitylogs_table.query(
                IndexName='PeriodIdIndex',
                KeyConditionExpression=Key('org_id').eq(claims.get('hd')) & Key('periodId').eq(period_id)
            )
            activity_logs = logs_resp.get('Items', [])


            # Merge period metadata and activity logs for PDF
            merged = dict(period)
            merged['activity_logs'] = activity_logs
            # Add prepared_by_name from claims if available
            if claims.get('name'):
                merged['prepared_by_name'] = claims['name']

            # If query param ?pdf=1, return PDF
            query = event.get('queryStringParameters') or {}
            if query.get('pdf') == '1':
                pdf_bytes = generate_ics214_pdf(merged)
                filename = f"ICS214-{period_id}.pdf" if period_id else "ICS214.pdf"
                pdf_headers = {
                    'Content-Type': 'application/pdf',
                    'Content-Disposition': f'attachment; filename="{filename}"'
                }
                # Merge CORS headers
                merged_headers = dict(cors_headers)
                merged_headers.update(pdf_headers)
                return {
                    'statusCode': 200,
                    'headers': merged_headers,
                    'body': base64.b64encode(pdf_bytes).decode('utf-8'),
                    'isBase64Encoded': True
                }
            return {
                'statusCode': 200,
                'headers': cors_headers,
                'body': json.dumps(merged)
                }
        else:
            # List all ICS-214 periods
            resp = table.query(KeyConditionExpression=Key('org_id').eq(claims.get('hd')))
            return {
                'statusCode': 200,
                'headers': cors_headers,
                'body': json.dumps(resp.get('Items', []))
            }

    elif method == 'POST':
        # Create a new ICS-214 period
        import uuid
        from datetime import datetime, timezone
        body = json.loads(event.get('body', '{}'))
        if 'periodId' not in body:
            body['periodId'] = str(uuid.uuid4())
        if 'startTime' not in body or not body['startTime']:
            # Set startTime in UTC ISO 8601 format with 'Z' suffix
            body['startTime'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        body['org_id'] = claims.get('hd')
        table.put_item(Item=body)
        return {
            'statusCode': 201,
            'headers': cors_headers,
            'body': json.dumps({'message': 'ICS-214 period created', 'id': body['periodId']})
        }

    elif method == 'PUT':
        # Update an existing ICS-214 period
        if not period_id:
            return {
                'statusCode': 400,
                'headers': cors_headers,
                'body': json.dumps({'error': 'Missing ICS-214 period id in path'})
            }
        from datetime import datetime
        body = json.loads(event.get('body', '{}'))
        body['periodId'] = period_id
        if 'startTime' not in body or not body['startTime']:
            body['startTime'] = datetime.now().isoformat()
        body['org_id'] = claims.get('hd')
        table.put_item(Item=body)
        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps({'message': 'ICS-214 period updated', 'id': period_id})
        }

    elif method == 'DELETE':
        # RBAC: Only allow admin users to delete
        if not period_id:
            return {
                'statusCode': 400,
                'headers': cors_headers,
                'body': json.dumps({'error': 'Missing ICS-214 period id in path'})
            }
        if not claims.get('is_admin'):
            return {
                'statusCode': 403,
                'headers': cors_headers,
                'body': json.dumps({'error': 'Admin privileges required for delete'})
            }
        table.delete_item(Key={'org_id': claims.get('hd'), 'periodId': period_id})
        return {
            'statusCode': 204,
            'headers': cors_headers,
            'body': ''
        }

    else:
        return {
            'statusCode': 405,
            'headers': cors_headers,
            'body': json.dumps({'error': 'Method not allowed'})
        }


def generate_ics214_pdf(item: Dict[str, Any]) -> bytes:
    """
    Fill the ICS-214 PDF template (ics214-v3.1.pdf) with period data.
    Assumes the template is in the same directory as this script.
    """
    template_path = os.path.join(os.path.dirname(__file__), "ics214-v3.1.pdf")
    reader = PdfReader(template_path)
    writer = PdfWriter()
    # Add page 1 and page 2 from template
    writer.add_page(reader.pages[0])
    writer.add_page(reader.pages[1])
    # Always add page 3 (instructions) at the end
    instruction_page = reader.pages[2]


    # Inject current date and time for PDF generation
    from datetime import datetime
    now = datetime.now()
    item = dict(item)  # Copy to avoid mutating original
    item['generated_datetime'] = now.strftime('%Y-%m-%d %H:%M:%S')

    # Map period fields: data key -> list of PDF field names
    field_map = {
        "name": ["1 Incident Name_19", "1 Incident Name_20"],
        "prepared_by_name": ["8 Prepared by Name", "8 Prepared by Name_2"],
        "generated_datetime": ["DateTime_15", "DateTime_16"],
        # Add more mappings as needed
    }

    # Prepare data for static fields
    data = {}
    # Handle startTime and endTime for date/time split fields
    start_time = item.get('startTime')
    end_time = item.get('endTime')
    if start_time:
        try:
            date_part, time_part = start_time.split('T')
            data['Date From'] = date_part
            data['Time From'] = time_part.rstrip('Z')
        except Exception:
            data['Date From'] = start_time
            data['Time From'] = ''
    if end_time:
        try:
            date_part, time_part = end_time.split('T')
            data['Date To'] = date_part
            data['Time To'] = time_part.rstrip('Z')
        except Exception:
            data['Date To'] = end_time
            data['Time To'] = ''

    # Fill all mapped PDF fields for each data key
    for k, pdf_fields in field_map.items():
        if k in item:
            for pdf_field in pdf_fields:
                if pdf_field not in data:
                    data[pdf_field] = str(item[k])

    activity_logs = item.get('activity_logs', [])
    total_logs = len(activity_logs)

    # Fill page 1 (first 24 logs)
    for idx in range(min(24, total_logs)):
        log = activity_logs[idx]
        dt_field = f"DateTimeRow{idx+1}"
        act_field = f"Notable ActivitiesRow{idx+1}"
        dt_val = log.get('timestamp', '')
        act_val = log.get('details', log.get('action', ''))
        writer.update_page_form_field_values(
            writer.pages[0],
            {dt_field: dt_val, act_field: act_val}
        )

    # Fill page 2 (next 36 logs)
    for idx in range(24, min(60, total_logs)):
        log = activity_logs[idx]
        row = (idx - 24) + 1
        dt_field = f"DateTimeRow{row}_2"
        act_field = f"Notable ActivitiesRow{row}_2"
        dt_val = log.get('timestamp', '')
        act_val = log.get('details', log.get('action', ''))
        writer.update_page_form_field_values(
            writer.pages[1],
            {dt_field: dt_val, act_field: act_val}
        )

    # For logs beyond 60, duplicate page 2 as needed
    extra_logs = activity_logs[60:]
    for i in range(0, len(extra_logs), 36):
        # Add a new copy of page 2 for each batch of 36 logs
        writer.add_page(reader.pages[1])
        page_idx = len(writer.pages) - 1
        for j, log in enumerate(extra_logs[i:i+36]):
            row = j + 1
            dt_field = f"DateTimeRow{row}_2"
            act_field = f"Notable ActivitiesRow{row}_2"
            dt_val = log.get('timestamp', '')
            act_val = log.get('details', log.get('action', ''))
            writer.update_page_form_field_values(
                writer.pages[page_idx],
                {dt_field: dt_val, act_field: act_val}
            )


    # Fill period fields on every page except the last (instructions) page
    for i in range(len(writer.pages) - 1):
        writer.update_page_form_field_values(writer.pages[i], data)

    # Add instructions page at the end
    writer.add_page(instruction_page)

    output = io.BytesIO()
    writer.write(output)
    output.seek(0)
    return output.read()
