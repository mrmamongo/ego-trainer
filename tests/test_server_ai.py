"""Tutoring acceptance tests: delivery gate, billing, access and real defenses."""

import json
import sqlite3
from collections import deque
from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi.testclient import TestClient

from ego_server.ai_config import AISettings, ModelSettings, get_settings, save_settings
from ego_server.auth import create_token
from ego_server.db import init_schema
from ego_server.deps import get_db


CODE = "def task_t1(values):\n    return sum(values)\n"
STATEMENT = """# Задача T1: Сумма
## Условие
Верни сумму чисел.
## Учебные цели
Удерживать накопленную сумму.
## Пояснения
Пустой список — отдельный случай.
## Проверка понимания
Объясни накопление и перенос на новый пример.
<details>
<summary>Эталонное решение</summary>
```python
def task_t1(values):
    return sum(values) # PRIVATE_REFERENCE
```
</details>
## Тесты
```python
[([1, 2], 3, "sum"), ([], 0, "empty")]
```
"""


@pytest.fixture
def env(tmp_path, monkeypatch):
    from cryptography.fernet import Fernet

    import importlib
    from ego_server import config, db as database, main

    monkeypatch.setenv("EGO_DB_PATH", str(tmp_path / "ai.db"))
    importlib.reload(config)
    importlib.reload(database)
    importlib.reload(main)
    app = main.app

    monkeypatch.setattr(config.settings, "settings_encryption_key", Fernet.generate_key().decode())
    db_path = tmp_path / "ai.db"
    path = tmp_path / "task_t1.md"
    path.write_text(STATEMENT, encoding="utf-8")

    def connect():
        db = sqlite3.connect(db_path, check_same_thread=False)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys = ON")
        return db

    with connect() as db:
        init_schema(db)
        for user, role in (("alice", "student"), ("bob", "student"), ("root", "admin")):
            db.execute(
                "INSERT INTO students VALUES (?, ?, ?, '', '2026-01-01', NULL)", (user, user, role)
            )
        db.execute(
            """INSERT INTO tasks (id, block, slug, task_id, title, level, version,
            content_hash, md_path, created_at, updated_at) VALUES
            ('T1', 'T', 'test', 'T1', 'Sum', 'easy', '1.0.0', 'hash', ?, 'now', 'now')""",
            (str(path),),
        )
        save_settings(
            db,
            AISettings(
                enabled=True,
                main=ModelSettings(
                    base_url="http://tutor.local/v1",
                    model="tutor",
                    input_usd_per_million=1,
                    output_usd_per_million=2,
                ),
                guard=ModelSettings(
                    base_url="http://guard.local/v1",
                    model="tiny",
                    input_usd_per_million=1,
                    output_usd_per_million=1,
                ),
            ),
        )

    def db_dep():
        db = connect()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = db_dep
    client = TestClient(app)  # No lifespan: every operation uses this isolated DB.
    headers = {
        name: {"Authorization": "Bearer " + create_token(user_id=name, username=name, role=role)}
        for name, role in (("alice", "student"), ("bob", "student"), ("root", "admin"))
    }
    yield client, headers, connect
    client.close()
    app.dependency_overrides.clear()


def provision(env, amount="1"):
    client, headers, _ = env
    assert (
        client.put(
            "/admin/ai/students/alice", headers=headers["root"], json={"enabled": True}
        ).status_code
        == 200
    )
    assert (
        client.post(
            "/admin/ai/students/alice/credits",
            headers=headers["root"],
            json={"amount_usd": amount, "request_id": "credit-1"},
        ).status_code
        == 200
    )


def fake_provider(monkeypatch, drafts, guard=True):
    import ego_server.ai

    queue = deque(drafts)
    calls = []

    def provider(model, messages, settings):
        calls.append((model.model, messages))
        assert "PRIVATE_REFERENCE" not in json.dumps(messages)
        if model.model == "tiny":
            value = {"allow": guard, "reason": "checked"}
        else:
            value = queue.popleft()
        return {
            "choices": [{"message": {"content": json.dumps(value, ensure_ascii=False)}}],
            "usage": {"prompt_tokens": 100, "completion_tokens": 20},
        }

    monkeypatch.setattr(ego_server.ai, "_provider_sync", provider)
    return calls


