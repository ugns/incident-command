import logging
import os
from typing import Any, Dict

from aws_xray_sdk.core import patch_all, xray_recorder

from EventCoord.utils.response import decode_claims

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
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


def get_claims(event: Dict[str, Any]) -> Dict[str, Any]:
    claims = decode_claims(event)
    if claims is None:
        return {}
    if isinstance(claims, dict):
        return claims
    try:
        return dict(claims)
    except Exception:
        return {}
