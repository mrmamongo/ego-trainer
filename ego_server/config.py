"""Server configuration — env vars with safe development defaults."""

from pathlib import Path
from typing import Literal
from pydantic import Field

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="EGO_", env_file=".env", extra="ignore")

    environment: Literal["development", "test", "production"] = "development"
    db_path: Path = Path(".ego-server/ego.db")
    jwt_secret: str = "dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7  # 7 days
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:8000"]
    allowed_hosts: list[str] = ["localhost", "127.0.0.1", "testserver"]
    bind_host: str = "0.0.0.0"
    bind_port: int = 8000
    uvicorn_workers: int = 1
    log_truncated_to: int = 8 * 1024  # 8KB max log per run
    service_name: str = "Ego Trainer"
    registration_enabled: bool = True
    check_timeout_seconds: float = 5
    max_code_chars: int = 100000
    ai_enabled: bool = False
    ai_base_url: str = ""
    ai_model: str = ""
    ai_api_key: str = Field(default="", repr=False)
    settings_encryption_key: str = Field(default="", repr=False)


_INSECURE_JWT_SECRETS = {
    "",
    "change-me-in-production",
    "dev-secret-change-in-production",
}


def validate_runtime_settings(config: Settings) -> None:
    """Reject development-only settings when running in production mode."""
    if config.environment != "production":
        return
    if config.jwt_secret in _INSECURE_JWT_SECRETS or len(config.jwt_secret) < 32:
        raise RuntimeError(
            "EGO_JWT_SECRET must be a non-default secret of at least 32 characters "
            "when EGO_ENVIRONMENT=production"
        )
    if not config.allowed_hosts or "*" in config.allowed_hosts:
        raise RuntimeError("EGO_ALLOWED_HOSTS must contain explicit hosts in production")
    if "*" in config.cors_origins:
        raise RuntimeError("EGO_CORS_ORIGINS must contain explicit origins in production")


settings = Settings()
