# Dockerfile for ego-server — FastAPI + SQLite (MVP).
# See ADR-0001 D7 (FastAPI + SQLite for MVP), D13 (three entry-points).
#
# Build:  docker build -t ego-server .
# Run:    docker run -p 8000:8000 -v ego-data:/app/.ego-server ego-server
#
# The server reads docs/tasks/ from the repo (git canonical, D2).
# SQLite DB is stored in /app/.ego-server/ego.db (mounted as a volume).

FROM python:3.11-slim AS base

# Prevent Python from writing .pyc files and buffering stdout/stderr.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install build dependencies (for bcrypt etc.), then clean up.
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy project files.
COPY pyproject.toml README.md ./
COPY ego/ ego/
COPY ego_server/ ego_server/
COPY ego_tui/ ego_tui/
COPY docs/tasks/ docs/tasks/

# Install the package with server + dev extras.
RUN pip install -e ".[server,dev]"

# Create data directory for SQLite.
RUN mkdir -p /app/.ego-server

# Expose the FastAPI port.
EXPOSE 8000

# Environment defaults (override at runtime).
ENV EGO_DB_PATH=/app/.ego-server/ego.db \
    EGO_JWT_SECRET=change-me-in-production

# Health check via /health endpoint.
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run: migrate schema, import tasks, start uvicorn.
CMD ["sh", "-c", "ego-server migrate && ego-server admin import-tasks --docs-dir docs/tasks && exec uvicorn ego_server.main:app --host 0.0.0.0 --port 8000"]
