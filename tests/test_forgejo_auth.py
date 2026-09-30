"""OAuth contract, identity continuity, replay protection and role boundaries."""

import re
import secrets
from datetime import datetime
from urllib.parse import parse_qs, urlsplit

import httpx
import pytest
from fastapi.testclient import TestClient

from ego_server import auth, config, db, forgejo


@pytest.fixture
def setup(tmp_path, monkeypatch):
    settings = config.Settings(
        _env_file=None,
        db_path=tmp_path / "oauth.db",
        environment="test",
        forgejo_enabled=True,
        forgejo_client_id="client",
        forgejo_client_secret="private-secret",
        public_url="http://127.0.0.1",
        forgejo_url="https://git.born-in-july.ru",
    )
    monkeypatch.setattr(config, "settings", settings)
    monkeypatch.setattr(db, "settings", settings)
    monkeypatch.setattr(auth, "settings", settings)
    profile = {"sub": "42", "preferred_username": "alice", "is_admin": True}
    calls = []

    def provider(request):
        calls.append(request)
        assert request.url.host == "git.born-in-july.ru"
        if request.url.path == "/login/oauth/access_token":
            body = parse_qs(request.content.decode())
            assert body["client_secret"] == ["private-secret"]
            assert body["grant_type"] == ["authorization_code"]
            assert len(body["code_verifier"][0]) >= 43
            assert body["redirect_uri"] == ["http://127.0.0.1/auth/forgejo/callback"]
            return httpx.Response(
                200,
                json={"access_token": "private-provider-token", "refresh_token": "unused-refresh"},
            )
        assert request.url.path == "/login/oauth/userinfo"
        assert request.headers["Authorization"] == "Bearer private-provider-token"
        return httpx.Response(200, json=profile)

    monkeypatch.setattr(
        forgejo, "_client", lambda: httpx.AsyncClient(transport=httpx.MockTransport(provider))
    )
    import importlib

    from ego_server import main

    importlib.reload(main)
    with TestClient(main.app, base_url="http://127.0.0.1") as client:
        yield client, settings, profile, calls


def begin(client):
    verifier = secrets.token_urlsafe(32)
    response = client.post(
        "/auth/forgejo/start", json={"code_challenge": forgejo.challenge(verifier)}
    )
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    flow = response.json()
    assert verifier not in flow["authorization_url"]
    opened = client.get(flow["authorization_url"], follow_redirects=False)
    assert opened.status_code == 302
    query = parse_qs(urlsplit(opened.headers["location"]).query)
    assert query["code_challenge_method"] == ["S256"]
    assert "HttpOnly" in opened.headers["set-cookie"]
    assert "SameSite=lax" in opened.headers["set-cookie"]
    return flow["state"], verifier


def finish(client, state, verifier):
    callback = client.get(
        "/auth/forgejo/callback", params={"state": state, "code": "provider-code"}
    )
    assert callback.status_code == 200, callback.text
    assert "private-provider-token" not in callback.text
    assert "private-secret" not in callback.text
    ticket = re.search(r'ticket:"([A-Za-z0-9_-]{43})"', callback.text)[1]
    # Even the flow initiator needs the completion proof delivered to this browser.
    assert (
        client.post(
            "/auth/forgejo/exchange", json={"state": state, "code_verifier": verifier}
        ).status_code
        == 401
    )
    response = client.post(
        "/auth/forgejo/exchange", json={"state": state, "code_verifier": verifier, "ticket": ticket}
    )
    assert response.status_code == 200, response.text
    return response.json()


def execute(db_fn):
    conn = db.get_connection()
    try:
        result = db_fn(conn)
        conn.commit()
        return result
    finally:
        conn.close()


