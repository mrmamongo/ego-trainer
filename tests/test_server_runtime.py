"""Production runtime configuration and static-entrypoint tests."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from ego_server.config import Settings, validate_runtime_settings


def test_production_rejects_default_jwt_secret() -> None:
    config = Settings(
        environment="production",
        jwt_secret="dev-secret-change-in-production",
        allowed_hosts=["localhost"],
        cors_origins=["http://localhost:8000"],
    )
    with pytest.raises(RuntimeError, match="EGO_JWT_SECRET"):
        validate_runtime_settings(config)


def test_production_rejects_wildcard_hosts_and_cors() -> None:
    base = {
        "environment": "production",
        "jwt_secret": "a-secure-production-secret-with-32-chars",
    }
    with pytest.raises(RuntimeError, match="EGO_ALLOWED_HOSTS"):
        validate_runtime_settings(Settings(**base, allowed_hosts=["*"]))
    with pytest.raises(RuntimeError, match="EGO_CORS_ORIGINS"):
        validate_runtime_settings(Settings(**base, allowed_hosts=["localhost"], cors_origins=["*"]))


def test_production_accepts_explicit_runtime_settings() -> None:
    validate_runtime_settings(
        Settings(
            environment="production",
            jwt_secret="a-secure-production-secret-with-32-chars",
            allowed_hosts=["localhost"],
            cors_origins=["https://ego.example.com"],
        )
    )


def test_admin_ui_is_only_at_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("ego_server.config.settings.db_path", tmp_path / "runtime.db")
    from ego_server.main import app

    with TestClient(app, base_url="http://testserver") as client:
        root = client.get("/")
        assert root.status_code == 200
        assert "Cogito — Панель управления" in root.text
        assert "/static/admin/bundle.js" in root.text

        assert client.get("/admin", follow_redirects=False).status_code == 404
        student = client.get("/student")
        assert student.status_code == 200
        assert "/static/student.js" in student.text
        assert "forgejo-login" in student.text
        assert client.get("/student/").status_code == 200
