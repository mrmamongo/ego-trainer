"""OAuth discovery and task tools against isolated Ego DB/content."""

import asyncio
import importlib
import time
from urllib.parse import urlencode

import httpx
import jwt
import pytest
from fastmcp import Client
from fastmcp.server.auth import AccessToken
from fastmcp.server.auth.oauth_proxy.models import JTIMapping, UpstreamTokenSet
from fastmcp.server.dependencies import get_access_token
from starlette.testclient import TestClient

from ego_server import auth, config, content_config, db, task_mcp
from ego_server.sync import sync_from_path


@pytest.fixture
def env(tmp_path, monkeypatch):
    root = tmp_path / "content"
    folder = root / "projects/p1/folders/f1"
    folder.mkdir(parents=True)
    (root / "catalog.yaml").write_text(
        "schema_version: 1\nprojects:\n- id: p1\n  path: projects/p1\n", encoding="utf-8"
    )
    (root / "projects/p1/project.yaml").write_text(
        "id: p1\nname: P1\nversion_policy: declare\n", encoding="utf-8"
    )
    (folder / "folder.yaml").write_text("id: f1\ncode: F\nname: Basics\n", encoding="utf-8")
    md = folder / "task_f1.md"
    md.write_text(
        "---\nid: F1\ntitle: Answer\nversion: 1.0.0\n---\n"
        "# Задача F1: Answer\n\n## Условие\nReturn 42.\n",
        encoding="utf-8",
    )
    (folder / "task_f1.solution.py").write_text("def task_f1():\n    return 42\n", encoding="utf-8")
    (folder / "task_f1.tests.py").write_text(
        "from ego.testing import case\n"
        "@case(args=(), expected=42, level='smoke')\ndef task_f1():\n    ...\n",
        encoding="utf-8",
    )
    settings = config.Settings(
        _env_file=None,
        environment="test",
        db_path=tmp_path / "ego.db",
        forgejo_enabled=True,
        forgejo_url="https://git.example.com",
        forgejo_client_id="browser-client",
        forgejo_client_secret="browser-secret",
        public_url="http://localhost",
        mcp_enabled=True,
        mcp_forgejo_client_id="mcp-client",
        mcp_forgejo_client_secret="mcp-private-secret",
        mcp_signing_key="test-signing-key-" + "x" * 64,
        mcp_storage_path=tmp_path / "auth-store",
    )
    for module in (config, db, auth, task_mcp):
        monkeypatch.setattr(module, "settings", settings)
    monkeypatch.setattr(
        content_config,
        "content_settings",
        content_config.ContentSettings(_env_file=None, repo_url=str(root)),
    )
    db.init_db()
    conn = db.get_connection()
    sync = sync_from_path(conn, root)
    assert sync.errors == 0
    conn.execute(
        "INSERT INTO students(id,username,role,password_hash,created_at) "
        "VALUES ('u1','teacher','admin','',datetime('now'))"
    )
    conn.execute(
        "INSERT INTO external_identities(issuer,subject,user_id,remote_username,created_at) "
        "VALUES ('https://git.example.com','42','u1','teacher',datetime('now'))"
    )
    conn.commit()
    conn.close()
    token = AccessToken(
        token="upstream-secret",
        client_id="mcp-client",
        scopes=["openid", "profile"],
        claims={"forgejo_issuer": "https://git.example.com", "forgejo_subject": "42"},
    )
    monkeypatch.setattr(task_mcp, "get_access_token", lambda: token)
    from ego_server import main

    importlib.reload(main)
    with TestClient(main.app, base_url="http://localhost") as client:
        yield main._task_mcp, client, settings, md, token


def run_tool(server, name, args=None):
    async def run():
        async with Client(server) as client:
            return await client.call_tool(name, args or {})

    return asyncio.run(run()).data


