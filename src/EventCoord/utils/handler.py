import logging
import os
from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Optional, Tuple

from aws_xray_sdk.core import patch_all, xray_recorder

from EventCoord.utils.response import build_response, decode_claims
from EventCoord.utils.types import APIGatewayProxyEvent, APIGatewayProxyResponse

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
    "Access-Control-Expose-Headers": "Content-Disposition",
}


def init_tracing(service_name: str = "incident-cmd") -> None:
    patch_all()  # Automatically patches boto3, requests, etc.
    xray_recorder.configure(service=service_name)


def get_logger(name: str) -> logging.Logger:
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    if not logger.hasHandlers():
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logging.getLogger().setLevel(log_level)
    return logger


def get_claims(event: APIGatewayProxyEvent | Mapping[str, Any]) -> Dict[str, Any]:
    claims = decode_claims(event)
    if claims is None:
        return {}
    if isinstance(claims, dict):
        return claims
    try:
        return dict(claims)
    except Exception:
        return {}


@dataclass
class HandlerContext:
    """
    Common context extracted from an API Gateway Lambda proxy event.

    :meth:`get_handler_context` validates that ``org_id`` is present and
    returns an error response instead of this object when it is not, so callers
    can rely on :attr:`org_id` being a non-empty string.

    Attributes
    ----------
    claims:
        Decoded JWT payload forwarded by the API Gateway authorizer.
    org_id:
        Organisation scope derived from the ``org_id`` JWT claim.
    method:
        HTTP method (e.g. ``"GET"``, ``"POST"``).
    path_params:
        Path parameter dict from ``event["pathParameters"]`` (never ``None``).
    resource_path:
        The matched resource path template (e.g. ``/volunteers/{volunteerId}``).

    Usage::

        ctx, err = get_handler_context(event)
        if err:
            return err

        if ctx.method == "GET":
            items = MyModel.list(ctx.org_id)
            return build_response(200, items, headers=CORS_HEADERS)
    """

    claims: Dict[str, Any]
    org_id: str
    method: str
    path_params: Dict[str, Any] = field(default_factory=dict)
    resource_path: str = ""


def get_handler_context(
    event: APIGatewayProxyEvent | Mapping[str, Any],
) -> Tuple[Optional[HandlerContext], Optional[APIGatewayProxyResponse]]:
    """
    Extract :class:`HandlerContext` from an API Gateway proxy event.

    Returns ``(context, None)`` on success, or ``(None, error_response)``
    when the JWT does not carry a valid ``org_id`` claim (HTTP 403).

    Typical usage::

        ctx, err = get_handler_context(event)
        if err:
            return err
        # ctx is guaranteed non-None here
        items = MyModel.list(ctx.org_id)
    """
    claims = get_claims(event)
    org_id = claims.get("org_id")
    if not org_id:
        return None, build_response(
            403,
            {"error": "Missing organization (org_id claim) in token"},
            headers=CORS_HEADERS,
        )
    context = HandlerContext(
        claims=claims,
        org_id=org_id,
        method=event.get("httpMethod", "GET"),
        path_params=event.get("pathParameters") or {},
        resource_path=event.get("resource", "") or event.get("path", ""),
    )
    return context, None
