import os
import logging
import boto3
from authlib.jose import JsonWebKey
from EventCoord.utils.response import build_response
from aws_xray_sdk.core import patch_all, xray_recorder

patch_all()  # Automatically patches boto3, requests, etc.

xray_recorder.configure(service='incident-cmd')

# Use RSA public key from AWS Secrets Manager
PUBLIC_KEY_SECRET_ARN = os.environ.get('JWT_PUBLIC_KEY_SECRET_ARN')
cors_headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "GET,OPTIONS"
}

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_public_keys():
    if not PUBLIC_KEY_SECRET_ARN:
        raise Exception("JWT_PUBLIC_KEY_SECRET_ARN not set")
    client = boto3.client('secretsmanager')
    # Get all version IDs for the secret
    versions = client.list_secret_version_ids(
        SecretId=PUBLIC_KEY_SECRET_ARN)['Versions']
    # Sort by CreatedDate descending (latest first)
    versions_sorted = sorted(
        versions, key=lambda v: v['CreatedDate'], reverse=True)
    # Get up to 2 most recent versions
    keys = []
    for v in versions_sorted[:2]:
        version_id = v['VersionId']
        resp = client.get_secret_value(
            SecretId=PUBLIC_KEY_SECRET_ARN, VersionId=version_id)
        keys.append(resp['SecretString'])
    return keys


def lambda_handler(event, context):
    try:
        public_keys_pem = get_public_keys()
        jwks_keys = []
        for key_pem in public_keys_pem:
            jwk = JsonWebKey.import_key(key_pem, {'kty': 'RSA'})
            jwks_keys.append(jwk.as_dict())
        jwks = {"keys": jwks_keys}
        logger.info(
            f"JWKS published with {len(jwks_keys)} keys, kids: {[k.get('kid') for k in jwks_keys]}")
        return build_response(200, jwks, headers=cors_headers)
    except Exception as e:
        logger.error(f"Failed to publish JWKS: {e}", exc_info=True)
        return build_response(
            500,
            {"error": "Failed to publish JWKS", "details": str(e)},
            headers=cors_headers
        )
