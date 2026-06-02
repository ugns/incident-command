# Decoupling Authentication & Making the API Reusable

This document evaluates how authentication was coupled into the Incident
Command API, the problems that coupling created, and the decoupling strategy
implemented in `src/EventCoord/auth/`. It is intended both as a record of the
refactor and as a guide for adding new authentication methods.

---

## 1. Where authentication lived before

Authentication and token handling were spread across four places, each with its
own copy of part of the logic:

| Concern | Location (before) | Notes |
| --- | --- | --- |
| Provider contract + registry | `lambda/login/handler.py` | `AuthProvider` Protocol and the `PROVIDERS` dict were defined *inside* the login Lambda. |
| Google verification + org lookup | `lambda/login/googleAuthProvider.py` | Local module (imported as `from googleAuthProvider import ...`), not part of the shared package. |
| Token **minting** | `lambda/login/handler.py` | Private-key fetch, `kid`/`jku` header assembly, claim copying and `jwt.encode` inlined in the handler. |
| Token **verification** (REST/WS) | `lambda/authorizer/handler.py` | JWKS fetch with a module-level cache. |
| Token **verification** (handlers) | `src/EventCoord/client/auth.py` | A *second*, slightly different verifier with retry/backoff. |
| Token **decoding** (handlers) | `src/EventCoord/utils/response.py` (`decode_claims`) | A *third* path that reads claims **without verifying the signature** (trusts the authorizer). |

### Coupling problems identified

1. **Provider registry not reusable.** The `AuthProvider` Protocol and the
   `{"google": ...}` registry lived in the login handler. Anything else that
   wanted to authenticate a credential (a future WebSocket login, a CLI, a
   batch job) could not reuse them, and adding a provider meant editing the
   handler.

2. **Google provider not in the shared layer.** It sat in `lambda/login/` and
   was imported by filename. It could not be unit tested with the rest of the
   `EventCoord` package and could not be shared.

3. **Eager, import-time DynamoDB scan.** `googleAuthProvider.py` computed
   `valid_auds = [org['aud'] for org in Organization.list_all() ...]` **at
   module import**. Consequences:
   - A DynamoDB *scan* ran during every cold start.
   - Organisations created after a container warmed up were invisible until the
     container recycled.
   - The module could not be imported (or tested) without live AWS access.

4. **Tenancy policy baked into the provider.** "Look up the org by `aud`" is a
   Google/OAuth-specific rule. Other methods resolve tenancy differently (by
   email domain, by an explicit `org_id` on an API key, by a single fixed org
   for single-tenant installs). That rule was hard-wired into the provider.

5. **Identity vs. token-minting mixed together.** The login handler both
   *verified who the caller was* and *minted the API's own JWT*. These are
   separate responsibilities with separate keys and lifecycles.

6. **Three divergent verifiers.** The authorizer, the client helper, and
   `decode_claims` each implemented token handling differently (caching vs.
   retry vs. no verification, and two different ways of deriving the expected
   issuer). Drift between the signer and verifiers is a real security risk.

7. **Ad-hoc claim shapes.** The claim set (`email`, `sub`, `name`, `hd`,
   `org_id`, `org_name`, `givenName`, `familyName`) was re-spelled in the login
   handler, the authorizer context, and `Flags` independently.

---

## 2. Decoupling strategy

The refactor introduces a single, dependency-free, unit-testable package,
`EventCoord.auth`, built around four small abstractions:

```
EventCoord.auth/
├── identity.py              # Identity: canonical normalised principal
├── org_resolver.py          # OrgResolver strategies (aud / domain / static)
├── providers/
│   ├── base.py              # AuthProvider Protocol + AuthError/AuthResult
│   ├── registry.py          # AuthProviderRegistry
│   └── google.py            # GoogleAuthProvider (DI: jwks fetcher + org resolver)
└── tokens.py                # TokenIssuer + TokenVerifier
```

### 2.1 `Identity` — one shape for everyone

Every provider normalises its provider-specific payload into a single
`Identity` dataclass. All downstream code (token minting, the authorizer
context, `Flags`, the resource handlers) depends only on `Identity`, never on
the originating provider.

`Identity.to_claims()` deliberately keeps the **existing wire spellings**
(`givenName` / `familyName`) so already-issued tokens and the current frontend
keep working; `from_claims()` accepts both camelCase and snake_case.

### 2.2 `AuthProvider` — the extension point

```python
class AuthProvider(Protocol):
    name: str
    def authenticate(self, credential: str) -> tuple[Identity | None, AuthError | None]:
        ...
```

Providers never raise for ordinary auth failures; they return a structured
`AuthError` (carrying a client-safe message and an HTTP status). Adding a new
method (GitHub, Cognito, SAML assertion, API key, email/password,
machine-to-machine client credentials) means writing one class and registering
it — nothing else changes.

