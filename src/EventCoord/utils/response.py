import json

def build_response(status_code: int, body, headers=None):
    return {
        'statusCode': status_code,
        'headers': headers or {},
        'body': json.dumps(body)
    }
