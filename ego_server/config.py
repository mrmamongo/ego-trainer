"""Server configuration — env vars with sensible defaults."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="EGO_", env_file=".env", extra="ignore")

    db_path: Path = Path(".ego-server/ego.db")
    jwt_secret: str = "dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7  # 7 days
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:8000"]
    log_truncated_to: int = 8 * 1024  # 8KB max log per run


settings = Settings()
