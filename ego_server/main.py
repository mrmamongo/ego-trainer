"""Ego server — FastAPI application."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from ego_server import __version__
from ego_server.config import settings
from ego_server.db import init_db
from ego_server.routers import auth, check, progress, tasks
from ego_server.routers import admin as admin_router


_STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Ego Server",
    version=__version__,
    description="Platform for practice tasks: catalog, progress, auth.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
app.include_router(progress.router, prefix="/progress", tags=["progress"])
app.include_router(check.router, prefix="/check", tags=["check"])
app.include_router(admin_router.router, prefix="/admin", tags=["admin"])


@app.get("/health", tags=["meta"])
async def health() -> dict:
    return {"status": "ok", "version": __version__}


# === Admin panel (static HTML + JS) ===


@app.get("/admin", include_in_schema=False)
async def admin_panel_root() -> FileResponse:
    """Serve the mentor admin panel at /admin (no trailing slash)."""
    return FileResponse(_STATIC_DIR / "admin.html")


@app.get("/admin/", include_in_schema=False)
async def admin_panel() -> FileResponse:
    """Serve the mentor admin panel."""
    return FileResponse(_STATIC_DIR / "admin.html")


app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")
