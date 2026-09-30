"""Admin-only configuration interface. Provider secrets never leave the server."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse

from ego_server.deps import DbDep, require_role
from ego_server.service_settings import (
    SettingsConflict,
    SettingsUpdate,
    deployment_env,
    save_settings,
    settings_snapshot,
)

router = APIRouter()
Admin = Annotated[dict, Depends(require_role("admin"))]


@router.get("/settings")
def read_settings(db: DbDep, user: Admin) -> dict:
    return settings_snapshot(db)


@router.put("/settings")
def write_settings(body: SettingsUpdate, db: DbDep, user: Admin) -> dict:
    try:
        return save_settings(db, body, user["sub"])
    except SettingsConflict as exc:
        raise HTTPException(409, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc


@router.get("/settings/deployment", response_class=PlainTextResponse)
def export_deployment(db: DbDep, user: Admin) -> str:
    return deployment_env(db)