### 2.3 `AuthProviderRegistry` — pluggable selection

A small name→provider registry replaces the in-handler `PROVIDERS` dict.
Registration is **explicit** (no import-time magic) so the cold-start path stays
predictable. The login handler builds its registry in `build_registry()`:

```python
def build_registry() -> AuthProviderRegistry:
    org_resolver = AudienceOrgResolver(Organization)
    reg = AuthProviderRegistry()
    reg.register(GoogleAuthProvider(org_resolver))
    # reg.register(GithubAuthProvider(...))
    # reg.register(ApiKeyProvider(StaticOrgResolver(...)))
    return reg
```

### 2.4 `OrgResolver` — tenancy policy out of the provider

The provider no longer decides how a principal maps to an organisation. Three
strategies ship:

- `AudienceOrgResolver` — by token `aud` (the original Google behaviour), but
  the DynamoDB lookup is now **lazy/per-request** and the model is **injected**.
- `HostedDomainOrgResolver` — by `hd` claim, falling back to the email domain.
- `StaticOrgResolver` — a single fixed org (single-tenant / dev / service keys).

This is what makes the same provider reusable across deployments with different
tenancy rules.

### 2.5 `TokenIssuer` / `TokenVerifier` — one signer, one verifier

`TokenIssuer.issue(identity)` encapsulates private-key retrieval (injected),
`kid`/`jku`/`iat`/`exp` assembly and signing. `TokenVerifier.verify(token)`
provides the single verification implementation — JWKS caching **and**
retry-with-backoff **and** automatic refresh on failure (covering all three
behaviours that previously diverged). Key material is injected, so both classes
are fully unit-testable without AWS.

The authorizer and `client/auth.py` now both delegate to `TokenVerifier`,
collapsing three verifiers into one.

---

## 3. What changed (and what did not)

**Refactored to use the shared package**

- `lambda/login/handler.py` → builds a registry + uses `TokenIssuer`.
- `lambda/authorizer/handler.py` → uses `TokenVerifier`; token extraction for
  REST headers and WebSocket query params kept intact.
- `src/EventCoord/client/auth.py` → delegates to `TokenVerifier`; public
  `require_auth` / `check_auth` API unchanged.
- `lambda/login/googleAuthProvider.py` → **removed** (logic moved to
  `EventCoord.auth.providers.google`).

**Intentionally preserved (no behaviour change)**

- The login response body (`{"token", "user"}`) and JWT claim spellings.
- The authorizer context keys (`email`, `sub`, `name`, `hd`, `org_id`,
  `org_name`).
- Issuer/JWKS URL conventions and environment variables
  (`JWT_ISSUER`, `JWT_PRIVATE_KEY_SECRET_ARN`, `TOKEN_TTL`, `JWKS_URL`).
- `decode_claims` / `get_claims` in handlers (the trusted, post-authorizer
  decode path). See the note below.

---

## 4. Adding a new authentication method

1. Implement the provider:

```python
from EventCoord.auth import Identity
from EventCoord.auth.providers.base import AuthError

class ApiKeyProvider:
    name = "apikey"

    def __init__(self, key_store, org_resolver):
        self._keys = key_store
        self._orgs = org_resolver

    def authenticate(self, credential: str):
        record = self._keys.lookup(credential)
        if not record:
            return None, AuthError("Invalid API key")
        org = self._orgs.resolve(record)
        if not org:
            return None, AuthError("Key not bound to an organization")
        return Identity(
            subject=record["key_id"],
            provider=self.name,
            org_id=org["org_id"],
            org_name=org.get("name"),
        ), None
```

2. Register it in `build_registry()` (or any registry you construct).

3. Done. Token issuing, verification, the authorizer context, and every
   resource handler already work because they only depend on `Identity`.

---

## 5. Follow-up opportunities (not in this change)

- **Clarify the unverified decode path.** `decode_claims` (used by every
  resource handler via `get_claims`) reads claims **without** verifying the
  signature, relying on the API Gateway authorizer having already validated the
  token. This is a valid pattern but an implicit coupling; consider renaming it
  to make the "trusted, post-authorizer" contract explicit, or having it verify
  when invoked outside the gateway.
- **Migrate to registered claim names.** Tokens still use `givenName` /
  `familyName` for backwards compatibility. A future major version could move to
  `given_name` / `family_name` once the frontend is updated.
- **Provider auto-discovery.** Providers could be registered via entry points
  so deployments can enable methods through configuration rather than code.
- **Standardise model method names.** `Organization` mixes `get_by_aud`,
  `get_by_org_id`, `list_all`; a `get_by_domain` would enable
  `HostedDomainOrgResolver` out of the box.
