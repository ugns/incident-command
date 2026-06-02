"""A small registry so auth methods can be added without editing handlers."""

from __future__ import annotations

from typing import Dict, Iterable, List, Optional

from EventCoord.auth.providers.base import AuthProvider


class AuthProviderRegistry:
    """Name -> :class:`AuthProvider` lookup.

    A process-wide default instance (:data:`registry`) is provided, but callers
    may construct their own isolated registry (handy for tests). Registration
    is explicit rather than import-time magic so behaviour stays predictable in
    the Lambda cold-start path.
    """

    def __init__(self) -> None:
        self._providers: Dict[str, AuthProvider] = {}

    def register(self, provider: AuthProvider, *, name: Optional[str] = None) -> AuthProvider:
        key = (name or getattr(provider, "name", "")).lower()
        if not key:
            raise ValueError("Auth provider must have a non-empty name")
        self._providers[key] = provider
        return provider

    def unregister(self, name: str) -> None:
        self._providers.pop(name.lower(), None)

    def get(self, name: str) -> Optional[AuthProvider]:
        return self._providers.get((name or "").lower())

    def names(self) -> List[str]:
        return sorted(self._providers.keys())

    def __contains__(self, name: object) -> bool:
        return isinstance(name, str) and name.lower() in self._providers

    def __iter__(self) -> Iterable[AuthProvider]:
        return iter(self._providers.values())


#: Default, process-wide registry used by the Lambda handlers.
registry = AuthProviderRegistry()
