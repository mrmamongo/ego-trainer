# Private pilot deployment

This guide covers a private, single-server pilot using Docker Compose, a local
mounted task catalog and the admin console. It is not a public deployment
guide.

## Security boundary

Bind the service to loopback or a trusted private network and limit access to
the pilot group. Do not publish it on the public internet. Student submissions
run as subprocesses; the current sandbox does not provide hardened OS-level
isolation. Public launch is blocked by Beads issue `ego-trainer-41s`.

The example Compose configuration binds to `127.0.0.1` by default. If access
from another machine is required, put the service behind a private VPN or a
trusted access gateway, set explicit allowed hosts and browser origins, and
keep the service off public interfaces.

## Prerequisites

- Docker Engine with Docker Compose v2 (`docker compose`).
- A private platform checkout containing `Dockerfile` and
  `docker-compose.yml`.
- A disposable local catalog checkout/copy. The container mounts this
  directory read-write so reviewed Task Studio edits can be saved.
- A secret manager or another secure way to generate and store secrets.

Run the following commands from the platform repository root, where the
Compose file lives.

## Configure secrets and content

Create `.env` in the repository root. Do not commit it:

```dotenv
EGO_JWT_SECRET=<random-secret-at-least-32-characters>
EGO_SETTINGS_ENCRYPTION_KEY=<Fernet-key>
EGO_CONTENT_PATH=/absolute/path/to/disposable-task-catalog
EGO_BIND_ADDRESS=127.0.0.1
EGO_PORT=8000
```

Generate a JWT secret with a cryptographically secure random generator. The
encryption key must be a valid Fernet key. For example, in an environment with
the project's Python dependencies installed:

```sh
python -c "import secrets; print(secrets.token_urlsafe(48))"
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Store both values securely and keep a protected backup. `EGO_JWT_SECRET` is
required in production mode; Compose fails if it is missing, and the server
rejects a default or shorter-than-32-character JWT secret.

`EGO_CONTENT_PATH` is the host directory mounted at `/content` inside the
container. It should contain the catalog layout (`catalog.yaml`,
`projects/<project>/project.yaml`, and folder/task files). The mount is
read-write for Task Studio, so use a working copy when you do not want pilot
edits to change a curated source checkout.

The Compose service sets `EGO_TASKS_REPO_URL=/content`. That makes the content
path deployment-controlled and locked in the Settings UI. To change the host
catalog directory, update `EGO_CONTENT_PATH` and recreate the service.

## Start the server and create an administrator

```sh
docker compose up -d --build
docker compose ps
docker compose logs -f ego-server
```

Wait for the health check, then create the first administrator through the
container CLI. Choose a unique password and avoid saving it in shell history
where that is a concern:

```sh
docker compose exec ego-server ego-server admin create-user \
  --username admin --password '<unique-strong-password>' --role admin
```

Open the admin console at <http://127.0.0.1:8000/>. Swagger is at
<http://127.0.0.1:8000/docs>; health is at
<http://127.0.0.1:8000/health>.

Registration is disabled by default in production. Create pilot accounts
through the admin console or CLI; enable registration only if the pilot needs it. Create additional mentor accounts through the user
management interface or the CLI; do not rely on public self-registration to
grant privileged roles.

## Load and maintain the local catalog

The server reads the mounted catalog at `/content`. After placing or updating
catalog files in the host directory, run a manual sync:

```sh
docker compose exec ego-server ego-server admin sync-tasks --from /content
```

Check the admin overview for the latest sync result and any task errors. Keep
the catalog directory and SQLite data volume in separate backups.

Remote Git checkout, authentication and cron-based sync are not implemented
(`ego-trainer-8di.2`). A local mount and explicit manual sync are the current
pilot path.

## Configure service settings and AI

Sign in as an administrator and open **Settings**. Operational values stored
in the database can be applied live when the UI does not mark them as
environment-locked. This includes the service display name, registration
policy, session duration, checker limits, AI enablement, provider URL/model,
AI response limits/timeouts, tools policy and system prompt.

For an OpenAI-compatible provider, enter:

- **Base URL:** the provider API base, typically ending in `/v1`, such as
  `https://api.openai.com/v1`. Do not append `/chat/completions`.
