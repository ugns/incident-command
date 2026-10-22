import logging
import os
from typing import Any, Dict

import boto3

from EventCoord.auth.provider import AuthResult

logger = logging.getLogger(__name__)

_dynamodb = boto3.resource("dynamodb")


class ApiKeyAuthProvider:
    """
    Static API-key authentication for service-to-service integrations.

    The caller passes an opaque key as the ``token`` field in the login request
    body (with ``"provider": "api_key"``).  The key is looked up in a DynamoDB
    table and, if found and active, user claims are returned.

    This provider is intended for automated systems (scripts, CI pipelines,
    external services) that cannot participate in an interactive OAuth flow.

    DynamoDB table schema
    ----------------------
    * Partition key: ``key_id`` (String) – the opaque API key value
    * Required attributes: ``org_id`` (String), ``active`` (Boolean)
    * Optional attributes: ``org_name``, ``name``, ``email``

    Configuration (environment variables)
    --------------------------------------
    ``API_KEYS_TABLE`` *(optional)*:
        DynamoDB table name for API key look-ups.  Defaults to ``"api_keys"``.
    """

    @property
    def provider_name(self) -> str:
        return "api_key"

    def _get_key_record(self, key_id: str) -> Dict[str, Any] | None:
        table_name = os.environ.get("API_KEYS_TABLE", "api_keys")
        table = _dynamodb.Table(table_name)
        resp = table.get_item(Key={"key_id": key_id})
        return resp.get("Item")

    def authenticate(self, token: str) -> AuthResult:
        if not token:
            return AuthResult.failure("Missing API key")

        try:
            item = self._get_key_record(token)
        except Exception as exc:
            logger.error("DynamoDB error looking up API key: %s", exc)
            return AuthResult.failure("API key lookup failed")

        if not item:
            return AuthResult.failure("Invalid API key")

        if not item.get("active", True):
            return AuthResult.failure("API key is inactive")

        org_id = item.get("org_id")
        if not org_id:
            logger.error(
                "API key record is missing org_id (key prefix: %s…)", token[:8]
            )
            return AuthResult.failure("API key configuration error")

        user_info = {
            "sub": item.get("key_id", token),
            "email": item.get("email", ""),
            "name": item.get("name", ""),
            "org_id": org_id,
            "org_name": item.get("org_name", ""),
        }
        return AuthResult.success(user_info)
