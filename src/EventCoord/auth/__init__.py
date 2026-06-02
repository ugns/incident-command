"""Reusable, provider-agnostic authentication building blocks.

This package decouples *how* a caller proves who they are (the
:class:`~EventCoord.auth.providers.base.AuthProvider` implementations) from
*how* the API issues and verifies its own session tokens
(:class:`~EventCoord.auth.tokens.TokenIssuer` /
:class:`~EventCoord.auth.tokens.TokenVerifier`).

The goal is that adding a new authentication method (GitHub, Cognito, SAML,
API keys, email/password, machine-to-machine client credentials, ...) only
requires implementing a small :class:`AuthProvider` and registering it -- no
changes to the Lambda handlers, token signing, or downstream resource code.
"""

from EventCoord.auth.identity import Identity
from EventCoord.auth.org_resolver import (
    AudienceOrgResolver,
    HostedDomainOrgResolver,
    OrgResolver,
    StaticOrgResolver,
)
from EventCoord.auth.providers import (
    AuthError,
    AuthProvider,
    AuthProviderRegistry,
    AuthResult,
    registry,
)
from EventCoord.auth.tokens import TokenIssuer, TokenVerifier

__all__ = [
    "Identity",
    "AuthProvider",
    "AuthError",
    "AuthResult",
    "AuthProviderRegistry",
    "registry",
    "OrgResolver",
    "AudienceOrgResolver",
    "HostedDomainOrgResolver",
    "StaticOrgResolver",
    "TokenIssuer",
    "TokenVerifier",
]