- **Model:** the exact model identifier accepted by that provider.
- **API key:** the provider credential. The UI stores it encrypted and does
  not return its value in settings responses. Use the connection check before
  enabling the assistant.

An explicit `EGO_AI_API_KEY` environment variable locks the key to deployment
configuration. Otherwise, an administrator can set or replace it in the UI.
Do not put provider credentials in URLs, task files, prompts or source control.

The AI assistant can read the service/catalog context and prepare settings or
task-content proposals. It does not directly apply changes. Review the
proposal in the relevant Settings or Task Studio screen, validate it where
available, then use the explicit Save action to write it.

## Live settings and restart-required configuration

The Settings screen identifies values supplied by the environment as locked.
Database-backed operational settings apply without restarting the container
unless their corresponding environment variable is set.

Infrastructure and secret values are configured outside the live admin UI.
Update the Compose environment and recreate the service for changes to:

- `EGO_JWT_SECRET` and `EGO_SETTINGS_ENCRYPTION_KEY`;
- `EGO_DB_PATH` and the persistent database volume;
- host port/bind address, allowed hosts, CORS origins and worker count;
- `EGO_CONTENT_PATH` or the container mount layout;
- any environment variable that locks an operational setting, including
  `EGO_SERVICE_NAME`, `EGO_REGISTRATION_ENABLED`,
  `EGO_JWT_EXPIRE_MINUTES`, `EGO_CHECK_TIMEOUT_SECONDS`,
  `EGO_MAX_CODE_CHARS`, `EGO_AI_ENABLED`, `EGO_AI_BASE_URL`,
  `EGO_AI_MODEL` and `EGO_AI_API_KEY`.

After updating `.env`, recreate the server container:

```sh
docker compose up -d --force-recreate ego-server
```

The Compose variables `EGO_BIND_ADDRESS`, `EGO_PORT`, `EGO_ALLOWED_HOSTS`,
`EGO_CORS_ORIGINS`, `EGO_UVICORN_WORKERS` and `EGO_CONTENT_PATH` configure
the container boundary/mount. Environment-driven UI fields may be locked;
the UI's lock label names the controlling variable.

## JWT and encrypted AI-key rotation

The provider key is encrypted in SQLite with Fernet. When
`EGO_SETTINGS_ENCRYPTION_KEY` is set, it is the encryption master key. Keep it
stable and back it up separately from the database. Rotating only
`EGO_JWT_SECRET` then invalidates existing login tokens but does not prevent
decrypting the stored AI key.

If no dedicated encryption key is configured, the encryption key is derived
from `EGO_JWT_SECRET`. Rotating the JWT secret in that mode invalidates login
tokens and makes the stored AI key undecryptable; enter the provider key again
in Settings after restart. Changing `EGO_SETTINGS_ENCRYPTION_KEY` also makes
the existing encrypted key undecryptable. The application does not re-encrypt
it automatically; configure the new master key, restart, then enter the
provider key again.

Back up the SQLite volume, mounted catalog, JWT secret and encryption master
key as separate protected items. Restore the matching master key with the DB
backup before enabling AI.

## Operations and limitations

```sh
docker compose logs -f ego-server
docker compose ps
docker compose down
```

The named `ego-data` volume stores SQLite data and survives a normal
`docker compose down`. `docker compose down -v` deletes that volume and its
database; use it only when intentionally resetting the pilot.

This setup is a private pilot, not a production-readiness claim. Hardened
subprocess isolation is still required before public launch (`ego-trainer-41s`)
and remote content-repository sync/cron remain open (`ego-trainer-8di.2`).
