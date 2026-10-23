# Cogito: Forgejo-only login and dashboard theme repair

Published to `https://cogito.born-in-july.ru/` on 2026-10-23.
Tracking: `ego-trainer-hg8`.

The deployed `/auth/providers` advertised both Forgejo and local authentication,
with registration open. The dashboard used Tailwind components but its HTML did
not load the existing `/static/admin/theme.css`. This reproduced as missing theme
variables, Times New Roman text and native browser buttons.

The release connects the existing theme before component CSS, uses its background
variables, and serves the dashboard HTML with `Cache-Control: no-store`.
Production now sets `EGO_LOCAL_AUTH_ENABLED=false`; Forgejo and registration for
new Forgejo identities remain enabled. Existing guards reject password login,
password registration, administrative password-account creation and password reset.
Development password-auth code and existing account records are retained.

## Release boundary

The deployed image is `ego-trainer:auth-theme-20261023`. It derives from the exact
previous running image, `ego-trainer:vstart-b638972`, image ID
`sha256:18a673150d60c1c36f7d4d513b843dc600b42313ced108d6eed44ad009356736`.
Only the installed `ego_server/static/admin.html` and `ego_server/main.py` were
patched. Existing JS/CSS assets were preserved. This was not a deployment of the
local checkout, which contains unrelated uncommitted work.

Only `COGITO_IMAGE` and `EGO_LOCAL_AUTH_ENABLED` changed in the private deployment
environment. The existing Compose file, data/content mounts and other services
were preserved. A linked Forgejo administrator was verified before switching.

## Verification

- 60 local tests passed: dashboard shell, Forgejo OAuth and local-auth contracts.
- A candidate with no network and a separate SQLite/MCP storage copy passed 12
  HTTP checks. The same 12 checks passed after switching the live container.
- Password login, registration, admin account creation and reset returned 403.
  Authenticated admin overview returned 200; anonymous access returned 401.
- Student page, IDE page, theme asset and health returned 200.
- Before/after row hashes matched for all existing students (14), external
  identities (3), progress records (43), runs (66) and task records (119).
- The public browser login showed only Forgejo, zero password inputs, the expected
  sans-serif font, `--background: #09090b`, and no JavaScript console errors.
  A new interactive Forgejo login and authenticated dashboard navigation were not
  repeated; OAuth flow behavior is covered by the existing contract tests.

## Recovery

Private backups, image metadata and candidate/live verification reports are in
`/opt/cogito/releases/auth-theme-20261023`. A fresh SQLite backup was made immediately
before switching. To roll back, restore the saved environment configuration and
recreate only `cogito-server` with the existing Compose file. No schema migration
or data restoration is required for this change. Restoring the previous environment
also restores password authentication, so prefer keeping the new auth flag when
rolling back only the theme repair.
