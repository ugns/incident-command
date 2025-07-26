import json
import base64
from typing import Any, Dict
import importlib
import glob
import os
from pathlib import Path
import traceback
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

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
    try:
        method = event.get('httpMethod', 'GET')
        path_params = event.get('pathParameters') or {}
        report_type = path_params.get('reportType')

        logger.info(f"Received event: {json.dumps(event)}")
        logger.info(f"Method: {method}, report_type: {report_type}")

        if method == 'GET' and not report_type:
            logger.info("Handling GET /reports endpoint (no report_type)")
            report_files = glob.glob(os.path.join(os.path.dirname(__file__), '*_form.py'))
            logger.info(f"Found report_files: {report_files}")
            supported_reports = []
            for file_path in report_files:
                logger.info(f"Processing file_path: {file_path}")
                stem = Path(file_path).stem
                logger.info(f"File stem: {stem}")
                if not stem.endswith('_form'):
                    logger.info(f"Skipping file (does not end with _form): {stem}")
                    continue
                rtype = stem[:-5]  # strip '_form'
                logger.info(f"Parsed report type: {rtype}")
                try:
                    module = importlib.import_module(f'{rtype}_form')
                    logger.info(f"Imported module: {rtype}_form")
                    media_type = getattr(module, 'MEDIA_TYPE', 'application/pdf')
                    logger.info(f"Media type for {rtype}: {media_type}")
                except Exception as e:
                    logger.error(f"Error importing module {rtype}_form: {e}\n{traceback.format_exc()}")
                    media_type = 'application/pdf'
                supported_reports.append({'type': rtype, 'media_type': media_type})
            logger.info(f"Final supported_reports: {supported_reports}")
            return {
                'statusCode': 200,
                'body': json.dumps({'reports': supported_reports}),
                'headers': {**cors_headers, 'Content-Type': 'application/json'},
            }

        if report_type:
            logger.info(f"Handling /reports/{report_type} endpoint")
            try:
                body = event.get('body', '{}')
                logger.info(f"Raw body: {body}")
                if event.get('isBase64Encoded'):
                    body = base64.b64decode(body).decode('utf-8')
                    logger.info(f"Decoded base64 body: {body}")
                data = json.loads(body)
                logger.info(f"Parsed JSON data: {data}")
            except Exception as e:
                logger.error(f"Error parsing request body: {e}\n{traceback.format_exc()}")
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'Invalid request body', 'details': str(e)}),
                    'headers': {
                        **cors_headers,
                        'Content-Type': 'application/json',
                    }
                }
            response = dynamic_report_handler(report_type, data)
            logger.info(f"Report handler response: {response}")
            if response.get('statusCode') == 200:
                headers = dict(response.get('headers', {}))
                headers['Content-Type'] = response.get('media_type', 'application/pdf')
                response['headers'] = headers
            return response

        logger.warning("No matching endpoint found for event.")
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'Not found'}),
            'headers': {
                **cors_headers,
                'Content-Type': 'application/json'
            }
        }
    except Exception as e:
        logger.error(f"Unhandled exception in lambda_handler: {e}\n{traceback.format_exc()}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error', 'details': str(e)}),
            'headers': {
                **cors_headers,
                'Content-Type': 'application/json'
            }
        }