def new_session(env, **kwargs):
    client, headers, _ = env
    response = client.post(
        "/ai/sessions",
        headers=headers["alice"],
        json={"task_id": "T1", "student_code": CODE, **kwargs},
    )
    assert response.status_code == 200, response.text
    return response.json()["id"]


def send(env, session_id, text="", request_id="message-1"):
    client, headers, _ = env
    return client.post(
        f"/ai/sessions/{session_id}/messages",
        headers=headers["alice"],
        json={"text": text, "request_id": request_id},
    )


def test_access_and_admin_controls(env):
    client, headers, _ = env
    assert client.get("/ai/me").status_code == 401
    assert not client.get("/ai/me", headers=headers["alice"]).json()["enabled"]
    assert (
        client.post("/ai/sessions", headers=headers["alice"], json={"task_id": "T1"}).status_code
        == 403
    )
    assert (
        client.put(
            "/admin/ai/students/alice", headers=headers["alice"], json={"enabled": True}
        ).status_code
        == 403
    )
    assert client.get("/admin/ai/settings", headers=headers["alice"]).status_code == 403
    provision(env)
    assert client.get("/ai/me", headers=headers["alice"]).json()["available"]
    session_id = new_session(env)
    assert client.get(f"/ai/sessions/{session_id}", headers=headers["bob"]).status_code == 404


def test_encrypted_config_persists_and_keys_are_never_returned(env):
    client, headers, connect = env
    config = client.get("/admin/ai/settings", headers=headers["root"]).json()
    config["main"]["api_key"] = "secret-test-key"
    response = client.put("/admin/ai/settings", headers=headers["root"], json=config)
    assert response.status_code == 200, response.text
    assert "secret-test-key" not in response.text
    assert "api_key" not in response.json()["main"]
    assert response.json()["main"]["api_key_set"]
    with connect() as db:
        assert "secret-test-key" not in str(
            dict(db.execute("SELECT * FROM ai_settings").fetchone())
        )
        assert get_settings(db).main.api_key.get_secret_value() == "secret-test-key"
    # Editing rates/models through a fresh request preserves the encrypted key.
    config = response.json()
    config["main"]["model"] = "new-model"
    assert client.put("/admin/ai/settings", headers=headers["root"], json=config).status_code == 200
    with connect() as db:
        assert get_settings(db).main.model == "new-model"
        assert get_settings(db).main.api_key.get_secret_value() == "secret-test-key"


def test_credit_is_idempotent(env):
    provision(env)
    client, headers, _ = env
    body = {"amount_usd": "1", "request_id": "credit-1"}
    response = client.post("/admin/ai/students/alice/credits", headers=headers["root"], json=body)
    assert response.json()["balance_usd"] == "1.000000"
    body["amount_usd"] = "2"
    assert (
        client.post(
            "/admin/ai/students/alice/credits", headers=headers["root"], json=body
        ).status_code
        == 409
    )


def test_delivery_uses_separate_guard_and_charges_both_once(env, monkeypatch):
    provision(env)
    calls = fake_provider(
        monkeypatch, [{"reply": "Какое значение нужно вернуть для пустого списка?"}]
    )
    session_id = new_session(env)
    response = send(env, session_id, "Дай подсказку")
    assert response.status_code == 200, response.text
    assert [call[0] for call in calls] == ["tutor", "tiny"]
    assert response.json()["account"]["spent_usd"] == "0.000260"
    assert response.json()["account"]["reserved_usd"] == "0.000000"
    assert send(env, session_id, "Дай подсказку").status_code == 200
    assert len(calls) == 2  # Network retry cannot bill twice.


@pytest.mark.parametrize("guard_value", [False, "malformed"])
def test_rejected_or_malformed_review_never_delivers_draft(env, monkeypatch, guard_value):
    provision(env)
    fake_provider(monkeypatch, [{"reply": "SECRET_DRAFT готовый ответ"}], guard=guard_value)
    session_id = new_session(env)
    response = send(env, session_id, "Дай ответ")
    assert response.status_code in (422, 502)
    assert "SECRET_DRAFT" not in response.text
    client, headers, _ = env
    saved = client.get(f"/ai/sessions/{session_id}", headers=headers["alice"]).json()
    assert saved["messages"] == []
    assert saved["account"]["spent_usd"] == "0.000260"
    assert saved["account"]["reserved_usd"] == "0.000000"


