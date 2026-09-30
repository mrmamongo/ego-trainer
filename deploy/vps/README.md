# Cogito VPS deployment

This Compose project runs the Ego Trainer server as `cogito-server` under the project name `cogito`. The release procedure builds an image on the VPS from the public release archive and supplies its immutable tag; Compose consumes that pre-built image and has no `build` section. The only host-published application port is `127.0.0.1:18081`. Traefik reaches the service over the separate `cogito_proxy` Docker network.

The content checkout at `/opt/cogito/content` is writable because Task Studio edits canonical files there. The SQLite database and content checkout are separate bind mounts. Both directories must be writable by container UID/GID `10001:10001`.

## Create the deployment directory

```sh
sudo install -d -m 0750 -o 10001 -g 10001 /opt/cogito/data /opt/cogito/content
sudo install -d -m 0700 -o root -g root /opt/cogito/backups
sudo install -m 0600 -o root -g root /dev/null /opt/cogito/.env
sudoedit /opt/cogito/.env
```

Start with this private environment file. Replace the image tag with the immutable tag or digest supplied for this release, and generate a new independent JWT secret for the VPS. Keep secrets out of Git, shell transcripts, support messages, and screenshots.

```dotenv
COGITO_IMAGE=registry.example.invalid/ego-trainer:IMMUTABLE_RELEASE_TAG
EGO_JWT_SECRET=REPLACE_WITH_AT_LEAST_32_RANDOM_CHARACTERS
EGO_SETTINGS_ENCRYPTION_KEY=REPLACE_WITH_FRESH_FERNET_KEY
EGO_LOCAL_AUTH_ENABLED=true
EGO_FORGEJO_ENABLED=false
EGO_REGISTRATION_ENABLED=false
```

Generate a JWT secret on the VPS with `openssl rand -hex 32`. At initial setup, also generate a separate Fernet key for `EGO_SETTINGS_ENCRYPTION_KEY` with `python3 -c 'import base64,secrets; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())'`. Put both in `.env` using a private editor. Do not reuse or copy the pilot JWT secret or settings-encryption key. Keep this VPS-only Fernet key stable for the life of the VPS data; changing it later makes previously encrypted service settings unreadable. Keep `.env` mode `0600` and owned by root.

The Compose file fixes these production values: database `/var/lib/ego/ego.db`, task content `/content`, public URL `https://cogito.born-in-july.ru`, allowed hosts including the internal `cogito-server` host used by Traefik ForwardAuth, and an empty CORS origin list. Registration is environment-locked off by default, including when the database contains a previously saved `registration_enabled=true` value. Local password login remains enabled while Forgejo is disabled.

## Fresh VPS state and initial content

This deployment intentionally starts with an independent, empty VPS database. Do not transfer the local pilot SQLite database, users, progress, admin chats, service settings, external identity links, JWT secret, and settings-encryption key. Keep the local pilot unchanged. The first administrator and all later VPS accounts are created independently on the VPS.

Before the first start, ensure `/opt/cogito/data/ego.db` does not exist and populate `/opt/cogito/content` only from the deployment-authorized task source supplied for this server. The container syncs that mounted local catalog during startup. Remote Git clone/update automation is not included yet; that remains tracked by `ego-trainer-8di.2`.

```sh
sudo test ! -e /opt/cogito/data/ego.db
sudo chown -R 10001:10001 /opt/cogito/data /opt/cogito/content
```

Do not use the local pilot database as a seed. After startup, check the newly created VPS database:

```sh
sudo docker compose --project-directory /opt/cogito -f /opt/cogito/compose.yaml exec -T cogito-server python -c 'import sqlite3; print(sqlite3.connect("/var/lib/ego/ego.db").execute("PRAGMA integrity_check").fetchone()[0])'
```

The result must be `ok`. Confirm that the catalog contains only the task material authorized for this deployment.

## Start and inspect the service

Run Compose with the project directory and file path explicit so relative bind mounts always resolve under `/opt/cogito`:

```sh
sudo docker compose --project-directory /opt/cogito -f /opt/cogito/compose.yaml config --quiet
sudo docker compose --project-directory /opt/cogito -f /opt/cogito/compose.yaml up -d
sudo docker compose --project-directory /opt/cogito -f /opt/cogito/compose.yaml ps
sudo docker compose --project-directory /opt/cogito -f /opt/cogito/compose.yaml logs --tail=100 cogito-server
curl --fail http://127.0.0.1:18081/health
```