def candidate(task):
    return {
        "task_id": "F1",
        "expected_version": task["version"],
        "expected_content_etag": task["content_etag"],
        "markdown": task["markdown"]
        .replace("version: 1.0.0", "version: 1.0.1")
        .replace("Return 42.", "Return the integer 42."),
        "solution_py": task["solution_py"],
        "tests_py": task["tests_py"],
    }


def test_oauth_discovery_and_unauthenticated_transport(env):
    server, client, _, _, _ = env
    response = client.post("/mcp", json={"jsonrpc": "2.0", "id": 1, "method": "initialize"})
    assert response.status_code == 401
    assert "resource_metadata=" in response.headers["www-authenticate"]
    metadata = client.get("/.well-known/oauth-protected-resource/mcp").json()
    assert metadata["resource"] == "http://localhost/mcp"
    authorization = client.get("/.well-known/oauth-authorization-server").json()
    assert authorization["issuer"].rstrip("/") == "http://localhost"
    assert authorization["code_challenge_methods_supported"] == ["S256"]
    assert client.get("/health").status_code == 200
    assert client.get("/mcp-callback?state=unknown&code=code").status_code == 400
    assert asyncio.run(server.auth.verify_token("upstream-secret")) is None


def test_dcr_and_consent_do_not_expose_upstream_credentials(env):
    _, client, settings, _, _ = env
    response = client.post(
        "/register",
        json={
            "client_name": "Test author",
            "redirect_uris": ["http://localhost:4567/callback"],
            "grant_types": ["authorization_code", "refresh_token"],
            "response_types": ["code"],
            "token_endpoint_auth_method": "none",
        },
    )
    assert response.status_code == 201, response.text
    assert settings.mcp_forgejo_client_secret not in response.text
    info = response.json()
    params = {
        "client_id": info["client_id"],
        "redirect_uri": info["redirect_uris"][0],
        "response_type": "code",
        "code_challenge": "x" * 43,
        "code_challenge_method": "S256",
        "state": "client-state",
        "resource": "http://localhost/mcp",
        "scope": "openid profile",
    }
    authorized = client.get("/authorize?" + urlencode(params), follow_redirects=False)
    assert authorized.status_code == 302
    assert "/consent" in authorized.headers["location"]
    consent = client.get(authorized.headers["location"])
    assert consent.status_code == 200
    assert settings.mcp_forgejo_client_secret not in consent.text
    assert (
        client.post(
            "/register",
            json={
                "redirect_uris": ["javascript:alert(1)"],
            },
        ).status_code
        >= 400
    )


def test_identity_requires_verified_subject_and_current_linked_role(env):
    _, _, _, _, _ = env
    profile = {"sub": "42", "preferred_username": "teacher", "is_admin": True}
    calls = []

    def upstream(request):
        calls.append(request)
        return httpx.Response(200, json=profile)

    verifier = task_mcp.ForgejoVerifier(
        "https://git.example.com", transport=httpx.MockTransport(upstream)
    )
    valid = asyncio.run(verifier.verify_token("opaque-upstream-token"))
    assert valid.claims["forgejo_subject"] == "42"
    assert calls[0].url == "https://git.example.com/login/oauth/userinfo"
    profile["sub"] = "999"  # matching username/admin claim must not link an account
    assert asyncio.run(verifier.verify_token("opaque-upstream-token")) is None
    profile["sub"] = "42"
    conn = db.get_connection()
    conn.execute("UPDATE students SET role='student' WHERE id='u1'")
    conn.commit()
    conn.close()
    assert asyncio.run(verifier.verify_token("opaque-upstream-token")) is None


def test_edit_validate_save_and_stale_etag(env):
    server, _, _, md, _ = env
    task = run_tool(server, "get_task", {"task_id": "F1"})
    assert task["writable"] and task["content_etag"]
    before = md.read_bytes()
    proposed = candidate(task)
    validated = run_tool(server, "validate_task", proposed)
    assert validated["valid"] and validated["candidate_version"] == "1.0.1"
    assert md.read_bytes() == before
    saved = run_tool(server, "save_task", proposed)
    assert saved["new_version"] == "1.0.1"
    assert saved["content_etag"] != task["content_etag"]
    after = md.read_bytes()
    with pytest.raises(Exception, match="409"):
        run_tool(server, "save_task", proposed)
    assert md.read_bytes() == after


