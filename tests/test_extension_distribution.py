"""Extension distribution: GET /extension/latest, /extension/download, CLI publish.

The endpoints are public (no JWT): a new student installs the extension
before having an account. Nothing outside ``EGO_EXTENSION_DIR`` may ever be
served, and the CLI reads the version from ``extension/package.json`` inside
the ``.vsix`` zip, refuses older versions without ``--force`` and replaces
``latest.json`` atomically.
"""

from __future__ import annotations

import hashlib
import importlib
import json
import zipfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


def make_vsix(path: Path, version: str, *, payload: bytes = b"vsix-body") -> Path:
    """Write a minimal .vsix (zip with ``extension/package.json``)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "extension/package.json",
            json.dumps({"name": "ego-trainer", "version": version}),
        )
        archive.writestr("extension.vsixmanifest", "<PackageManifest/>")
        archive.writestr("extension/out/extension.cjs", payload)
    return path


@pytest.fixture
def extension_env(monkeypatch, tmp_path):
    """Temp DB + temp EGO_EXTENSION_DIR; reloads the app so routes read them."""
    db_path = tmp_path / "data" / "test.db"
    ext_dir = tmp_path / "ext"
    ext_dir.mkdir()
    monkeypatch.setenv("EGO_DB_PATH", str(db_path))
    monkeypatch.setenv("EGO_EXTENSION_DIR", str(ext_dir))

    import ego_server.config

    importlib.reload(ego_server.config)

    import ego_server.main

    importlib.reload(ego_server.main)
    return ext_dir


@pytest.fixture
def client(extension_env):
    from ego_server.main import app

    with TestClient(app) as test_client:
        yield test_client


# === GET /extension/latest ===


def test_latest_404_when_nothing_published(client):
    response = client.get("/extension/latest")
    assert response.status_code == 404
    detail = response.json()["detail"]
    assert "not published" in detail
    assert "latest.json" in detail


def test_latest_does_not_require_auth(client):
    # No Authorization header: still the same contract, not 401.
    assert client.get("/extension/latest").status_code == 404


def test_latest_200_after_publish(client, extension_env):
    from ego_server.cli import main as cli_main

    vsix = make_vsix(extension_env.parent / "incoming" / "cogito-0.2.0.vsix", "0.2.0")
    assert cli_main(["admin", "publish-extension", "--vsix", str(vsix)]) == 0

    response = client.get("/extension/latest")
    assert response.status_code == 200
    data = response.json()
    assert data["version"] == "0.2.0"
    assert data["sha256"] == hashlib.sha256(vsix.read_bytes()).hexdigest()
    assert data["size"] == vsix.stat().st_size
    assert data["download_url"] == "/extension/download"
    assert data["published_at"]
    assert data["notes"] is None
    assert "file" not in data  # the file name stays a server-side detail


def test_latest_leaks_no_file_name(client, extension_env):
    from ego_server.cli import main as cli_main

    vsix = make_vsix(extension_env.parent / "cogito-0.3.0.vsix", "0.3.0")
    cli_main(["admin", "publish-extension", "--vsix", str(vsix), "--notes", "Новые подсказки"])
    data = client.get("/extension/latest").json()
    assert data["notes"] == "Новые подсказки"


def test_latest_500_on_corrupt_latest_json(client, extension_env):
    (extension_env / "latest.json").write_text("{not json", encoding="utf-8")
    response = client.get("/extension/latest")
    assert response.status_code == 500
    assert "invalid" in response.json()["detail"]


# === GET /extension/download ===


def test_download_404_when_nothing_published(client):
    response = client.get("/extension/download")
    assert response.status_code == 404
    assert "not published" in response.json()["detail"]


def test_download_serves_published_vsix_with_headers(client, extension_env):
    from ego_server.cli import main as cli_main

    vsix = make_vsix(extension_env.parent / "cogito-0.2.0.vsix", "0.2.0")
    cli_main(["admin", "publish-extension", "--vsix", str(vsix)])

    response = client.get("/extension/download")
    assert response.status_code == 200
    assert response.content == vsix.read_bytes()
    assert response.headers["content-type"] == "application/octet-stream"
    assert response.headers["cache-control"] == "no-store"
    assert 'filename="cogito-0.2.0.vsix"' in response.headers["content-disposition"]

    latest = client.get("/extension/latest").json()
    assert hashlib.sha256(response.content).hexdigest() == latest["sha256"]
    assert len(response.content) == latest["size"]


def test_download_missing_file_is_404(client, extension_env):
    from ego_server.extension_dist import vsix_file_name

    (extension_env / "latest.json").write_text(
        json.dumps(
            {
                "version": "0.2.0",
                "sha256": "0" * 64,
                "file": vsix_file_name("0.2.0"),
                "size": 10,
                "published_at": "2026-01-01T00:00:00+00:00",
            }
        ),
        encoding="utf-8",
    )
    response = client.get("/extension/download")
    assert response.status_code == 404
    assert "missing" in response.json()["detail"]


@pytest.mark.parametrize(
    "bad_file",
    [
        "../secret.vsix",
        "../../etc/passwd",
        "..\\secret.vsix",
        "/etc/passwd",
        "sub/secret.vsix",
        "C:\\secret.vsix",
        "",
        ".",
        "..",
    ],
)
def test_download_rejects_path_traversal_in_latest_json(client, extension_env, bad_file):
    (extension_env.parent / "secret.vsix").write_bytes(b"secret-outside-dir")
    (extension_env / "latest.json").write_text(
        json.dumps(
            {
                "version": "0.2.0",
                "sha256": "0" * 64,
                "file": bad_file,
                "size": 10,
                "published_at": "2026-01-01T00:00:00+00:00",
            }
        ),
        encoding="utf-8",
    )
    for url in ("/extension/download", "/extension/latest"):
        response = client.get(url)
        assert response.status_code == 500, url
        assert b"secret-outside-dir" not in response.content
        assert "plain file name" in response.json()["detail"]


def test_download_rejects_symlink_escaping_extension_dir(client, extension_env):
    outside = extension_env.parent / "outside.vsix"
    outside.write_bytes(b"outside")
    link = extension_env / "cogito-0.2.0.vsix"
    try:
        link.symlink_to(outside)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks are not available for this user")
    (extension_env / "latest.json").write_text(
        json.dumps(
            {
                "version": "0.2.0",
                "sha256": "0" * 64,
                "file": "cogito-0.2.0.vsix",
                "size": 7,
                "published_at": "2026-01-01T00:00:00+00:00",
            }
        ),
        encoding="utf-8",
    )
    response = client.get("/extension/download")
    assert response.status_code != 200
    assert b"outside" not in response.content


# === CLI admin publish-extension ===


def _read_latest(ext_dir: Path) -> dict:
    return json.loads((ext_dir / "latest.json").read_text(encoding="utf-8"))


def test_cli_publish_reads_version_from_vsix(extension_env, capsys):
    from ego_server.cli import main

    # The file name deliberately disagrees with the version inside the zip.
    vsix = make_vsix(extension_env.parent / "cogito-9.9.9.vsix", "0.2.0")
    assert main(["admin", "publish-extension", "--vsix", str(vsix)]) == 0

    out = capsys.readouterr().out
    assert out.count("\n") == 1
    assert "Published 0.2.0" in out
    assert "sha256" in out

    published = extension_env / "cogito-0.2.0.vsix"
    assert published.is_file()
    assert published.read_bytes() == vsix.read_bytes()

    latest = _read_latest(extension_env)
    assert latest == {
        "version": "0.2.0",
        "sha256": hashlib.sha256(vsix.read_bytes()).hexdigest(),
        "file": "cogito-0.2.0.vsix",
        "size": vsix.stat().st_size,
        "published_at": latest["published_at"],
    }
    assert latest["published_at"].endswith("+00:00")
    # Atomic write leaves no temp files behind.
    assert sorted(p.name for p in extension_env.iterdir()) == [
        "cogito-0.2.0.vsix",
        "latest.json",
    ]


def test_cli_publish_copies_and_overwrites_file(extension_env):
    from ego_server.cli import main

    first = make_vsix(extension_env.parent / "a.vsix", "0.2.0", payload=b"one")
    second = make_vsix(extension_env.parent / "b.vsix", "0.2.1", payload=b"two")
    assert main(["admin", "publish-extension", "--vsix", str(first)]) == 0
    assert main(["admin", "publish-extension", "--vsix", str(second)]) == 0
    assert (extension_env / "cogito-0.2.1.vsix").read_bytes() == second.read_bytes()
    assert _read_latest(extension_env)["version"] == "0.2.1"


def test_cli_refuses_not_newer_version(extension_env, capsys):
    from ego_server.cli import main

    newer = make_vsix(extension_env.parent / "new.vsix", "0.3.0")
    same = make_vsix(extension_env.parent / "same.vsix", "0.3.0")
    older = make_vsix(extension_env.parent / "old.vsix", "0.2.9")
    assert main(["admin", "publish-extension", "--vsix", str(newer)]) == 0
    before = _read_latest(extension_env)
    capsys.readouterr()

    assert main(["admin", "publish-extension", "--vsix", str(older)]) == 1
    assert "not newer" in capsys.readouterr().err
    assert main(["admin", "publish-extension", "--vsix", str(same)]) == 1
    assert "not newer" in capsys.readouterr().err

    # Nothing changed on disk.
    assert _read_latest(extension_env) == before
    assert not (extension_env / "cogito-0.2.9.vsix").exists()


def test_cli_force_publishes_older_version(extension_env, capsys):
    from ego_server.cli import main

    newer = make_vsix(extension_env.parent / "new.vsix", "0.3.0")
    older = make_vsix(extension_env.parent / "old.vsix", "0.2.9")
    main(["admin", "publish-extension", "--vsix", str(newer)])
    capsys.readouterr()

    assert main(["admin", "publish-extension", "--vsix", str(older), "--force"]) == 0
    assert "Published 0.2.9 (was 0.3.0)" in capsys.readouterr().out
    assert _read_latest(extension_env)["version"] == "0.2.9"
    assert (extension_env / "cogito-0.2.9.vsix").is_file()


def test_cli_force_republishes_same_version(extension_env, capsys):
    from ego_server.cli import main

    vsix = make_vsix(extension_env.parent / "v.vsix", "0.2.0")
    main(["admin", "publish-extension", "--vsix", str(vsix)])
    capsys.readouterr()
    assert main(["admin", "publish-extension", "--vsix", str(vsix), "--force"]) == 0
    assert "Published 0.2.0 (was 0.2.0)" in capsys.readouterr().out


def test_cli_publish_rejects_non_zip(extension_env, capsys):
    from ego_server.cli import main

    bogus = extension_env.parent / "bogus.vsix"
    bogus.write_bytes(b"not a zip")
    assert main(["admin", "publish-extension", "--vsix", str(bogus)]) == 1
    assert "not a valid .vsix" in capsys.readouterr().err
    assert not (extension_env / "latest.json").exists()


def test_cli_publish_rejects_missing_vsix(extension_env, capsys):
    from ego_server.cli import main

    assert main(["admin", "publish-extension", "--vsix", str(extension_env.parent / "nope.vsix")]) == 1
    assert "not found" in capsys.readouterr().err


def test_cli_publish_rejects_invalid_version(extension_env, capsys):
    from ego_server.cli import main

    vsix = make_vsix(extension_env.parent / "bad.vsix", "not-a-version")
    assert main(["admin", "publish-extension", "--vsix", str(vsix)]) == 1
    assert "invalid extension version" in capsys.readouterr().err


def test_extension_dir_defaults_next_to_db(monkeypatch, tmp_path):
    import ego_server.config

    monkeypatch.delenv("EGO_EXTENSION_DIR", raising=False)
    monkeypatch.setenv("EGO_DB_PATH", str(tmp_path / "state" / "ego.db"))
    try:
        importlib.reload(ego_server.config)
        from ego_server.extension_dist import extension_dir

        assert extension_dir(ego_server.config.settings) == tmp_path / "state" / "extension"
    finally:
        monkeypatch.delenv("EGO_DB_PATH", raising=False)
        monkeypatch.delenv("EGO_EXTENSION_DIR", raising=False)
        importlib.reload(ego_server.config)


# === SemVer ordering used by the CLI ===


@pytest.mark.parametrize(
    ("candidate", "current", "expected"),
    [
        ("0.2.0", "0.1.9", True),
        ("0.2.0", "0.2.0", False),
        ("0.1.9", "0.2.0", False),
        ("1.0.0", "0.99.99", True),
        ("0.2.0-beta.1", "0.2.0", False),
        ("0.2.0", "0.2.0-beta.1", True),
        ("0.2.0-beta.2", "0.2.0-beta.10", False),
        ("0.2.0+build.1", "0.2.0", False),
        ("0.2.0", None, True),
        ("garbage", None, False),
        ("garbage", "0.1.0", False),
    ],
)
def test_is_newer_semver(candidate, current, expected):
    from ego_server.extension_dist import is_newer

    assert is_newer(candidate, current) is expected


# === Student page block ===


def test_student_page_has_extension_block(client):
    response = client.get("/student")
    assert response.status_code == 200
    assert 'id="extension-download"' in response.text
    assert "Расширение для VS Code" in response.text
    assert 'id="extension-link"' in response.text
    assert "/extension/latest" in client.get("/static/student.js").text
