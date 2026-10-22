import threading
import time
from typing import Any, List

import requests


class JwksClient:
    """
    Thread-safe JWKS fetcher with in-memory time-based caching.

    A single instance can be shared safely across Lambda invocations within
    the same execution environment.

    Parameters
    ----------
    url:
        Full JWKS endpoint URL, e.g.
        ``https://api.example.com/.well-known/jwks.json``.
    cache_expiry:
        How long (seconds) to cache the key set before re-fetching.
        Defaults to 300 (5 minutes).
    timeout:
        HTTP request timeout in seconds.  Defaults to 5.

    Example::

        _client = JwksClient("https://api.example.com/.well-known/jwks.json")

        def verify(token: str) -> JWTClaims:
            jwks = _client.get_keys()
            return JsonWebToken(["RS256"]).decode(token, jwks)
    """

    def __init__(self, url: str, cache_expiry: int = 300, timeout: int = 5) -> None:
        self.url = url
        self.cache_expiry = cache_expiry
        self.timeout = timeout
        self._cache: List[Any] = []
        self._lock = threading.Lock()
        self._last_fetch: float = 0.0

    def get_keys(self) -> List[Any]:
        """Return the cached JWKS key list, refreshing when stale."""
        now = time.time()
        with self._lock:
            if not self._cache or (now - self._last_fetch) > self.cache_expiry:
                resp = requests.get(self.url, timeout=self.timeout)
                resp.raise_for_status()
                self._cache = resp.json()["keys"]
                self._last_fetch = now
        return self._cache

    def invalidate(self) -> None:
        """Force the next :meth:`get_keys` call to re-fetch from the endpoint."""
        with self._lock:
            self._cache = []
            self._last_fetch = 0.0