def test_login_student_token_and_no_provider_credentials_persisted(setup):
    client, settings, _, calls = setup
    settings.local_auth_enabled = False
    assert client.get("/auth/providers").json() == {"forgejo": True, "local": False}
    state, verifier = begin(client)
    assert (
        client.post(
            "/auth/forgejo/exchange", json={"state": state, "code_verifier": verifier}
        ).status_code
        == 202
    )
    result = finish(client, state, verifier)
    assert result["role"] == "student"  # Forgejo's is_admin claim confers no local privileges.
    assert result["username"] == "alice"
    assert len(calls) == 2
    me = client.get("/auth/me", headers={"Authorization": "Bearer " + result["access_token"]})
    assert me.status_code == 200
    assert me.json()["user_id"] == result["user_id"]
    assert execute(lambda conn: conn.execute("SELECT COUNT(*) FROM oauth_flows").fetchone()[0]) == 0
    assert b"private-provider-token" not in settings.db_path.read_bytes()
    assert b"unused-refresh" not in settings.db_path.read_bytes()
    assert b"private-secret" not in settings.db_path.read_bytes()
    for endpoint in ("login", "register"):
        assert (
            client.post(
                "/auth/" + endpoint, json={"username": "alice", "password": "pw"}
            ).status_code
            == 403
        )


def test_name_collision_never_links_existing_admin(setup):
    client, _, _, _ = setup
    execute(
        lambda conn: conn.execute(
            "INSERT INTO students VALUES ('local','alice','admin','',datetime('now'),NULL)"
        )
    )
    result = finish(client, *begin(client))
    assert result["user_id"] != "local"
    assert result["role"] == "student"
    assert result["username"].startswith("forgejo-")


def test_rename_retains_role_and_progress_when_registration_closed(setup):
    client, settings, profile, _ = setup
    first = finish(client, *begin(client))

    def promote(conn):
        conn.execute("UPDATE students SET role='mentor' WHERE id=?", (first["user_id"],))
        conn.execute(
            "INSERT INTO progress (student_id,task_id,version,status,attempts,passed_tests,total_tests) VALUES (?,'F1','1.0.0','passed',1,1,1)",
            (first["user_id"],),
        )

    execute(promote)
    profile["preferred_username"] = "renamed"
    settings.registration_enabled = False
    second = finish(client, *begin(client))
    assert second["user_id"] == first["user_id"]
    assert second["role"] == "mentor"
    assert execute(lambda conn: conn.execute("SELECT COUNT(*) FROM progress").fetchone()[0]) == 1


def test_wrong_client_secret_and_replays_rejected(setup):
    client, _, _, calls = setup
    state, verifier = begin(client)
    assert (
        client.post(
            "/auth/forgejo/exchange", json={"state": state, "code_verifier": "x" * 43}
        ).status_code
        == 401
    )
    other = TestClient(client.app, base_url="http://127.0.0.1")
    assert (
        other.get("/auth/forgejo/callback", params={"state": state, "code": "stolen"}).status_code
        == 400
    )
    assert not calls
    result = finish(client, state, verifier)
    assert result["role"] == "student"
    assert (
        client.post(
            "/auth/forgejo/exchange", json={"state": state, "code_verifier": verifier}
        ).status_code
        == 400
    )
    assert (
        client.get("/auth/forgejo/callback", params={"state": state, "code": "again"}).status_code
        == 400
    )
    assert len(calls) == 2


def test_callback_used_once_even_before_exchange(setup):
    client, _, _, calls = setup
    state, verifier = begin(client)
    response = client.get("/auth/forgejo/callback", params={"state": state, "code": "ok"})
    assert response.status_code == 200
    ticket = re.search(r'ticket:"([A-Za-z0-9_-]{43})"', response.text)[1]
    assert (
        client.get("/auth/forgejo/callback", params={"state": state, "code": "again"}).status_code
        == 400
    )
    assert len(calls) == 2
    assert (
        client.post(
            "/auth/forgejo/exchange",
            json={"state": state, "code_verifier": verifier, "ticket": ticket},
        ).status_code
        == 200
    )


