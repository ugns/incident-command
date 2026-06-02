"""Strategies for mapping an authenticated principal to an organisation.

Multi-tenancy in EventCoord is driven entirely by ``org_id``. The *rule* used
to derive that ``org_id`` is, however, specific to each deployment and auth
method:

* Google Workspace logins map the token ``aud`` (OAuth client id) to an org.
* Other IdPs might map on a hosted-domain / email domain.
* API-key or service credentials might carry the ``org_id`` explicitly.

Keeping this rule behind the :class:`OrgResolver` protocol means providers stay
ignorant of tenancy policy, and the policy can be swapped without touching any
provider.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Protocol, runtime_checkable


@runtime_checkable
class OrgResolver(Protocol):
    """Resolve the organisation record for a set of provider claims."""

    def resolve(self, claims: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Return an org record (``{"org_id": ..., "name": ...}``) or ``None``."""
        ...


class AudienceOrgResolver:
    """Resolve an org by the token audience (``aud``).

    This preserves the original Google behaviour but defers the DynamoDB lookup
    to request time and accepts the organisation model as an injected
    dependency, so it can be unit tested without AWS.
    """

    def __init__(self, organization_model: Any) -> None:
        self._orgs = organization_model

    def resolve(self, claims: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        aud = claims.get("aud")
        if not isinstance(aud, str) or not aud:
            return None
        return self._orgs.get_by_aud(aud)


class HostedDomainOrgResolver:
    """Resolve an org by a hosted/email domain claim.

    Looks at the ``hd`` claim first, then falls back to the domain portion of
    the ``email`` claim. Requires the organisation model to expose a
    ``get_by_domain`` lookup.
    """

    def __init__(self, organization_model: Any) -> None:
        self._orgs = organization_model

    def resolve(self, claims: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        domain = claims.get("hd")
        if not domain:
            email = claims.get("email") or ""
            if "@" in email:
                domain = email.rsplit("@", 1)[-1]
        if not domain:
            return None
        getter = getattr(self._orgs, "get_by_domain", None)
        if getter is None:
            return None
        return getter(domain)


class StaticOrgResolver:
    """Always resolve to a single, fixed organisation.

    Useful for single-tenant deployments, local development, or service
    credentials that are scoped to one org.
    """

    def __init__(self, org: Dict[str, Any]) -> None:
        self._org = org

    def resolve(self, claims: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return self._org
