"""Server-only settings for the tutor and the independent response reviewer."""

import json
from decimal import Decimal

from fastapi import HTTPException
from pydantic import BaseModel, Field, SecretStr, field_validator


class ModelSettings(BaseModel):
    base_url: str = ""
    model: str = ""
    api_key: SecretStr = SecretStr("")
    input_usd_per_million: Decimal = Field(default=Decimal("0"), ge=0)
    output_usd_per_million: Decimal = Field(default=Decimal("0"), ge=0)
    max_output_tokens: int = Field(default=1024, ge=128, le=4096)
    json_mode: bool = True

    @field_validator("base_url")
    @classmethod
    def validate_url(cls, value):
        from ego_server.service_settings import ConsoleSettings

        return ConsoleSettings.provider_url(value)


class AISettings(BaseModel):
    enabled: bool = False
    main: ModelSettings = Field(default_factory=ModelSettings)
    guard: ModelSettings = Field(default_factory=lambda: ModelSettings(max_output_tokens=256))
    timeout_seconds: float = Field(default=45, ge=1, le=120)
    max_context_bytes: int = Field(default=48000, ge=8000, le=128000)
    max_reply_bytes: int = Field(default=12000, ge=1000, le=32000)
    max_turns: int = Field(default=20, ge=6, le=40)

    @property
    def ready(self) -> bool:
        return self.enabled and all(
            model.base_url.startswith(("https://", "http://")) and model.model
            for model in (self.main, self.guard)
        )


def _cipher():
    from ego_server.service_settings import _cipher as settings_cipher

    try:
        return settings_cipher()
    except (ValueError, TypeError) as exc:
        raise HTTPException(503, "Некорректный ключ шифрования настроек сервера") from exc


def public_settings(db) -> dict:
    row = db.execute("SELECT * FROM ai_settings WHERE id = 1").fetchone()
    data = json.loads(row["settings_json"]) if row else AISettings().model_dump(mode="json")
    for name in ("main", "guard"):
        data[name].pop("api_key", None)
        data[name]["api_key_set"] = bool(row and row[name + "_key"])
    return data


def get_settings(db) -> AISettings:
    row = db.execute("SELECT * FROM ai_settings WHERE id = 1").fetchone()
    if not row:
        return AISettings()
    settings = AISettings.model_validate_json(row["settings_json"])
    for name in ("main", "guard"):
        encrypted = row[name + "_key"]
        if encrypted:
            from cryptography.fernet import InvalidToken

            try:
                getattr(settings, name).api_key = SecretStr(
                    _cipher().decrypt(encrypted.encode()).decode()
                )
            except InvalidToken as exc:
                raise HTTPException(503, "Не удалось расшифровать конфигурацию моделей") from exc
    return settings


def save_settings(db, settings: AISettings) -> dict:
    old = db.execute("SELECT * FROM ai_settings WHERE id = 1").fetchone()
    keys = {}
    for name in ("main", "guard"):
        model = getattr(settings, name)
        if "api_key" in model.model_fields_set:
            key = model.api_key.get_secret_value()
            keys[name] = _cipher().encrypt(key.encode()).decode() if key else ""
        else:
            keys[name] = old[name + "_key"] if old else ""
    config = settings.model_dump(mode="json", exclude={"main": {"api_key"}, "guard": {"api_key"}})
    db.execute(
        """INSERT INTO ai_settings VALUES (1, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET settings_json = excluded.settings_json,
        main_key = excluded.main_key, guard_key = excluded.guard_key""",
        (json.dumps(config), keys["main"], keys["guard"]),
    )
    db.commit()
    return public_settings(db)
