"""
EventCoord authentication provider framework.

This package provides a pluggable authentication abstraction that decouples
token validation logic from the login Lambda handler, making it straightforward
to add new identity providers without touching handler code.

Quick-start
-----------
::

    from EventCoord.auth import AuthProviderRegistry, AuthResult
    from EventCoord.auth.google import GoogleAuthProvider
    from EventCoord.auth.microsoft import MicrosoftAuthProvider
    from EventCoord.auth.api_key import ApiKeyAuthProvider

    registry = (
        AuthProviderRegistry()
        .register(GoogleAuthProvider())
        .register(MicrosoftAuthProvider())
        .register(ApiKeyAuthProvider())
    )

    result: AuthResult = registry.authenticate(provider_name, token)
    if result.error:
        ...  # return 401
    user_info = result.user_info  # guaranteed non-None on success

Adding a new provider
---------------------
1. Create a class that satisfies :class:`AuthProvider` (implement
   ``provider_name`` property and ``authenticate`` method).
2. Register it with the registry in the login handler.
3. No other changes required – the handler automatically accepts the new
   ``provider`` name in the request body.
"""

from EventCoord.auth.jwks import JwksClient
from EventCoord.auth.provider import AuthError, AuthProvider, AuthResult, UserInfo
from EventCoord.auth.registry import AuthProviderRegistry

__all__ = [
    "AuthError",
    "AuthProvider",
    "AuthProviderRegistry",
    "AuthResult",
    "JwksClient",
    "UserInfo",
]