@pytest.mark.parametrize(
    "failure", ["cancel", "expired", "invalid-profile", "closed-registration", "network"]
)
def test_failed_attempts_never_issue_token(setup, failure, monkeypatch):
    client, settings, profile, _ = setup
    state, verifier = begin(client)
    params = {"state": state, "code": "ok"}
    if failure == "cancel":
        params = {"state": state, "error": "access_denied"}
    elif failure == "expired":
        execute(lambda conn: conn.execute("UPDATE oauth_flows SET expires_at=0"))
    elif failure == "invalid-profile":
        profile["sub"] = ""
    elif failure == "closed-registration":
        settings.registration_enabled = False
    elif failure == "network":

        def failed(request):
            raise httpx.ConnectError("Do not expose provider/internal details", request=request)

        monkeypatch.setattr(
            forgejo, "_client", lambda: httpx.AsyncClient(transport=httpx.MockTransport(failed))
        )
    callback = client.get("/auth/forgejo/callback", params=params)
    assert callback.status_code == 400
    assert "Do not expose" not in callback.text
    assert (
        client.post(
            "/auth/forgejo/exchange", json={"state": state, "code_verifier": verifier}
        ).status_code
        == 400
    )
    assert execute(lambda conn: conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]) == 0


def test_external_user_cannot_login_with_empty_password(setup):
    client, _, _, _ = setup
    result = finish(client, *begin(client))
    response = client.post("/auth/login", json={"username": result["username"], "password": ""})
    assert response.status_code == 401


def test_schema_upgrade_idempotent_and_explicit_bootstrap_link(setup):
    from ego_server.cli import main

    client, _, _, _ = setup
    execute(
        lambda conn: conn.execute(
            "INSERT INTO students VALUES ('old','admin-name','admin','',datetime('now'),NULL)"
        )
    )
    assert main(["admin", "link-forgejo", "--user-id", "old", "--subject", "42"]) == 0
    assert main(["admin", "link-forgejo", "--user-id", "old", "--subject", "43"]) == 1
    assert main(["admin", "set-role", "--user-id", "old", "--role", "mentor"]) == 0
    execute(db.init_schema)
    execute(db.init_schema)
    result = finish(client, *begin(client))
    assert result["user_id"] == "old"
    assert result["role"] == "mentor"


def test_approved_username_links_existing_admin_with_registration_closed(setup):
    from ego_server.cli import main

    client, settings, profile, _ = setup
    settings.registration_enabled = False
    execute(
        lambda conn: conn.execute(
            "INSERT INTO students VALUES ('admin-id','local-admin','admin','',datetime('now'),NULL)"
        )
    )
    execute(
        lambda conn: conn.execute(
            "INSERT INTO progress (student_id,task_id,version,status,attempts,passed_tests,total_tests) "
            "VALUES ('admin-id','F1','1.0.0','passed',2,3,3)"
        )
    )
    assert (
        main(
            [
                "admin",
                "link-forgejo",
                "--user-id",
                "admin-id",
                "--username",
                "mrmamongo",
            ]
        )
        == 0
    )
    approval = execute(
        lambda conn: conn.execute(
            "SELECT issuer,username,user_id,created_at,expires_at,status,consumed_at,subject "
            "FROM forgejo_link_approvals"
        ).fetchone()
    )
    assert approval["issuer"] == "https://git.born-in-july.ru"
    assert approval["username"] == "mrmamongo"
    assert approval["user_id"] == "admin-id"
    assert approval["expires_at"] - int(datetime.fromisoformat(approval["created_at"]).timestamp()) == 900

    profile["preferred_username"] = "mrmamongo"
    result = finish(client, *begin(client))
    assert result["user_id"] == "admin-id"
    assert result["username"] == "local-admin"
    assert result["role"] == "admin"
    linked = execute(
        lambda conn: conn.execute(
            "SELECT subject,user_id,remote_username FROM external_identities WHERE issuer=?",
            (approval["issuer"],),
        ).fetchone()
    )
    assert tuple(linked) == ("42", "admin-id", "mrmamongo")
    completed = execute(
        lambda conn: conn.execute(
            "SELECT status,consumed_at,subject FROM forgejo_link_approvals"
        ).fetchone()
    )
    assert completed["status"] == "consumed"
    assert completed["consumed_at"]
    assert completed["subject"] == "42"
    progress = execute(
        lambda conn: conn.execute(
            "SELECT student_id,attempts,passed_tests FROM progress"
        ).fetchone()
    )
    assert tuple(progress) == ("admin-id", 2, 3)


