from jose import jwt

from EventCoord.utils.handler import CORS_HEADERS, get_claims


def test_get_claims_missing_headers_returns_empty_dict() -> None:
    assert get_claims({}) == {}


def test_get_claims_parses_bearer_token() -> None:
    token = jwt.encode({"sub": "user-123", "org_id": "org-1"}, "secret", algorithm="HS256")
    event = {"headers": {"Authorization": f"Bearer {token}"}}
    claims = get_claims(event)
    assert claims["sub"] == "user-123"
    assert claims["org_id"] == "org-1"


def test_cors_headers_has_standard_keys() -> None:
    assert "Access-Control-Allow-Origin" in CORS_HEADERS
    assert "Access-Control-Allow-Headers" in CORS_HEADERS
    assert "Access-Control-Allow-Methods" in CORS_HEADERS
