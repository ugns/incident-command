cors_headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS"
}

import json
import base64
import os
from io import BytesIO
from pdf_form import generate_ics214_report

def load_fields_json(env_var, default_path):
    path = os.environ.get(env_var, default_path)
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except Exception as e:
        raise RuntimeError(f"Failed to load fields JSON from {path}: {e}")

def handle_ics214_report(data):
    input_pdf_path = os.environ.get('ICS214_TEMPLATE_PDF', 'ics214_template.pdf')
    try:
        fields_json = load_fields_json('ICS214_FIELDS_JSON', 'fields.json')
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Failed to load fields.json', 'details': str(e)}),
            'headers': {**cors_headers, 'Content-Type': 'application/json'}
        }
    # Validate required fields in the report
    if not input_pdf_path or not isinstance(data, dict) or 'period' not in data or 'activityLogs' not in data or 'preparedBy' not in data:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing required fields in report'}),
            'headers': {**cors_headers, 'Content-Type': 'application/json'}
        }
    try:
        buffer = BytesIO()
        generate_ics214_report(
            input_pdf_path=input_pdf_path,
            output_pdf=buffer,
            fields_json=fields_json,
            report=data
        )
        buffer.seek(0)
        pdf_bytes = buffer.read()
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Failed to generate report', 'details': str(e)}),
            'headers': {**cors_headers, 'Content-Type': 'application/json'}
        }
    return {
        'statusCode': 200,
        'body': base64.b64encode(pdf_bytes).decode('utf-8'),
        'isBase64Encoded': True,
        'headers': {**cors_headers, 'Content-Type': 'application/pdf', 'Content-Disposition': 'attachment; filename="ics214.pdf"'}
    }

REPORT_HANDLERS = {
    'ics214': handle_ics214_report,
    # Add new report types here
}

def lambda_handler(event, context):
    method = event.get('httpMethod', 'GET')
    path_params = event.get('pathParameters', {})
    report_type = path_params.get('reportType')

    if method == 'GET' and not report_type:
        # GET /reports: return supported report types
        supported_reports = list(REPORT_HANDLERS.keys())
        return {
            'statusCode': 200,
            'body': json.dumps({'reports': supported_reports}),
            'headers': {**cors_headers, 'Content-Type': 'application/json'}
        }

    if report_type:
        handler = REPORT_HANDLERS.get(report_type)
        if not handler:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Unsupported reportType'}),
                'headers': {**cors_headers, 'Content-Type': 'application/json'}
            }
        try:
            body = event.get('body')
            if event.get('isBase64Encoded'):
                body = base64.b64decode(body).decode('utf-8')
            data = json.loads(body)
        except Exception as e:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid request body', 'details': str(e)}),
                'headers': {**cors_headers, 'Content-Type': 'application/json'}
            }
        return handler(data)

    return {
        'statusCode': 404,
        'body': json.dumps({'error': 'Not found'}),
        'headers': {**cors_headers, 'Content-Type': 'application/json'}
    }