def test_closed_registration_never_links_same_username_without_approval(setup):
    client, settings, profile, _ = setup
    settings.registration_enabled = False
    execute(
        lambda conn: conn.execute(
            "INSERT INTO students VALUES ('admin-id','mrmamongo','admin','',datetime('now'),NULL)"
        )
    )
    state, _ = begin(client)
    callback = client.get(
        "/auth/forgejo/callback", params={"state": state, "code": "provider-code"}
    )
    assert callback.status_code == 400
    assert execute(lambda conn: conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]) == 1
    assert execute(lambda conn: conn.execute("SELECT COUNT(*) FROM external_identities").fetchone()[0]) == 0
    assert profile["preferred_username"] == "alice"


def test_approved_username_mismatch_does_not_consume_or_link(setup):
    from ego_server.cli import main

    client, settings, _, _ = setup
    settings.registration_enabled = False
    execute(
        lambda conn: conn.execute(
            "INSERT INTO students VALUES ('admin-id','local-admin','admin','',datetime('now'),NULL)"
        )
    )
    assert main(
        ["admin", "link-forgejo", "--user-id", "admin-id", "--username", "mrmamongo"]
    ) == 0
    state, _ = begin(client)
    callback = client.get(
        "/auth/forgejo/callback", params={"state": state, "code": "provider-code"}
    )
    assert callback.status_code == 400
    approval = execute(
        lambda conn: conn.execute(
            "SELECT status,subject,consumed_at FROM forgejo_link_approvals"
        ).fetchone()
    )
    assert tuple(approval) == ("pending", None, None)
    assert execute(lambda conn: conn.execute("SELECT COUNT(*) FROM external_identities").fetchone()[0]) == 0


def test_expired_approval_cannot_link_username(setup):
    from ego_server.cli import main

    client, settings, profile, _ = setup
    settings.registration_enabled = False
    profile["preferred_username"] = "mrmamongo"
    execute(
        lambda conn: conn.execute(
            "INSERT INTO students VALUES ('admin-id','local-admin','admin','',datetime('now'),NULL)"
        )
    )
    assert main(
        ["admin", "link-forgejo", "--user-id", "admin-id", "--username", "mrmamongo"]
    ) == 0
    execute(lambda conn: conn.execute("UPDATE forgejo_link_approvals SET expires_at=0"))
    state, _ = begin(client)
    callback = client.get(
        "/auth/forgejo/callback", params={"state": state, "code": "provider-code"}
    )
    assert callback.status_code == 400
    assert execute(lambda conn: conn.execute("SELECT COUNT(*) FROM external_identities").fetchone()[0]) == 0
    assert execute(
        lambda conn: conn.execute("SELECT status FROM forgejo_link_approvals").fetchone()[0]
    ) == "pending"


def test_consumed_approval_cannot_bind_a_second_subject(setup):
    from ego_server.cli import main

    client, settings, profile, _ = setup
    settings.registration_enabled = False
    profile["preferred_username"] = "mrmamongo"
    execute(
        lambda conn: conn.execute(
            "INSERT INTO students VALUES ('admin-id','local-admin','admin','',datetime('now'),NULL)"
        )
    )
    assert main(
        ["admin", "link-forgejo", "--user-id", "admin-id", "--username", "mrmamongo"]
    ) == 0
    first = finish(client, *begin(client))
    assert first["user_id"] == "admin-id"
    profile["sub"] = "43"
    state, _ = begin(client)
    callback = client.get(
        "/auth/forgejo/callback", params={"state": state, "code": "provider-code"}
    )
    assert callback.status_code == 400
    rows = execute(
        lambda conn: conn.execute(
            "SELECT subject,user_id FROM external_identities ORDER BY subject"
        ).fetchall()
    )
    assert [tuple(row) for row in rows] == [("42", "admin-id")]
    assert execute(lambda conn: conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]) == 1


