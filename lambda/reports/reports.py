import json
import base64
from typing import Any, Dict
import importlib
import glob
import os
from pathlib import Path

cors_headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "GET,POST,OPTIONS"
}


# Dynamically load and call the reportType's generate_report()
def dynamic_report_handler(report_type, data):
    module_name = f"{report_type}_form"
    try:
        module = importlib.import_module(module_name)
    except Exception as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': f'Could not import module {module_name}', 'details': str(e)}),
            'headers': {**cors_headers, 'Content-Type': 'application/json'},
        }
    # Get media type
    media_type = getattr(module, 'MEDIA_TYPE', 'application/pdf')
    # Call generate_report
    try:
        result = module.generate_report(data)
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Failed to generate report', 'details': str(e)}),
            'headers': {**cors_headers, 'Content-Type': 'application/json'},
        }
    # Expect result to be bytes (PDF or other binary)
    return {
        'statusCode': 200,
        'body': base64.b64encode(result).decode('utf-8'),
        'isBase64Encoded': True,
        'headers': {
            **cors_headers,
            'Content-Disposition': f'attachment; filename="{report_type}.pdf"',
        },
    }


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    method = event.get('httpMethod', 'GET')
    path_params = event.get('pathParameters') or {}
    report_type = path_params.get('reportType')

    if method == 'GET' and not report_type:
        # Discover available *_form.py files
        report_files = glob.glob(os.path.join(os.path.dirname(__file__), '*_form.py'))
        supported_reports = []
        for file_path in report_files:
            stem = Path(file_path).stem
            if not stem.endswith('_form'):
                continue
            rtype = stem[:-5]  # strip '_form'
            try:
                module = importlib.import_module(f'{rtype}_form')
                media_type = getattr(module, 'MEDIA_TYPE', 'application/pdf')
            except Exception:
                media_type = 'application/pdf'
            supported_reports.append({'type': rtype, 'media_type': media_type})
        return {
            'statusCode': 200,
            'body': json.dumps({'reports': supported_reports}),
            'headers': {**cors_headers, 'Content-Type': 'application/json'},
        }

    if report_type:
        try:
            body = event.get('body', '{}')
            if event.get('isBase64Encoded'):
                body = base64.b64decode(body).decode('utf-8')
            data = json.loads(body)
        except Exception as e:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid request body', 'details': str(e)}),
                'headers': {
                    **cors_headers,
                    'Content-Type': 'application/json',
                }
            }
        response = dynamic_report_handler(report_type, data)
        if response.get('statusCode') == 200:
            headers = dict(response.get('headers', {}))
            headers['Content-Type'] = response.get('media_type', 'application/pdf')
            response['headers'] = headers
        return response

    return {
        'statusCode': 404,
        'body': json.dumps({'error': 'Not found'}),
        'headers': {
            **cors_headers,
            'Content-Type': 'application/json'
        }
    }
