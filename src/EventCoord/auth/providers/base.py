"""The provider contract every authentication method implements."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol, Tuple, runtime_checkable

from EventCoord.auth.identity import Identity


@dataclass
class AuthError:
    """A structured authentication failure.

    Attributes:
        message: Human readable, client-safe error message.
        status_code: HTTP status the caller should surface (defaults to 401).
    """

    message: str
    status_code: int = 401

    def to_body(self) -> dict:
        return {"error": self.message}


# An authentication attempt yields exactly one of (identity, error).
AuthResult = Tuple[Optional[Identity], Optional[AuthError]]


@runtime_checkable
class AuthProvider(Protocol):
    """Validate a provider-specific credential into a normalised identity.

    Implementations MUST NOT raise for ordinary authentication failures;
    instead they return ``(None, AuthError(...))``. They return
    ``(Identity, None)`` on success.

    The ``credential`` is intentionally untyped (``str``) because most methods
    exchange an opaque token/key string. Providers that need richer input can
    accept a JSON string and parse it.
    """

    #: Stable, lower-case identifier used to select the provider (e.g. "google").
    name: str

    def authenticate(self, credential: str) -> AuthResult:
        ...