Because the VPS starts with a fresh database, create the first administrator through the trusted container CLI. Use an operator-generated password and do not commit or record it in this README:

```sh
sudo docker compose --project-directory /opt/cogito -f /opt/cogito/compose.yaml exec cogito-server ego-server admin create-user --username <admin-name> --password <strong-password> --role admin
```

The public registration endpoint is disabled. After the first administrator signs in, accounts can be managed from the admin panel; the first mentor role still requires the trusted server CLI per the role policy.

## Traefik v3.2 file-provider integration

This VPS uses Traefik's **file provider**, not the Docker provider. Do not add Docker labels or mount the Docker socket. The Traefik container and `cogito-server` must share the Compose network `cogito_proxy`.

After Compose creates the network, connect the existing `kad-traefik` container without recreating it:

```sh
sudo docker network connect cogito_proxy kad-traefik
sudo docker network inspect cogito_proxy
```

The router, service, and middlewares belong in the existing `/opt/kad-arbitr/traefik/dynamic.yml`, using entrypoint `websecure` and TLS resolver `letsencrypt`. The API router must have higher priority than the general browser router and match segment-bounded paths only:

```yaml
http:
  routers:
    cogito-api:
      rule: >-
        Host(`cogito.born-in-july.ru`) &&
        (Path(`/auth/me`) ||
         (Path(`/auth/providers`) && HeaderRegexp(`Authorization`, `(?i)^Bearer\s+.+`)) ||
         Path(`/admin`) || PathPrefix(`/admin/`) ||
         Path(`/tasks`) || PathPrefix(`/tasks/`) ||
         Path(`/progress`) || PathPrefix(`/progress/`) ||
         Path(`/check`) || PathPrefix(`/check/`))
      entryPoints: [websecure]
      middlewares: [cogito-jwt]
      service: cogito
      priority: 100
      tls:
        certResolver: letsencrypt
    cogito-browser:
      rule: Host(`cogito.born-in-july.ru`)
      entryPoints: [websecure]
      service: cogito
      priority: 1
      tls:
        certResolver: letsencrypt
  middlewares:
    cogito-jwt:
      forwardAuth:
        address: http://cogito-server:8000/auth/me
        trustForwardHeader: false
        authRequestHeaders:
          - Authorization
  services:
    cogito:
      loadBalancer:
        servers:
          - url: http://cogito-server:8000
```

The browser router has no authentication middleware: HTTPS exposes the login page, static files, health endpoint, and login/OAuth entry points. Keep new account registration disabled. Every protected application API route uses the higher-priority `cogito-jwt` ForwardAuth router, which sends only the Bearer `Authorization` header to `/auth/me` and forwards the request only after Ego verifies the current account and role. The unauthenticated `/auth/providers` lookup falls through to the browser router so the login page can show configured providers. The app port remains bound to `127.0.0.1:18081`; browser and API clients use the public HTTPS hostname rather than exposing that port.

The existing Traefik `dynamic.yml` is mounted as one file with watching enabled. Update that file **in place** so the container's bind mount keeps the same inode; replacing it atomically with a rename can leave the container watching the old file. Check Traefik logs for the loaded `cogito` router, ForwardAuth middleware, service, and TLS configuration. If `kad-traefik` is recreated, reconnect it to `cogito_proxy`; network attachments do not survive container recreation.

## Forgejo later

Forgejo login is disabled by default. A Forgejo personal access token is not an OAuth client secret. When the Forgejo OAuth application is ready, add its **OAuth client ID and client secret** privately to `/opt/cogito/.env`, set `EGO_FORGEJO_ENABLED=true`, keep the exact public callback origin, and—only after the real-provider smoke passes—set `EGO_LOCAL_AUTH_ENABLED=false`. Register this exact callback URI in Forgejo:

```text
https://cogito.born-in-july.ru/auth/forgejo/callback
```

Keep new account registration closed unless an operator intentionally opens it. First mentor bootstrap and explicit linking of existing pilot identities remain trusted CLI operations. See [FORGEJO_AUTH.md](../../docs/FORGEJO_AUTH.md) for the OAuth contract and rollout checks.

## Backups and recovery

Back up the new VPS SQLite database with SQLite's backup API and back up its content checkout from the same recovery point. Store those backups, the VPS `.env`, and the private Traefik `dynamic.yml` in a private backup location with restrictive access; encrypt off-host copies. Test restore into separate directories before replacing live VPS data. Do not mix these backups with the local pilot snapshot.
