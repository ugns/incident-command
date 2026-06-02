"""
Tests for the EventCoord.auth package.

Covers: AuthResult, AuthProviderRegistry, JwksClient, and the
HandlerContext/get_handler_context utilities.
"""
from unittest.mock import MagicMock, patch

import pytest
from jose import jwt

from EventCoord.auth.jwks import JwksClient
from EventCoord.auth.provider import AuthResult
from EventCoord.auth.registry import AuthProviderRegistry
from EventCoord.utils.handler import CORS_HEADERS, HandlerContext, get_handler_context


# ---------------------------------------------------------------------------
# AuthResult
# ---------------------------------------------------------------------------


class TestAuthResult:
    def test_success_factory(self):
        user = {"sub": "u1", "email": "a@b.com", "org_id": "org-1", "org_name": "Org"}
        result = AuthResult.success(user)
        assert result.user_info == user
        assert result.error is None

    def test_failure_factory_basic(self):
        result = AuthResult.failure("Invalid token")
        assert result.user_info is None
        assert result.error == {"error": "Invalid token"}

    def test_failure_factory_with_extra(self):
        result = AuthResult.failure("Unsupported provider", supported=["google"])
        assert result.error["error"] == "Unsupported provider"
        assert result.error["supported"] == ["google"]

    def test_is_named_tuple(self):
        result = AuthResult.success({"sub": "x", "org_id": "o"})
        user_info, error = result
        assert user_info is not None
        assert error is None

    def test_truthy_on_success(self):
        result = AuthResult.success({"sub": "x"})
        assert not result.error
        assert result.user_info


# ---------------------------------------------------------------------------
# AuthProviderRegistry
# ---------------------------------------------------------------------------


def _make_provider(name: str, succeed: bool = True) -> MagicMock:
    """Create a mock AuthProvider."""
    provider = MagicMock()
    provider.provider_name = name
    if succeed:
        provider.authenticate.return_value = AuthResult.success(
            {"sub": "u1", "email": "a@b.com", "org_id": "org-1", "org_name": "Acme"}
        )
    else:
        provider.authenticate.return_value = AuthResult.failure("Bad token")
    return provider


class TestAuthProviderRegistry:
    def test_register_and_get(self):
        registry = AuthProviderRegistry()
        p = _make_provider("google")
        registry.register(p)
        assert registry.get("google") is p
        assert registry.get("other") is None

    def test_names_sorted(self):
        registry = AuthProviderRegistry()
        registry.register(_make_provider("microsoft"))
        registry.register(_make_provider("google"))
        assert registry.names() == ["google", "microsoft"]

    def test_chained_registration(self):
        registry = (
            AuthProviderRegistry()
            .register(_make_provider("google"))
            .register(_make_provider("microsoft"))
        )
        assert set(registry.names()) == {"google", "microsoft"}

    def test_authenticate_dispatches_to_provider(self):
        registry = AuthProviderRegistry()
        p = _make_provider("google")
        registry.register(p)
        result = registry.authenticate("google", "tok123")
        p.authenticate.assert_called_once_with("tok123")
        assert result.user_info is not None

    def test_authenticate_unknown_provider(self):
        registry = AuthProviderRegistry()
        result = registry.authenticate("github", "tok")
        assert result.error is not None
        assert "Unsupported provider" in result.error["error"]
        assert result.error["supported"] == []

    def test_authenticate_unknown_provider_lists_registered(self):
        registry = AuthProviderRegistry()
        registry.register(_make_provider("google"))
        result = registry.authenticate("github", "tok")
        assert "google" in result.error["supported"]

    def test_authenticate_failed_provider(self):
        registry = AuthProviderRegistry()
        registry.register(_make_provider("google", succeed=False))
        result = registry.authenticate("google", "bad-tok")
        assert result.error is not None
        assert result.user_info is None

    def test_re_register_warning(self, caplog):
        import logging

        registry = AuthProviderRegistry()
        registry.register(_make_provider("google"))
        with caplog.at_level(logging.WARNING, logger="EventCoord.auth.registry"):
            registry.register(_make_provider("google"))
        assert any("Re-registering" in m for m in caplog.messages)


# ---------------------------------------------------------------------------
# JwksClient
# ---------------------------------------------------------------------------