def test_existing_mapped_subject_precedes_username_approval(setup):
    from ego_server.cli import main

    client, settings, profile, _ = setup
    first = finish(client, *begin(client))
    settings.registration_enabled = False
    execute(
        lambda conn: conn.execute(
            "INSERT INTO students VALUES ('admin-id','local-admin','admin','',datetime('now'),NULL)"
        )
    )
    assert main(
        ["admin", "link-forgejo", "--user-id", "admin-id", "--username", "alice"]
    ) == 0
    second = finish(client, *begin(client))
    assert second["user_id"] == first["user_id"]
    assert second["role"] == "student"
    assert execute(
        lambda conn: conn.execute(
            "SELECT role FROM students WHERE id='admin-id'"
        ).fetchone()[0]
    ) == "admin"
    assert execute(
        lambda conn: conn.execute(
            "SELECT status FROM forgejo_link_approvals"
        ).fetchone()[0]
    ) == "pending"


def test_username_approval_cli_rejects_invalid_duplicate_and_linked_targets(setup):
    from ego_server.cli import main

    _, _, _, _ = setup
    execute(
        lambda conn: conn.executemany(
            "INSERT INTO students VALUES (?,?,?,'',datetime('now'),NULL)",
            [
                ("admin-id", "local-admin", "admin"),
                ("other-id", "other", "student"),
            ],
        )
    )
    def approve(user_id: str, username: str) -> int:
        return main(
            ["admin", "link-forgejo", "--user-id", user_id, "--username", username]
        )

    assert approve("admin-id", "") == 1
    assert approve("admin-id", "mrmämongo") == 1
    assert approve("admin-id", "two words") == 1
    assert approve("admin-id", "mrmamongo") == 0
    assert approve("admin-id", "mrmamongo") == 1
    assert approve("other-id", "mrmamongo") == 1
    assert approve("admin-id", "different") == 1
    assert approve("missing", "unknown") == 1
    execute(
        lambda conn: conn.execute(
            "INSERT INTO external_identities VALUES (?,?,?,?,datetime('now'))",
            ("https://git.born-in-july.ru", "already", "other-id", "other"),
        )
    )
    assert approve("other-id", "new-name") == 1


@pytest.mark.parametrize(
    "url",
    [
        "http://git.born-in-july.ru",
        "https://user:secret@git.born-in-july.ru",
        "https://git.born-in-july.ru/?token=x",
        "https://git.born-in-july.ru/#fragment",
    ],
)
def test_invalid_provider_configuration(url):
    with pytest.raises(ValueError):
        forgejo._base_url(url)


def test_vscode_completion_targets_only_local_listener(setup):
    client, _, _, _ = setup
    verifier = secrets.token_urlsafe(32)
    started = client.post(
        "/auth/forgejo/start",
        json={
            "code_challenge": forgejo.challenge(verifier),
            "client": "vscode",
            "callback_port": 41234,
        },
    ).json()
    client.get(started["authorization_url"], follow_redirects=False)
    callback = client.get(
        "/auth/forgejo/callback",
        params={"state": started["state"], "code": "ok"},
        follow_redirects=False,
    )
    assert callback.status_code == 303
    location = urlsplit(callback.headers["location"])
    assert location.netloc == "127.0.0.1:41234"
    ticket = parse_qs(location.query)["ticket"][0]
    assert "access_token" not in location.query
    assert (
        client.post(
            "/auth/forgejo/exchange",
            json={"state": started["state"], "code_verifier": verifier, "ticket": ticket},
        ).status_code
        == 200
    )
    assert (
        client.post(
            "/auth/forgejo/start",
            json={"code_challenge": forgejo.challenge(verifier), "callback_port": 41234},
        ).status_code
        == 422
    )
