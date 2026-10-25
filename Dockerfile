# Dockerfile for ego-server — FastAPI + SQLite (MVP).
# See ADR-0001 D7 (FastAPI + SQLite for MVP), D13 (three entry-points).
#
# Build:  docker build -t ego-server:0.1.0 .
# Run via docker-compose.yml with EGO_JWT_SECRET and EGO_CONTENT_PATH set.
#
# Canonical task content is mounted at /content; it is never baked into the
# image. SQLite is stored in /var/lib/ego/ego.db on a persistent volume.
#
# Stages:
#   web     admin-ui build (Node): /panel bundle, theme, /ide bundle -> /static
#   builder Python wheel; receives the full ego_server/static/admin/ output
#   runtime Python 3.11 runtime image

# === Web assets: mentor/admin panel (/panel) and browser IDE (/ide) ===
# Pinned Node LTS major (20) matches admin-ui/package.json requirements.
FROM node:20-slim AS web

WORKDIR /web

# Dependencies first so source-only changes reuse the npm layer.
COPY admin-ui/package.json admin-ui/package-lock.json ./
RUN npm ci --no-audit --no-fund

# Sources: everything except node_modules and the build's own scratch output.
COPY admin-ui/build.mjs ./
COPY admin-ui/src ./src

# The icon is referenced by the admin login page from /static/branding.
COPY ego_server/static/branding /static/branding

# build.mjs resolves its output as ../ego_server/static/admin relative to
# /web, i.e. /ego_server/static/admin. The committed generated files (tracked
# on purpose) are the baseline, so a git-only build context still starts from
# them; the build then overwrites them in place.
COPY ego_server/static/admin /ego_server/static/admin

# Builds bundle.js/css, theme.css, ide.js/css, workers/ and assets/; fails if
# a shell asset the HTML pages load was not emitted.
RUN npm run build \
    && for f in bundle.js bundle.css theme.css ide.js ide.css workers/editor.worker.js; do \
         test -s "/ego_server/static/admin/$f" \
           || { echo "missing admin/$f" >&2; exit 1; }; \
       done

FROM python:3.11-slim AS builder

# Prevent Python from writing .pyc files and buffering stdout/stderr.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

# Install wheel build dependencies, then clean apt metadata in the same layer.
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only package sources needed to build the wheel.
COPY pyproject.toml README.md ./
COPY ego/ ego/
COPY ego_server/ ego_server/
COPY ego_tui/ ego_tui/

# Ship the built panel/IDE assets: replace ego_server/static/admin entirely so
# the wheel holds exactly what the web stage produced (no stale files).
RUN rm -rf ego_server/static/admin
COPY --from=web /ego_server/static/admin/ ego_server/static/admin/

# Build the application and all runtime dependencies as wheels. Development
# tools and canonical task solutions are deliberately absent from the image.
RUN pip wheel --wheel-dir /wheels ".[server,mcp,collab]"

FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    EGO_ENVIRONMENT=production \
    EGO_DB_PATH=/var/lib/ego/ego.db \
    EGO_TASKS_REPO_URL=/content \
    EGO_BIND_HOST=0.0.0.0 \
    EGO_BIND_PORT=8000 \
    EGO_UVICORN_WORKERS=1 \
    EGO_COLLAB_ENABLED=true

RUN groupadd --gid 10001 ego \
    && useradd --uid 10001 --gid 10001 --no-create-home --shell /usr/sbin/nologin ego \
    && mkdir -p /var/lib/ego /content /var/lib/ego/incoming \
    && chown -R ego:ego /var/lib/ego /content

COPY --from=builder /wheels /wheels
RUN pip install --no-index --find-links=/wheels "ego-trainer[server,mcp,collab]" \
    && rm -rf /wheels

# Expose the FastAPI port.
EXPOSE 8000

VOLUME ["/var/lib/ego"]

USER 10001:10001

# Health check via /health endpoint.
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run: validate production config, migrate, sync mounted content, exec Uvicorn.
CMD ["python", "-m", "ego_server.entrypoint"]