class TestJwksClient:
    def _make_mock_response(self, keys=None):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"keys": keys or [{"kid": "k1"}]}
        mock_resp.raise_for_status = MagicMock()
        return mock_resp

    def test_fetches_keys_on_first_call(self):
        client = JwksClient("https://example.com/.well-known/jwks.json")
        mock_resp = self._make_mock_response()
        with patch("EventCoord.auth.jwks.requests.get", return_value=mock_resp) as mock_get:
            keys = client.get_keys()
        mock_get.assert_called_once()
        assert keys == [{"kid": "k1"}]

    def test_cache_hit_avoids_second_request(self):
        client = JwksClient("https://example.com/.well-known/jwks.json", cache_expiry=60)
        mock_resp = self._make_mock_response()
        with patch("EventCoord.auth.jwks.requests.get", return_value=mock_resp) as mock_get:
            client.get_keys()
            client.get_keys()
        assert mock_get.call_count == 1

    def test_cache_expiry_triggers_refetch(self):
        import time

        client = JwksClient(
            "https://example.com/.well-known/jwks.json", cache_expiry=0
        )
        mock_resp = self._make_mock_response()
        with patch("EventCoord.auth.jwks.requests.get", return_value=mock_resp) as mock_get:
            client.get_keys()
            # Expiry of 0 means every call is stale
            client.get_keys()
        assert mock_get.call_count == 2

    def test_invalidate_clears_cache(self):
        client = JwksClient("https://example.com/.well-known/jwks.json", cache_expiry=300)
        mock_resp = self._make_mock_response()
        with patch("EventCoord.auth.jwks.requests.get", return_value=mock_resp) as mock_get:
            client.get_keys()
            client.invalidate()
            client.get_keys()
        assert mock_get.call_count == 2

    def test_http_error_propagates(self):
        client = JwksClient("https://example.com/.well-known/jwks.json")
        mock_resp = MagicMock()
        mock_resp.raise_for_status.side_effect = Exception("HTTP 503")
        with patch("EventCoord.auth.jwks.requests.get", return_value=mock_resp):
            with pytest.raises(Exception, match="HTTP 503"):
                client.get_keys()


# ---------------------------------------------------------------------------
# HandlerContext / get_handler_context
# ---------------------------------------------------------------------------


def _make_event(org_id=None, method="GET", path_params=None, path="/volunteers"):
    token_payload = {"sub": "u1", "email": "a@b.com"}
    if org_id:
        token_payload["org_id"] = org_id
    token = jwt.encode(token_payload, "secret", algorithm="HS256")
    return {
        "headers": {"Authorization": f"Bearer {token}"},
        "httpMethod": method,
        "pathParameters": path_params,
        "resource": path,
        "path": path,
    }


class TestHandlerContext:
    def test_returns_context_when_org_id_present(self):
        event = _make_event(org_id="org-1", method="POST")
        ctx, err = get_handler_context(event)
        assert err is None
        assert ctx is not None
        assert ctx.org_id == "org-1"
        assert ctx.method == "POST"

    def test_returns_error_when_org_id_missing(self):
        event = _make_event(org_id=None)
        ctx, err = get_handler_context(event)
        assert ctx is None
        assert err is not None
        assert err["statusCode"] == 403

    def test_path_params_normalised_to_empty_dict(self):
        event = _make_event(org_id="org-1", path_params=None)
        ctx, err = get_handler_context(event)
        assert err is None
        assert ctx.path_params == {}

    def test_path_params_forwarded(self):
        event = _make_event(org_id="org-1", path_params={"volunteerId": "v1"})
        ctx, err = get_handler_context(event)
        assert err is None
        assert ctx.path_params == {"volunteerId": "v1"}

    def test_resource_path_from_resource_key(self):
        event = _make_event(org_id="org-1", path="/volunteers/{volunteerId}")
        event["resource"] = "/volunteers/{volunteerId}"
        ctx, err = get_handler_context(event)
        assert err is None
        assert ctx.resource_path == "/volunteers/{volunteerId}"

    def test_cors_headers_has_standard_keys(self):
        assert "Access-Control-Allow-Origin" in CORS_HEADERS
        assert "Access-Control-Allow-Headers" in CORS_HEADERS
        assert "Access-Control-Allow-Methods" in CORS_HEADERS
        assert "Access-Control-Expose-Headers" in CORS_HEADERS

    def test_handler_context_is_dataclass(self):
        ctx = HandlerContext(
            claims={"sub": "u1", "org_id": "o"},
            org_id="o",
            method="GET",
        )
        assert ctx.path_params == {}
        assert ctx.resource_path == ""
