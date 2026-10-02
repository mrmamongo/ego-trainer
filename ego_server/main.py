"""Ego server — FastAPI application."""

from contextlib import AsyncExitStack, asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from ego_server import __version__
from ego_server.config import settings, validate_runtime_settings
from ego_server.db import init_db
from ego_server.routers import ai as ai_router
from ego_server.routers import admin as admin_router
from ego_server.routers import (
    admin_settings,
    auth,
    check,
    forgejo_auth,
    progress,
    tasks,
)

_STATIC_DIR = Path(__file__).parent / "static"
_mcp_http_app = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    validate_runtime_settings(settings)
    init_db()
    async with AsyncExitStack() as stack:
        if _mcp_http_app is not None:
            await stack.enter_async_context(_mcp_http_app.lifespan(_mcp_http_app))
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
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(forgejo_auth.router, prefix="/auth", tags=["auth"])
app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
app.include_router(progress.router, prefix="/progress", tags=["progress"])
app.include_router(check.router, prefix="/check", tags=["check"])
app.include_router(ai_router.router, prefix="/ai", tags=["ai"])
app.include_router(ai_router.admin_router, prefix="/admin/ai", tags=["ai-admin"])
app.include_router(admin_router.router, prefix="/admin", tags=["admin"])
app.include_router(admin_settings.router, prefix="/admin", tags=["admin-settings"])


@app.exception_handler(RequestValidationError)
async def safe_validation_error(request, exc: RequestValidationError):
    # Never echo passwords or provider keys in validation responses.
    details = [
        {k: v for k, v in error.items() if k not in {"input", "ctx"}} for error in exc.errors()
    ]
    return JSONResponse(status_code=422, content=jsonable_encoder({"detail": details}))


@app.get("/health", tags=["meta"])
async def health() -> dict:
    return {"status": "ok", "version": __version__}


# === Admin panel (static HTML + JS) ===


@app.get("/", include_in_schema=False)
async def admin_panel_root() -> FileResponse:
    """Serve the mentor admin panel at the site root."""
    return FileResponse(_STATIC_DIR / "admin.html")


@app.get("/student", include_in_schema=False)
@app.get("/student/", include_in_schema=False)
async def student_panel() -> FileResponse:
    return FileResponse(_STATIC_DIR / "student.html", headers={"Cache-Control": "no-store"})


@app.get("/student/tasks/{task_id:path}", include_in_schema=False)
async def student_task_page(task_id: str) -> FileResponse:
    """Serve bookmarkable task pages; task data keeps its authenticated API boundary."""
    return FileResponse(_STATIC_DIR / "student.html", headers={"Cache-Control": "no-store"})


@app.get("/favicon.ico", include_in_schema=False)
async def favicon() -> FileResponse:
    return FileResponse(_STATIC_DIR / "branding" / "favicon.ico", media_type="image/x-icon")


app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")

if settings.mcp_enabled:
    # Mount last: normal Ego routes keep their routing/auth contracts. The
    # subapp owns /mcp and its OAuth discovery, consent and token endpoints.
    from ego_server.task_mcp import create_task_mcp

    _task_mcp = create_task_mcp(app)
    _mcp_http_app = _task_mcp.http_app(
        path="/mcp", stateless_http=True, allowed_hosts=settings.allowed_hosts
    )
    app.mount("/", _mcp_http_app)
