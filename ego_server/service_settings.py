"""Validated, versioned administration settings shared by all server workers."""

from __future__ import annotations

import base64
import json
import sqlite3
from datetime import datetime, timezone
from urllib.parse import urlsplit
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ConsoleSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    service_name: str = Field(default="Ego Trainer", min_length=1, max_length=80)
    registration_enabled: bool = True
    session_minutes: int = Field(default=10080, ge=15, le=43200)
    check_timeout_seconds: float = Field(default=5, ge=1, le=30)
    max_code_chars: int = Field(default=100000, ge=1000, le=500000)
    content_path: str = Field(default="", max_length=1000)
    ai_enabled: bool = False
    ai_base_url: str = Field(default="", max_length=1000)
    ai_model: str = Field(default="", max_length=160)
    ai_temperature: float | None = Field(default=None, ge=0, le=2)
    ai_token_limit_parameter: Literal["max_tokens", "max_completion_tokens"] = "max_tokens"
    ai_max_tokens: int = Field(default=4096, ge=256, le=16384)
    ai_timeout_seconds: int = Field(default=90, ge=5, le=180)
    ai_tools_enabled: bool = True
    ai_system_prompt: str = Field(default="", max_length=8000)

    @field_validator("service_name", "ai_model", "content_path", mode="before")
    @classmethod
    def trim(cls, value: str) -> str:
        return value.strip() if isinstance(value, str) else value

    @field_validator("ai_base_url")
    @classmethod
    def provider_url(cls, value: str) -> str:
        value = value.strip().rstrip("/")
        if not value:
            return value
        parsed = urlsplit(value)
        if (
            parsed.scheme not in {"http", "https"}
            or not parsed.hostname
            or parsed.username
            or parsed.password
            or parsed.query
            or parsed.fragment
        ):
            raise ValueError("Use an http(s) API base URL without credentials, query or fragment")
        if parsed.hostname in {"169.254.169.254", "metadata.google.internal"}:
            raise ValueError("Cloud metadata endpoints cannot be used as AI providers")
        return value


class SettingsUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    expected_revision: int = Field(ge=0)
    config: ConsoleSettings
    api_key: str | None = Field(default=None, max_length=20000, repr=False)
    clear_api_key: bool = False


class SettingsConflict(ValueError):
    pass


_ENV_FIELDS = {
    "service_name": "service_name",
    "registration_enabled": "registration_enabled",
    "session_minutes": "jwt_expire_minutes",
    "check_timeout_seconds": "check_timeout_seconds",
    "max_code_chars": "max_code_chars",
    "ai_enabled": "ai_enabled",
    "ai_base_url": "ai_base_url",
    "ai_model": "ai_model",
}


def _defaults() -> ConsoleSettings:
    from ego_server import config, content_config

    values = {name: getattr(config.settings, env_name) for name, env_name in _ENV_FIELDS.items()}
    values["content_path"] = content_config.content_settings.to_config().url
    if (
        config.settings.environment == "production"
        and "registration_enabled" not in config.settings.model_fields_set
    ):
        values["registration_enabled"] = False
    return ConsoleSettings(**values)


def _record(db: sqlite3.Connection) -> sqlite3.Row | None:
    try:
        return db.execute("SELECT * FROM service_settings WHERE id = 1").fetchone()
    except sqlite3.OperationalError as exc:
        if "no such table" not in str(exc):
            raise
        return None


def locked_fields() -> dict[str, str]:
    from ego_server import config, content_config

    locked = {
        name: "EGO_" + source.upper()
        for name, source in _ENV_FIELDS.items()
        if source in config.settings.model_fields_set
    }
    if "repo_url" in content_config.content_settings.model_fields_set:
        locked["content_path"] = "EGO_TASKS_REPO_URL"
    if "ai_api_key" in config.settings.model_fields_set:
        locked["api_key"] = "EGO_AI_API_KEY"
    return locked


def load_settings(db: sqlite3.Connection) -> ConsoleSettings:
    defaults = _defaults()
    row = _record(db)
    values = defaults.model_dump()
    if row:
        values.update(json.loads(row["config_json"]))
    for name in locked_fields():
        if name in values:
            values[name] = getattr(defaults, name)
    return ConsoleSettings.model_validate(values)


def _cipher():
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.hkdf import HKDF
    from ego_server import config

    if config.settings.settings_encryption_key:
        return Fernet(config.settings.settings_encryption_key.encode())
    key = HKDF(
        algorithm=hashes.SHA256(), length=32, salt=None, info=b"ego-admin-settings-v1"
    ).derive(config.settings.jwt_secret.encode())
    return Fernet(base64.urlsafe_b64encode(key))


