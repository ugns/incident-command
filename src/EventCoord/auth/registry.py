import logging
from typing import Dict, List, Optional

from EventCoord.auth.provider import AuthProvider, AuthResult

logger = logging.getLogger(__name__)


class AuthProviderRegistry:
    """
    Registry / factory for :class:`~EventCoord.auth.provider.AuthProvider`
    implementations.

    Providers are keyed by their :attr:`~AuthProvider.provider_name`.  The
    login Lambda passes the ``provider`` field from the request body to
    :meth:`authenticate`, which dispatches to the matching provider.

    Usage::

        from EventCoord.auth.registry import AuthProviderRegistry
        from EventCoord.auth.google import GoogleAuthProvider
        from EventCoord.auth.microsoft import MicrosoftAuthProvider

        registry = AuthProviderRegistry()
        registry.register(GoogleAuthProvider())
        registry.register(MicrosoftAuthProvider())

        result = registry.authenticate("google", id_token)
        if result.error:
            return build_response(401, result.error, headers=CORS_HEADERS)
        # result.user_info is now guaranteed non-None
    """

    def __init__(self) -> None:
        self._providers: Dict[str, AuthProvider] = {}

    def register(self, provider: AuthProvider) -> "AuthProviderRegistry":
        """
        Register *provider* under its :attr:`~AuthProvider.provider_name`.

        Returns ``self`` so registrations can be chained::

            registry.register(GoogleAuthProvider()).register(MicrosoftAuthProvider())
        """
        name = provider.provider_name
        if name in self._providers:
            logger.warning("Re-registering auth provider '%s'", name)
        self._providers[name] = provider
        return self

    def get(self, name: str) -> Optional[AuthProvider]:
        """Return the provider registered under *name*, or ``None``."""
        return self._providers.get(name)

    def names(self) -> List[str]:
        """Return the sorted list of registered provider names."""
        return sorted(self._providers.keys())

    def authenticate(self, provider_name: str, token: str) -> AuthResult:
        """
        Dispatch a token to the named provider and return an
        :class:`~EventCoord.auth.provider.AuthResult`.

        Returns a failure result (with an ``"error"`` and ``"supported"`` key)
        when the provider is not registered.
        """
        provider = self._providers.get(provider_name)
        if not provider:
            logger.warning(
                "Requested auth provider '%s' is not registered", provider_name
            )
            return AuthResult(
                user_info=None,
                error={
                    "error": f"Unsupported provider: {provider_name}",
                    "supported": self.names(),
                },
            )
        return provider.authenticate(token)
