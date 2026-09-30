# Dockerfile for ego-server — FastAPI + SQLite (MVP).
# See ADR-0001 D7 (FastAPI + SQLite for MVP), D13 (three entry-points).
#
# Build:  docker build -t ego-server:0.1.0 .
# Run via docker-compose.yml with EGO_JWT_SECRET and EGO_CONTENT_PATH set.
#
# Canonical task content is mounted at /content; it is never baked into the
# image. SQLite is stored in /var/lib/ego/ego.db on a persistent volume.

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

# Build the application and all runtime dependencies as wheels. Development
# tools and canonical task solutions are deliberately absent from the image.
RUN pip wheel --wheel-dir /wheels ".[server,mcp]"

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
    EGO_UVICORN_WORKERS=1

RUN groupadd --gid 10001 ego \
    && useradd --uid 10001 --gid 10001 --no-create-home --shell /usr/sbin/nologin ego \
    && mkdir -p /var/lib/ego /content \
    && chown -R ego:ego /var/lib/ego /content

COPY --from=builder /wheels /wheels
RUN pip install --no-index --find-links=/wheels "ego-trainer[server,mcp]" \
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
