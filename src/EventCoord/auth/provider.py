from typing import Any, Dict, NamedTuple, Optional, Protocol

UserInfo = Dict[str, Any]
AuthError = Dict[str, Any]


class AuthResult(NamedTuple):
    """
    Result of an authentication attempt.

    Exactly one of ``user_info`` (success) or ``error`` (failure) is
    populated; the other is ``None``.

    Use the factory class-methods instead of constructing directly::

        return AuthResult.success({"sub": "...", "email": "...", ...})
        return AuthResult.failure("Invalid token")
    """

    user_info: Optional[UserInfo]
    error: Optional[AuthError]

    @classmethod
    def success(cls, user_info: UserInfo) -> "AuthResult":
        """Return a successful result carrying *user_info*."""
        return cls(user_info=user_info, error=None)

    @classmethod
    def failure(cls, message: str, **extra: Any) -> "AuthResult":
        """Return a failed result with *message* (and any *extra* fields)."""
        return cls(user_info=None, error={"error": message, **extra})


class AuthProvider(Protocol):
    """
    Protocol for OAuth / token-based authentication providers.

    Implement this interface to add support for a new identity provider (e.g.
    Google, Microsoft, GitHub) or a static API-key store.  Register the
    concrete implementation with :class:`~EventCoord.auth.registry.AuthProviderRegistry`
    and pass its :attr:`provider_name` in the ``provider`` field of the login
    request body.

    Normalised ``user_info`` keys
    -----------------------------
    On success, ``user_info`` must include at minimum:

    * ``sub``       – subject identifier (unique per user per provider)
    * ``email``     – user's email address
    * ``name``      – display name (may be empty string)
    * ``org_id``    – organisation the user belongs to
    * ``org_name``  – human-readable organisation name

    Optional well-known keys: ``givenName``, ``familyName``, ``picture``,
    ``hd`` (hosted / tenant domain).
    """

    @property
    def provider_name(self) -> str:
        """Unique, URL-safe identifier for this provider (e.g. ``"google"``)."""
        ...

    def authenticate(self, token: str) -> AuthResult:
        """
        Validate *token* and return normalised user claims.

        On failure return an :class:`AuthResult` whose ``error`` dict contains
        at least an ``"error"`` key; that dict is returned verbatim as the
        HTTP 401 response body.
        """
        ...
