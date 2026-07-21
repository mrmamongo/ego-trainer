"""Ego server — FastAPI application."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ego_server import __version__
from ego_server.config import settings
from ego_server.db import init_db
from ego_server.routers import auth, check, progress, tasks
from ego_server.routers import admin as admin_router


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
