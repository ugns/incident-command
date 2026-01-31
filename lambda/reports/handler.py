import json
import os
import base64
import importlib
import glob
import traceback
from pathlib import Path
from typing import Any
from EventCoord.utils.types import APIGatewayProxyEvent
from aws_lambda_typing.context import Context as LambdaContext
from EventCoord.utils.types import APIGatewayProxyResponse
from EventCoord.utils.response import build_response
from EventCoord.utils.handler import get_claims, get_logger, init_tracing
from EventCoord.utils.csv_import import parse_csv_rows

init_tracing()
logger = get_logger(__name__)

cors_headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
    "Access-Control-Expose-Headers": "Content-Disposition",
}


# Dynamically load and call the reportType's generate_report()
def dynamic_report_handler(
    report_type: str,
    data: dict[str, Any]
) -> APIGatewayProxyResponse:
    module_name = f"{report_type}_form"
    try:
        module = importlib.import_module(module_name)
    except Exception as e:
        return build_response(
            400,
            {'error': f'Could not import module {module_name}',
                'details': str(e)},
            headers=cors_headers
        )
    # Get media type
    media_type = getattr(module, 'MEDIA_TYPE', 'application/pdf')
    # Call generate_report
    try:
        result = module.generate_report(data)
    except Exception as e:
        return build_response(
            500,
            {'error': 'Failed to generate report', 'details': str(e)},
            headers=cors_headers
        )
    # Generate a short hash from the data for filename uniqueness
    import hashlib
    import mimetypes
    from pathlib import Path
    data_bytes = json.dumps(data, sort_keys=True).encode('utf-8')
    short_hash = hashlib.sha256(data_bytes).hexdigest()[:8]
    ext = mimetypes.guess_extension(media_type) or ''
    # Use pathlib to format filename and extension
    base_name = f"{report_type}-{short_hash}"
    filename = str(Path(base_name).with_suffix(ext)) if ext else base_name
    return build_response(
        200,
        base64.b64encode(result).decode('utf-8'),
        headers={
            **cors_headers,
            'Content-Disposition': f'attachment; filename="{filename}"',
            'Content-Type': media_type,
        },
        is_base64_encoded=True,
    )


def lambda_handler(
    event: APIGatewayProxyEvent,
    context: LambdaContext
) -> APIGatewayProxyResponse:
    logger.debug(f"Reports event: {event}")
    logger.debug(f"Reports context: {context}")
    claims = get_claims(event)
    org_id = claims.get('org_id')
    if not org_id:
        return build_response(
            403,
            {'error': 'Missing organization (org_id claim) in token'},
            headers=cors_headers
        )

    try:
        method = event.get('httpMethod', 'GET')
        path_params = event.get('pathParameters') or {}
        report_type = path_params.get('reportType')

        logger.info(f"Received event: {json.dumps(event)}")
        logger.info(f"Method: {method}, report_type: {report_type}")

        if method == 'GET' and not report_type:
            logger.info("Handling GET /reports endpoint (no report_type)")
            report_files = glob.glob(os.path.join(
                os.path.dirname(__file__), '*_form.py'))
            logger.info(f"Found report_files: {report_files}")
            supported_reports = []
            for file_path in report_files:
                logger.info(f"Processing file_path: {file_path}")
                stem = Path(file_path).stem
                logger.info(f"File stem: {stem}")
                if not stem.endswith('_form'):
                    logger.info(
                        f"Skipping file (does not end with _form): {stem}")
                    continue
                rtype = stem[:-5]  # strip '_form'
                logger.info(f"Parsed report type: {rtype}")
                # Log directory contents before import
                current_dir = os.path.dirname(__file__)
                try:
                    dir_listing = os.listdir(current_dir)
                    logger.info(
                        f"Directory listing for {current_dir}: {dir_listing}")
                except Exception as e:
                    logger.error(f"Error listing directory {current_dir}: {e}")
                logger.info(f"Attempting to import module: {rtype}_form")
                try:
                    module = importlib.import_module(f'{rtype}_form')
                    logger.info(f"Imported module: {rtype}_form")
                    media_type = getattr(
                        module, 'MEDIA_TYPE', 'application/pdf')
                    media_title = getattr(
                        module, 'TITLE', rtype.capitalize() + ' Report')
                    logger.info(f"Media type for {rtype}: {media_type}")
                except Exception as e:
                    logger.error(
                        f"Error importing module {rtype}_form: {e}\n{traceback.format_exc()}")
                    media_type = 'application/pdf'
                    media_title = rtype.capitalize() + ' Report'
                supported_reports.append(
                    {'type': rtype, 'mediaType': media_type, 'title': media_title})
            logger.info(f"Final supported_reports: {supported_reports}")
            return build_response(200, {'reports': supported_reports}, headers=cors_headers)

        if report_type:
            logger.info(f"Handling /reports/{report_type} endpoint")
            try:
                body = event.get('body') or ''
                logger.info(f"Raw body: {body}")
                if event.get('isBase64Encoded') and body:
                    body = base64.b64decode(body).decode('utf-8')
                    logger.info(f"Decoded base64 body: {body}")
                if report_type == 'pkey':
                    if not body:
                        return build_response(400, {
                            'error': 'Missing CSV body'
                        }, headers=cors_headers)
                    rows = parse_csv_rows(body)
                    if not rows:
                        return build_response(400, {
                            'error': 'No CSV rows found'
                        }, headers=cors_headers)
                    data = {'rows': rows}
                    logger.info(f"Parsed CSV rows: {len(rows)}")
                else:
                    data = json.loads(body or '{}')
                    logger.info(f"Parsed JSON data: {data}")
            except Exception as e:
                logger.error(
                    f"Error parsing request body: {e}\n{traceback.format_exc()}")
                return build_response(400, {
                    'error': 'Invalid request body',
                    'details': str(e)
                }, headers=cors_headers)

            response = dynamic_report_handler(report_type, data)
            logger.info(f"Report handler response: {response}")
            return response

        logger.warning("No matching endpoint found for event.")
        return build_response(404, {'error': 'Not found'}, headers=cors_headers)
    except Exception as e:
        logger.error(
            f"Unhandled exception in lambda_handler: {e}\n{traceback.format_exc()}")
        return build_response(
            500,
            {'error': 'Internal server error', 'details': str(e)},
            headers=cors_headers
        )
