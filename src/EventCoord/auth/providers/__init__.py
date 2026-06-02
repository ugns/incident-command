"""Authentication providers and the registry used to discover them."""

from EventCoord.auth.providers.base import (
    AuthError,
    AuthProvider,
    AuthResult,
)
from EventCoord.auth.providers.registry import AuthProviderRegistry, registry

__all__ = [
    "AuthError",
    "AuthProvider",
    "AuthResult",
    "AuthProviderRegistry",
    "registry",
]