def test_guard_transport_failure_and_missing_usage_fail_closed(env, monkeypatch):
    from fastapi import HTTPException
    import ego_server.ai

    provision(env)

    def provider(model, messages, settings):
        if model.model == "tiny":
            raise HTTPException(502, "guard unavailable")
        return {"choices": [{"message": {"content": '{"reply":"DO_NOT_DELIVER"}'}}]}

    monkeypatch.setattr(ego_server.ai, "_provider_sync", provider)
    response = send(env, new_session(env), "Помоги")
    assert response.status_code == 502
    assert "DO_NOT_DELIVER" not in response.text
    with env[2]() as db:
        assert db.execute("SELECT reserved FROM ai_accounts").fetchone()[0] == 0
        assert (
            db.execute("SELECT estimated FROM ai_usage WHERE purpose = 'tutor'").fetchone()[0] == 1
        )


def test_reservations_prevent_parallel_overspend(env):
    from ego_server.ai import _reserve
    from fastapi import HTTPException

    provision(env, "0.000100")
    session_id = new_session(env)

    def reserve(request_id):
        with env[2]() as db:
            try:
                _reserve(db, "alice", request_id, session_id, 80)
                return "ok"
            except HTTPException as exc:
                return exc.status_code

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(reserve, ["one", "two"]))
    assert sorted(results, key=str) == sorted(["ok", 402], key=str)


def test_defense_requires_server_check_and_three_independent_answers(env, monkeypatch):
    provision(env)
    client, headers, _ = env
    assert (
        client.post(
            "/ai/sessions", headers=headers["alice"], json={"task_id": "T1", "mode": "defend"}
        ).status_code
        == 409
    )
    checked = client.post(
        "/check", headers=headers["alice"], json={"task_id": "T1", "student_code": CODE}
    )
    assert checked.status_code == 200, checked.text
    assert checked.json()["status"] == "passed"
    submission_id = checked.json()["understanding"]["submission_id"]
    progress = client.get("/progress/me", headers=headers["alice"]).json()
    assert progress[0]["solution_hash"] == checked.json()["solution_hash"]

    answers = [
        "Накопитель хранит сумму обработанных чисел",
        "После первого числа сумма равна двум",
        "Для среднего нужна сумма и количество",
    ]
    fake_provider(
        monkeypatch,
        [{"reply": "Объясни механизм накопления."}]
        + [
            {"reply": "Следующий вопрос или итог.", "step_passed": True, "evidence": answer}
            for answer in answers
        ],
    )
    session_id = new_session(
        env, mode="defend", submission_id=submission_id, student_code="FORGED CODE"
    )
    assert send(env, session_id).status_code == 200
    for i, answer in enumerate(answers):
        response = send(env, session_id, answer, str(i))
        assert response.status_code == 200, response.text
        assert response.json()["status"] == ("confirmed" if i == 2 else "active")
    submissions = client.get("/ai/submissions", headers=headers["alice"]).json()
    assert submissions[0]["understanding"] == "confirmed"
    assert len(submissions[0]["evidence"]) == 3
    with env[2]() as db:
        assert db.execute("SELECT student_code FROM ai_submissions").fetchone()[0] == CODE


def test_claim_of_understanding_without_answer_is_not_accepted(env, monkeypatch):
    provision(env)
    fake_provider(
        monkeypatch, [{"reply": "Поздравляю", "step_passed": True, "evidence": "понятно всем"}]
    )
    assert send(env, new_session(env), "понятно всем").status_code == 502


def test_learning_sections_are_visible_and_reference_is_hidden(env):
    client, headers, _ = env
    task = client.get("/tasks/T1", headers=headers["alice"]).json()
    for section in ("Учебные цели", "Пояснения", "Проверка понимания"):
        assert section in task["statement_md"]
    assert "PRIVATE_REFERENCE" not in task["statement_md"]
    assert task["solution_py"] == ""


def test_budget_exhaustion_calls_no_models(env, monkeypatch):
    provision(env, "0.000001")
    calls = fake_provider(monkeypatch, [])
    assert send(env, new_session(env), "Помоги").status_code == 402
    assert calls == []