def provider_key(db: sqlite3.Connection) -> str:
    from cryptography.fernet import InvalidToken
    from ego_server import config

    if "ai_api_key" in config.settings.model_fields_set:
        return config.settings.ai_api_key
    row = _record(db)
    if not row or not row["api_key_encrypted"]:
        return ""
    try:
        return _cipher().decrypt(row["api_key_encrypted"].encode()).decode()
    except InvalidToken as exc:
        raise ValueError("AI key cannot be decrypted after a key rotation; enter it again") from exc


def settings_snapshot(db: sqlite3.Connection) -> dict:
    from ego_server import __version__, config

    row = _record(db)
    key_error = ""
    try:
        key_set = bool(provider_key(db))
    except ValueError as exc:
        key_set = False
        key_error = str(exc)
    runtime = config.settings
    return {
        "revision": row["revision"] if row else 0,
        "config": load_settings(db).model_dump(),
        "api_key_configured": key_set,
        "api_key_error": key_error,
        "locked_fields": locked_fields(),
        "updated_at": row["updated_at"] if row else None,
        "runtime": {
            "version": __version__,
            "environment": runtime.environment,
            "db_path": str(runtime.db_path),
            "bind_host": runtime.bind_host,
            "bind_port": runtime.bind_port,
            "workers": runtime.uvicorn_workers,
            "allowed_hosts": runtime.allowed_hosts,
            "cors_origins": runtime.cors_origins,
            "jwt_secret_configured": len(runtime.jwt_secret) >= 32,
        },
    }


def save_settings(db: sqlite3.Connection, update: SettingsUpdate, actor_id: str) -> dict:
    current = load_settings(db)
    for field, variable in locked_fields().items():
        if field == "api_key":
            if update.api_key is not None or update.clear_api_key:
                raise ValueError(f"AI key is managed by {variable}")
        elif getattr(update.config, field) != getattr(current, field):
            raise ValueError(f"{field} is managed by {variable}")
    if update.config.content_path:
        from ego_server.content_config import TasksRepoConfig

        path = TasksRepoConfig(url=update.config.content_path).resolved_local_path
        if not path.is_dir():
            raise ValueError("Content path must be an existing directory on the server")
    if update.api_key is not None and update.clear_api_key:
        raise ValueError("Choose a new API key or clear it, not both")
    encrypted = None
    if update.api_key is not None:
        encrypted = _cipher().encrypt(update.api_key.strip().encode()).decode()
    now = datetime.now(timezone.utc).isoformat()
    db.execute("BEGIN IMMEDIATE")
    try:
        row = _record(db)
        revision = row["revision"] if row else 0
        if revision != update.expected_revision:
            raise SettingsConflict("Settings changed in another window; reload before saving")
        key = row["api_key_encrypted"] if row else ""
        if update.clear_api_key:
            key = ""
        elif encrypted is not None:
            key = encrypted
        db.execute(
            "INSERT INTO service_settings (id, revision, config_json, api_key_encrypted, "
            "updated_at, updated_by) VALUES (1, ?, ?, ?, ?, ?) ON CONFLICT(id) DO UPDATE SET "
            "revision=excluded.revision, config_json=excluded.config_json, "
            "api_key_encrypted=excluded.api_key_encrypted, updated_at=excluded.updated_at, "
            "updated_by=excluded.updated_by",
            (revision + 1, update.config.model_dump_json(), key, now, actor_id),
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
    return settings_snapshot(db)


def effective_content_config(db: sqlite3.Connection):
    from ego_server.content_config import content_settings

    current = content_settings.to_config()
    return current.model_copy(update={"url": load_settings(db).content_path})


def deployment_env(db: sqlite3.Connection) -> str:
    snapshot = settings_snapshot(db)
    runtime = snapshot["runtime"]
    lines = [
        "# Docker Compose environment. Add secrets, then restart the service.",
        "EGO_BIND_ADDRESS=127.0.0.1",
        f"EGO_PORT={runtime['bind_port']}",
        "EGO_JWT_SECRET=<set-a-random-secret-of-at-least-32-characters>",
        "EGO_CONTENT_PATH=<absolute-host-path-to-your-content-checkout>",
        f"EGO_ALLOWED_HOSTS={json.dumps(runtime['allowed_hosts'])}",
        f"EGO_CORS_ORIGINS={json.dumps(runtime['cors_origins'])}",
        f"EGO_UVICORN_WORKERS={runtime['workers']}",
    ]
    return "\n".join(lines) + "\n"