def test_current_role_and_identity_rechecked_before_each_tool(env):
    server, _, _, _, _ = env
    assert run_tool(server, "whoami")["can_save_tasks"]
    task = run_tool(server, "get_task", {"task_id": "F1"})
    conn = db.get_connection()
    conn.execute("UPDATE students SET role='mentor' WHERE id='u1'")
    conn.commit()
    assert run_tool(server, "get_task", {"task_id": "F1"})["task_id"] == "F1"
    with pytest.raises(Exception, match="does not permit"):
        run_tool(server, "save_task", candidate(task))
    conn.execute("DELETE FROM external_identities WHERE subject='42'")
    conn.commit()
    conn.close()
    with pytest.raises(Exception, match="does not permit"):
        run_tool(server, "whoami")


def test_oauth_mcp_keys_must_be_separate():
    settings = config.Settings(
        _env_file=None,
        forgejo_enabled=True,
        forgejo_client_id="b",
        forgejo_client_secret="bs",
        public_url="https://cogito.example.com",
        mcp_enabled=True,
        mcp_forgejo_client_id="m",
        mcp_forgejo_client_secret="ms",
        mcp_signing_key="short",
    )
    with pytest.raises(RuntimeError, match="43 random"):
        config.validate_runtime_settings(settings)
    settings.mcp_signing_key = "x" * 64
    settings.jwt_secret = settings.mcp_signing_key
    with pytest.raises(RuntimeError, match="separate"):
        config.validate_runtime_settings(settings)


def test_http_bearer_is_bound_to_mcp_and_upstream_identity(env, monkeypatch):
    server, client, settings, _, _ = env
    proxy = server.auth
    monkeypatch.setattr(task_mcp, "get_access_token", get_access_token)
    proxy._token_validator.transport = httpx.MockTransport(
        lambda request: httpx.Response(200, json={"sub": "42"})
    )

    async def store_tokens():
        now = time.time()
        await proxy._upstream_token_store.put(
            key="test-upstream",
            value=UpstreamTokenSet(
                upstream_token_id="test-upstream",
                access_token="opaque-upstream-secret",
                refresh_token=None,
                refresh_token_expires_at=None,
                expires_at=now + 3600,
                token_type="Bearer",
                scope="openid profile",
                client_id="test-client",
                created_at=now,
            ),
            ttl=3600,
        )
        await proxy._jti_mapping_store.put(
            key="test-jti",
            value=JTIMapping(
                jti="test-jti",
                upstream_token_id="test-upstream",
                created_at=now,
            ),
            ttl=3600,
        )

    asyncio.run(store_tokens())
    bearer = proxy.jwt_issuer.issue_access_token(
        client_id="test-client",
        scopes=["openid", "profile"],
        jti="test-jti",
    )
    body = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": "whoami", "arguments": {}},
    }

    def post(token):
        return client.post(
            "/mcp",
            json=body,
            headers={
                "Authorization": "Bearer " + token,
                "Accept": "application/json, text/event-stream",
            },
        )

    response = post(bearer)
    assert response.status_code == 200
    assert '"can_save_tasks":true' in response.text
    claims = jwt.decode(bearer, options={"verify_signature": False})
    claims["aud"] = "https://another-service.example/mcp"
    other_audience = jwt.encode(claims, proxy.jwt_issuer._signing_key, algorithm="HS256")
    assert post(other_audience).status_code == 401
    assert post("opaque-upstream-secret").status_code == 401
    for path in settings.mcp_storage_path.rglob("*"):
        if path.is_file():
            assert b"opaque-upstream-secret" not in path.read_bytes()
    conn = db.get_connection()
    conn.execute("DELETE FROM external_identities WHERE subject='42'")
    conn.commit()
    conn.close()
    assert post(bearer).status_code == 401