def test_crashed_request_is_recovered_without_losing_budget(env):
    from ego_server.ai import _reserve

    provision(env)
    session_id = new_session(env)
    with env[2]() as db:
        _reserve(db, "alice", "crash", session_id, 500)
        db.execute("UPDATE ai_requests SET created_at = '2000-01-01'")
        db.execute("UPDATE ai_sessions SET busy = 1 WHERE id = ?", (session_id,))
        db.commit()
    client, headers, _ = env
    account = client.get("/ai/me", headers=headers["alice"]).json()
    assert account["reserved_usd"] == "0.000000"
    assert account["spent_usd"] == "0.000500"
    with env[2]() as db:
        assert db.execute("SELECT busy FROM ai_sessions").fetchone()[0] == 0


def test_openai_compatible_transport_runs_tutor_then_guard(env):
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    from threading import Thread
    from pydantic import SecretStr

    received = []

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            payload = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            received.append((self.path, payload, self.headers.get("Authorization")))
            value = (
                {"allow": True, "reason": "safe"}
                if payload["model"] == "tiny"
                else {"reply": "Что вернёт функция для пустого списка?"}
            )
            raw = json.dumps(
                {
                    "choices": [{"message": {"content": json.dumps(value)}}],
                    "usage": {"prompt_tokens": 10, "completion_tokens": 10},
                }
            ).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def log_message(self, *args):
            pass

    with ThreadingHTTPServer(("127.0.0.1", 0), Handler) as server:
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            provision(env)
            with env[2]() as db:
                settings = get_settings(db)
                settings.main.base_url = settings.guard.base_url = (
                    f"http://127.0.0.1:{server.server_port}/v1"
                )
                settings.main.api_key = SecretStr("transport-key")
                save_settings(db, settings)
            response = send(env, new_session(env), "Подсказка")
            assert response.status_code == 200, response.text
            assert [p[0] for p in received] == ["/v1/chat/completions"] * 2
            assert [p[1]["model"] for p in received] == ["tutor", "tiny"]
            assert received[0][2] == "Bearer transport-key"
            assert all("tools" not in p[1] for p in received)
        finally:
            server.shutdown()
            thread.join(timeout=2)


def test_help_uses_updated_code_without_changing_submission(env, monkeypatch):
    provision(env)
    calls = fake_provider(monkeypatch, [{"reply": "Which expression is now evaluated?"}])
    session_id = new_session(env)
    client, headers, _ = env
    response = client.post(
        f"/ai/sessions/{session_id}/messages",
        headers=headers["alice"],
        json={"text": "Explain my updated code", "student_code": "UPDATED_STUDENT_CODE"},
    )
    assert response.status_code == 200, response.text
    assert "UPDATED_STUDENT_CODE" in json.dumps(calls[0][1])


def test_provider_url_rejects_credentials_queries_and_metadata():
    from pydantic import ValidationError

    for url in (
        "http://user:secret@host/v1",
        "https://host/v1?key=secret",
        "http://169.254.169.254",
    ):
        with pytest.raises(ValidationError):
            ModelSettings(base_url=url)


def test_teacher_understanding_read_is_scoped_and_excludes_code_and_billing(env):
    client, headers, connect = env
    with connect() as database:
        database.execute(
            """INSERT INTO ai_submissions
            (id,student_id,task_id,version,solution_hash,student_code,statement_md,
             understanding,evidence_json,created_at) VALUES
            ('submission','alice','T1','1.0.0','hash',?,'statement','confirmed',?,'now')""",
            (CODE, json.dumps([{"stage": "mechanism", "quote": "My own explanation"}])),
        )
        database.execute("UPDATE students SET role='mentor' WHERE id='root'")
    endpoint = "/progress/alice/understanding"
    assert client.get(endpoint).status_code == 401
    assert client.get(endpoint, headers=headers["bob"]).status_code == 403
    own = client.get(endpoint, headers=headers["alice"])
    teacher = client.get(endpoint, headers=headers["root"])
    assert own.status_code == teacher.status_code == 200
    assert own.json() == teacher.json()
    assert client.get("/progress/me", headers=headers["alice"]).json() == []
    assert client.get("/progress/me/understanding", headers=headers["alice"]).json() == own.json()
    assert client.get("/progress/me/understanding", headers=headers["bob"]).json() == []
    assert client.get("/progress/me/understanding").status_code == 401
    result = teacher.json()[0]
    assert result["understanding"] == "confirmed"
    assert result["evidence"][0]["quote"] == "My own explanation"
    assert "student_code" not in result and "balance_usd" not in result
    assert client.get("/admin/ai/settings", headers=headers["root"]).status_code == 403
    assert client.get("/progress/unknown/understanding", headers=headers["root"]).status_code == 404
