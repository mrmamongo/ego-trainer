# Shared Cogito MCP

Endpoint: `https://cogito.born-in-july.ru/mcp` (Streamable HTTP).
Clients discover OAuth metadata, register dynamically, and authorize in the
browser through Forgejo. No shared admin API key is distributed to models.

Existing linked Ego accounts with `mentor` or `admin` roles can connect.
The server maps the verified Forgejo issuer/subject to the existing account;
it never grants privileges from a username. Role and identity changes are
checked on requests and on every tool invocation. Only admins can validate
or publish edits, matching Task Studio's REST permissions.

## Tools and editing

`whoami`, `get_catalog`, `get_task`, `list_students`,
`get_student_progress`, `get_student_understanding`, `validate_task`, `save_task`.

`get_student_understanding` returns defense status and student evidence for a
checked solution/version. It does not expose code snapshots, balances or keys.
Keep passing tests and confirmed understanding distinct; neither establishes
long-term or global mastery.

Read `cogito://task-authoring` before editing. Get the full canonical task and
its version/etag, propose the three-file candidate, validate, then save when
the teacher requests publication. `save_task` immediately replaces canonical
files and synchronizes metadata. A 409 means reread and review concurrent
changes; never silently override them. Validation checks structure and syntax;
it does not execute the curriculum tests. This release edits existing tasks.

The live source is the mounted `/opt/cogito/content` directory, not a Git
checkout. Saving does not create a Git commit or push. Student progress remains
in Ego's database. The VS Code extension keeps its existing browser Forgejo
login and Ego JWT; MCP tokens are separate.

## Deployment

Install `.[server,mcp]`; Docker includes both extras. MCP is disabled by default.
Register a separate confidential Forgejo OAuth application with callback
`https://cogito.born-in-july.ru/mcp-callback` and configure private environment:

```dotenv
EGO_MCP_ENABLED=true
EGO_MCP_FORGEJO_CLIENT_ID=<separate Forgejo application ID>
EGO_MCP_FORGEJO_CLIENT_SECRET=<application secret>
EGO_MCP_SIGNING_KEY=<at least 43 random characters, distinct from other keys>
EGO_MCP_STORAGE_PATH=/var/lib/ego/mcp-auth
```

Keep `/var/lib/ego` persistent and restrict the environment file to the
operator. The MCP store encrypts upstream credentials; back it up together
with its signing key, keep the key stable across restarts, and treat backups
as secrets. Rotating the key requires clients to authorize again.
Existing `EGO_FORGEJO_*` browser integration must remain enabled/configured.

Route `/mcp`, `/.well-known/*`, `/authorize`, `/consent`, `/register`, `/token`,
and `/mcp-callback` directly to Cogito over HTTPS. These routes use MCP OAuth;
do not place the Ego JWT ForwardAuth middleware in front of them. Preserve it
on the existing REST routes. Production host allowlists and HTTPS are required.

Verify health, discovery, unauthenticated MCP 401, dynamic registration and
browser consent. The final browser authorization requires the user's Forgejo
session. Keep the previous immutable Docker image/environment for rollback.
