import json

def lambda_handler(event, context):
    # Handles client messages (e.g., subscribe/unsubscribe)
    body = event.get('body')
    try:
        message = json.loads(body) if body else {}
    except Exception:
        message = {}
    action = message.get('action')
    # Example: handle ping
    if action == 'ping':
        return {"statusCode": 200, "body": json.dumps({"type": "pong"})}
    # Extend with more actions as needed
    return {"statusCode": 200, "body": json.dumps({"type": "ack"})}
