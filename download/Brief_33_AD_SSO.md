# Brief #33 — Active Directory / SSO Authentication (OIDC + SCIM)

**Author:** RahMirz (delivered to Kimi for implementation)
**Date:** 30 August 2026
**Status:** Ready for implementation (after Brief #32 completes)
**Estimated effort:** 2–3 weeks (6 phases)
**Predecessor:** Brief #17 (users, roles, clearance) — SSO will provision users into the existing model

---

## 1. Problem

Every enterprise procurement security review asks the same question in the first 10 minutes: "Does Seekra integrate with our Active Directory / Azure AD?" The current answer — "no, Seekra manages its own passwords" — fails the review. IT teams will not deploy a system where:

- New hires require a separate Seekra account creation step
- Offboards require a separate Seekra deactivation step (which may be missed)
- Password policies diverge from corporate standards
- Users have to remember yet another password

SSO eliminates all four problems. Group-to-role mapping eliminates the operational overhead of manual role assignment.

## 2. Goals

1. **OIDC login** — users click "Sign in with SSO", redirect to corporate IdP, authenticate, return to Seekra with a JWT. No Seekra password required.
2. **Just-in-time provisioning** — first SSO login auto-creates the Seekra user row with a default department + clearance (configurable per IdP).
3. **Group-to-role mapping** — IdP groups (e.g. `Seekra-Films-Editors`) map to Seekra roles + department memberships. Joining an AD group auto-updates Seekra access; leaving the group auto-removes access.
4. **SCIM provisioning** (phase 4) — automatic user create/update/delete from Azure AD, so HR-driven offboards propagate to Seekra within minutes without anyone touching Seekra.
5. **Multi-IdP** — support multiple SSO configs per tenant (one for employees, one for contractors, one for a parent organization).
6. **Fallback local login** — local password login still works for break-glass admin accounts (configured per tenant, default 1 allowed).

## 3. Non-goals

- **No SAML 2.0** in initial release — OIDC covers 95% of modern IdPs (Azure AD, Google Workspace, Keycloak, Okta). SAML can be added in a follow-up brief if a specific customer requires AD FS on-prem.
- **No LDAP bind authentication** — direct LDAP is a legacy pattern; OIDC via Azure AD is the modern equivalent.
- **No password sync** — Seekra never stores or syncs the IdP password.
- **No multi-factor enforcement** — MFA is the IdP's responsibility, not Seekra's. Seekra respects the IdP's MFA prompt.

## 4. Architecture

### 4.1 OIDC flow

```
User → /login → click "Sign in with SSO"
  ↓
Seekra redirects to IdP authorization endpoint
  ?client_id=...&redirect_uri=https://app.seekra.pk/auth/callback&scope=openid+profile+email+groups&state=...
  ↓
User authenticates at IdP (Azure AD, Google, Keycloak)
  ↓
IdP redirects back to /auth/callback?code=...&state=...
  ↓
Seekra exchanges code for tokens (POST to IdP token endpoint)
  → id_token (JWT containing user claims: sub, email, name, groups)
  → access_token (for SCIM user info queries if needed)
  ↓
Seekra verifies id_token signature against IdP's JWKS
  ↓
Seekra extracts claims: email, name, groups
  ↓
Just-in-time provisioning (if user doesn't exist):
  - Create User row with username = email, role from group mapping, clearance from group mapping
  - Hash a random unusable password (so local login is impossible for SSO users)
  - Add org_memberships based on group mapping
  ↓
Seekra issues its own JWT (existing token flow) and sets the cookie
  ↓
User is logged in
```

### 4.2 Database changes

```sql
-- backend/migrations/20260908_step46_sso.sql

CREATE TABLE IF NOT EXISTS sso_providers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,            -- "Azure AD (Corporate)", "Google Workspace"
    provider_type VARCHAR(50) NOT NULL,    -- "oidc" (saml in future)
    issuer VARCHAR(500) NOT NULL,           -- IdP issuer URL (e.g. https://login.microsoftonline.com/{tenant}/v2.0)
    client_id VARCHAR(500) NOT NULL,
    client_secret_encrypted TEXT NOT NULL,  -- AES-256 encrypted
    jwks_uri VARCHAR(500) NOT NULL,         -- where to fetch IdP public keys
    scopes VARCHAR(200) NOT NULL DEFAULT 'openid profile email groups',
    -- Azure AD uses 'groups' for group claims; Google uses 'groups' too; Keycloak uses 'realm roles'
    groups_claim VARCHAR(100) NOT NULL DEFAULT 'groups',
    -- Default provisioning config: if no group mapping matches, what to assign?
    default_role VARCHAR(20) NOT NULL DEFAULT 'viewer'
        CHECK (default_role IN ('admin', 'editor', 'viewer', 'auditor')),
    default_clearance INTEGER NOT NULL DEFAULT 1
        CHECK (default_clearance BETWEEN 0 AND 3),
    default_scope_org_id INTEGER REFERENCES org_nodes(id),  -- NULL = root
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_sso_providers_active ON sso_providers (is_active);

-- Group-to-role/scope mapping
CREATE TABLE IF NOT EXISTS sso_group_mappings (
    id SERIAL PRIMARY KEY,
    provider_id INTEGER NOT NULL REFERENCES sso_providers(id) ON DELETE CASCADE,
    idp_group_name VARCHAR(200) NOT NULL,   -- e.g. "Seekra-Films-Editors"
    seekra_role VARCHAR(20) NOT NULL
        CHECK (seekra_role IN ('admin', 'editor', 'viewer', 'auditor')),
    clearance_level INTEGER NOT NULL DEFAULT 1
        CHECK (clearance_level BETWEEN 0 AND 3),
    -- When a user is a member of this IdP group, add them to these org nodes
    -- (multiple rows per group → multiple memberships)
    scope_org_id INTEGER REFERENCES org_nodes(id),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (provider_id, idp_group_name, scope_org_id)
);
CREATE INDEX idx_sso_group_mappings_provider ON sso_group_mappings (provider_id);

-- Track which users came from which SSO provider (for SCIM + audit)
ALTER TABLE users ADD COLUMN IF NOT EXISTS sso_provider_id INTEGER REFERENCES sso_providers(id);
ALTER TABLE users ADD COLUMN IF NOT EXISTS sso_external_id VARCHAR(500);  -- IdP's sub claim
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_sso_user BOOLEAN NOT NULL DEFAULT FALSE;
CREATE INDEX IF NOT EXISTS idx_users_sso_external ON users (sso_provider_id, sso_external_id);

-- SCIM sync state
CREATE TABLE IF NOT EXISTS sso_sync_state (
    provider_id INTEGER PRIMARY KEY REFERENCES sso_providers(id) ON DELETE CASCADE,
    last_synced_at TIMESTAMP,
    last_sync_status VARCHAR(20),  -- 'ok', 'error', 'partial'
    last_error TEXT
);
```

### 4.3 Group mapping logic

On every SSO login:

1. Extract `groups` claim from id_token (or call `/me` API with access_token if groups aren't in the id_token — configurable per provider).
2. Query `sso_group_mappings` for all matching `idp_group_name` values.
3. Compute the user's:
   - **Role**: highest-privilege role from all matching mappings (admin > editor > viewer, auditor is separate). If no mapping, use `sso_providers.default_role`.
   - **Clearance**: highest clearance from all matching mappings. If no mapping, use `default_clearance`.
   - **Org memberships**: union of all `scope_org_id` from matching mappings. If no mapping, add to `default_scope_org_id`.
4. Update the user row with the computed role + clearance.
5. Reconcile `user_org_memberships`:
   - Add any memberships from the mapping that the user doesn't have.
   - **Remove** memberships from SSO-managed scopes that the user no longer has via the mapping. (Local-admin-added memberships are preserved — track via a `is_sso_managed` flag on `user_org_memberships`.)
6. If the user was removed from ALL IdP groups (no mappings match), set `is_active = false` (soft-deactivate per Brief #17 Phase 6).

### 4.4 SCIM provisioning (phase 4)

Seekra exposes a SCIM 2.0 endpoint at `/api/scim/v2`:

- `GET /Users` — list users (paginated, filtered by IdP)
- `POST /Users` — create a user (called by Azure AD when a new hire is provisioned)
- `GET /Users/{id}` — fetch one user
- `PATCH /Users/{id}` — update attributes (e.g. group membership change)
- `DELETE /Users/{id}` — deactivate (called by Azure AD on offboard)

Auth: SCIM requests authenticated via a bearer token configured per `sso_provider`. Azure AD sends this token in the `Authorization` header.

When Azure AD calls `DELETE /Users/{id}`: Seekra soft-deletes the user (Brief #17 Phase 6) — tokens invalidate instantly, audit trail preserved.

## 5. Phases

### Phase 1 — OIDC provider config + login flow (Week 1)

**Scope:**
- Migration `20260908_step46_sso.sql`.
- New `backend/app/services/sso.py` with:
  - `get_authorization_url(provider_id, state)` — builds the IdP authorization URL with correct params.
  - `exchange_code_for_tokens(provider_id, code)` — POST to IdP token endpoint.
  - `verify_id_token(provider_id, id_token)` — fetch JWKS from `jwks_uri`, verify signature, verify `iss` + `aud` + `exp`.
  - `extract_claims(provider_id, id_token)` — return dict with `sub`, `email`, `name`, `groups`.
- New endpoints:
  - `GET /api/auth/sso/providers` — list active SSO providers (public, used by /login page to show buttons)
  - `GET /api/auth/sso/{provider_id}/login` — generates state, stores in Redis with 10-min TTL, redirects to IdP authorization URL.
  - `GET /api/auth/sso/callback` — receives `code` + `state`, validates state, exchanges code, verifies id_token, provisions user (if needed), issues Seekra JWT, sets cookie, redirects to `/`.
- Admin endpoints (require `require_admin()`):
  - `GET /api/admin/sso/providers` — list all providers
  - `POST /api/admin/sso/providers` — create provider
  - `PATCH /api/admin/sso/providers/{id}` — update
  - `DELETE /api/admin/sso/providers/{id}` — soft-delete (set `is_active = false`)
  - `POST /api/admin/sso/providers/{id}/test` — fetch JWKS, verify issuer reachable
- Audit events: `SSO_LOGIN_SUCCESS`, `SSO_LOGIN_FAILED`, `SSO_USER_PROVISIONED`, `SSO_USER_UPDATED`.
- Frontend `/login` page: show "Sign in with SSO" buttons for each active provider (in addition to existing username/password form).
- Frontend `/admin/sso` page: list, create, edit, deactivate providers.

**Acceptance criteria:**
- Admin configures an Azure AD OIDC provider with valid client_id, client_secret, issuer URL.
- "Test connection" fetches JWKS and returns green.
- User visits `/login`, sees "Sign in with Azure AD" button.
- Click → redirects to Microsoft login → user authenticates → redirects back to Seekra → user is logged in.
- If user's email doesn't exist in Seekra → user row created with `default_role = viewer`, `default_clearance = 1`, added to `default_scope_org_id` org node.
- Audit trail shows `SSO_LOGIN_SUCCESS` + `SSO_USER_PROVISIONED` (first login) or `SSO_USER_UPDATED` (subsequent logins).
- User clicks "Sign out" → Seekra JWT cleared; IdP session untouched (Seekra does NOT do single logout yet — that's phase 6).

### Phase 2 — Group-to-role mapping (Week 2)

**Scope:**
- New endpoints for group mappings:
  - `GET /api/admin/sso/providers/{id}/mappings`
  - `POST /api/admin/sso/providers/{id}/mappings`
  - `PATCH /api/admin/sso/mappings/{id}`
  - `DELETE /api/admin/sso/mappings/{id}`
- Frontend `/admin/sso/providers/{id}` page: table of group mappings with "Add mapping" button.
- Group reconciliation logic in `sso.py:reconcile_user_from_groups(user, provider, idp_groups)`:
  - Compute role, clearance, org memberships per 4.3.
  - Update user row.
  - Diff current `user_org_memberships` vs computed; add missing, remove SSO-managed ones no longer in mapping.
  - Mark all SSO-managed memberships with `is_sso_managed = true` (new column on `user_org_memberships`).
- Called on every SSO login.
- Audit: `SSO_GROUP_MAPPING_APPLIED` with details (groups matched, role, clearance, scope changes).

**Acceptance criteria:**
- Admin creates a group mapping: `Seekra-Films-Editors` → role=editor, clearance=2, scope="Films · Production".
- User logs in via SSO; their IdP groups include `Seekra-Films-Editors`.
- After login, user has role=editor, clearance=2, member of "Films · Production" org node.
- Admin adds `Seekra-Group-Executive` mapping (role=admin, clearance=3, scope=Group Executive) and the user is in BOTH IdP groups.
- After next SSO login, user has role=admin (highest), clearance=3 (highest), member of BOTH Films · Production and Group Executive.
- Admin removes user from `Seekra-Films-Editors` in Azure AD.
- After next SSO login, user no longer has Films · Production membership (SSO-managed, removed), but retains Group Executive (still in that IdP group).
- If user is removed from ALL IdP groups, after next login they are soft-deactivated (`is_active = false`).

### Phase 3 — Frontend polish + error handling (Week 2)

**Scope:**
- `/login` page: show provider buttons with logos (Microsoft, Google, Keycloak generic). Bilingual labels (EN + AR).
- Error page for failed SSO (invalid state, expired token, IdP unreachable) — clear error message + "Try again" link.
- Loading state during callback (show spinner while exchanging code).
- "Remember this provider" checkbox — sets a cookie so next visit auto-redirects to the user's chosen IdP (skipping the login page).
- i18n strings for all SSO UI.

**Acceptance criteria:**
- SSO with invalid credentials shows a clean error page (not a stack trace).
- Arabic UI renders correctly with RTL layout.
- "Remember this provider" works — second visit skips login page.

### Phase 4 — SCIM 2.0 endpoint (Week 3)

**Scope:**
- New `backend/app/api/scim.py` with the SCIM 2.0 endpoints listed in 4.4.
- Auth: per-provider bearer token (generated when admin creates the provider, shown once).
- SCIM schema responses (`/Schemas`, `/ServiceProviderConfig`, `/ResourceTypes`) for Azure AD's setup wizard.
- Mapping SCIM attributes to Seekra fields:
  - `userName` → `users.username`
  - `emails[0].value` → `users.email`
  - `displayName` → `users.username` (fallback)
  - `active` → `users.is_active`
  - `groups[].display` → lookup in `sso_group_mappings.idp_group_name` → role + scope
- `DELETE /Users/{id}` → soft-delete (Brief #17 Phase 6).
- Audit events: `SCIM_USER_CREATED`, `SCIM_USER_UPDATED`, `SCIM_USER_DEACTIVATED`.
- Frontend `/admin/sso/providers/{id}` page shows the SCIM base URL + bearer token (with copy-to-clipboard button) for Azure AD config.

**Acceptance criteria:**
- Admin opens Azure AD → Enterprise Applications → Seekra → Provisioning → enters the SCIM URL + bearer token.
- Azure AD tests the connection — passes.
- Admin adds a new user in Azure AD assigned to the Seekra app.
- Within minutes (Azure AD's sync cycle), the user appears in Seekra `/admin/users` with `is_sso_user = true`.
- Admin removes the user from the Seekra app in Azure AD.
- Within minutes, the user is soft-deactivated in Seekra (cannot log in, tokens rejected).
- Audit trail shows `SCIM_USER_CREATED` then `SCIM_USER_DEACTIVATED`.

### Phase 5 — Multi-IdP support (Week 3)

**Scope:**
- Allow multiple `sso_providers` rows per tenant (already supported in the schema; just need UI changes).
- `/login` page shows all active providers as separate buttons.
- User picks one; subsequent logins can use any provider (the user's email links them — if same email appears in two IdPs, both logins resolve to the same Seekra user).
- Per-provider provisioning config (defaults) — already in schema.

**Acceptance criteria:**
- Admin configures two providers: Azure AD (for employees) + Google Workspace (for contractors).
- Both buttons appear on `/login`.
- Employee logs in via Azure AD → provisioned with employee defaults.
- Contractor logs in via Google → provisioned with contractor defaults (e.g. lower clearance).
- Same email in both IdPs → same Seekra user, whichever IdP they log in via.

### Phase 6 — Single Logout + session bridging (Week 3, stretch)

**Scope:**
- On Seekra logout: redirect to IdP's `end_session_endpoint` with the Seekra `id_token` to trigger IdP logout.
- IdP logout completes → redirects back to Seekra `/login?logout=1` → Seekra clears its JWT cookie.
- Optional (configurable per provider): skip IdP logout (some IdPs don't support it cleanly).
- Frontend: "Sign out" button respects this — if user logged in via SSO, sign-out also kills the IdP session.

**Acceptance criteria:**
- User logs in via Azure AD, uses Seekra, clicks "Sign out".
- Browser redirects to Microsoft logout, then back to Seekra login page.
- User clicks "Sign in with Azure AD" again — must re-authenticate (no SSO shortcut).
- Configurable: admin can disable IdP logout per provider (Seekra-only logout, IdP session persists).

## 6. Security considerations

- **State parameter**: the `state` param in OIDC flow MUST be a random nonce stored in Redis (10-min TTL) and validated on callback. Prevents CSRF.
- **PKCE**: implement Proof Key for Code Exchange (RFC 7636) for the OIDC flow — defense in depth, even for confidential clients.
- **JWKS caching**: cache IdP's JWKS in Redis for 1 hour; refresh on signature-verification failure.
- **Client secret encryption**: AES-256 at rest with per-tenant key (same as Brief #32 connector secrets).
- **No PII in logs**: SSO claims (email, groups) must not appear in audit event details unless explicitly required (configurable per tenant).
- **Break-glass admin**: every tenant must have at least one local-password admin (enforced at provider-creation time — if you try to deactivate the last non-SSO admin, block with 400).
- **Token lifetime**: Seekra JWT lifetime unchanged (existing `ACCESS_TOKEN_EXPIRE_MINUTES = 480`). SSO id_token is only used at login, not stored.

## 7. Out of scope (future briefs)

- SAML 2.0 support (for AD FS on-prem customers).
- LDAP bind authentication (legacy).
- Multi-factor enforcement inside Seekra (IdP's job).
- OIDC dynamic client registration (we configure clients manually).
- Cross-tenant SSO (a user from tenant A logging into tenant B).

## 8. Testing

- Unit tests for `verify_id_token` (use a mock JWKS).
- Unit tests for group mapping reconciliation (diff logic).
- Integration tests with a real Keycloak instance (run in docker-compose for tests).
- Mock Azure AD using `responses` library for SCIM endpoint tests.
- UAT script: configure Keycloak as IdP, log in, verify provisioning, group mapping, offboard.

## 9. Documentation

- Update `AGENTS.md` with the SSO provider model.
- Update `GOVERNANCE.md` with new audit event types.
- Update demo run book with "Section 10: SSO + SCIM" demo step (log in via Azure AD, show group mapping, offboard via SCIM).

---

**End of Brief #33.**
