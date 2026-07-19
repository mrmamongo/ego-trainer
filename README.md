# ego-trainer

Platform for junior developers to practice coding tasks with auto-checking.
Tasks are markdown files (`.md`) with statement + reference solution + tests.
Students write solutions in `.py` stubs, run `check`, get instant test results.
Server tracks progress across tasks.

## Quick Start

### 1. Start the server

```bash
podman compose up -d          # or: docker compose up -d
```

Server runs on `http://localhost:8000`. Swagger UI at `/docs`.

### 2. Install the VSCode extension

```bash
cd vscode-ego
npx tsc -p .
npx @vscode/vsce package --allow-missing-repository
code --install-extension ego-trainer-0.1.0.vsix
```

### 3. Use it

1. Open a workspace folder in VSCode
2. Run **`Ego: Init`** from Command Palette (or auto-welcome screen)
3. Choose **Connect to Server** or **Use Offline**
4. Dashboard opens with all tasks
5. Click a task → write code in `.py` editor → click **Check**
6. See test results, iterate

## Architecture

```
docs/tasks/*.md                    ← git canonical source of truth
   ↓ parser
ego/ (core library)                ← parser, runner, checker, models
   ↓
ego_server/ (FastAPI + SQLite)     ← HTTP API, sandbox check, progress
   ↓
vscode-ego/ (VSCode extension)     ← primary UI
ego/ (CLI)                         ← secondary, for CI/scripts
```

| Layer | Tech |
|-------|------|
| Core | Python 3.11+, Pydantic v2 |
| Server | FastAPI, SQLite, JWT, uvicorn |
| Extension | TypeScript, VSCode API |
| Tests | pytest (264 passed, 6 skipped) |
| Container | podman / docker compose |

## Project Structure

```
ego/                # Core: parser, runner, checker, models, CLI
ego_server/         # FastAPI server: auth, tasks, check, progress
ego_tui/            # Textual TUI (frozen — ADR-0014)
vscode-ego/         # VSCode extension (primary UI)
docs/tasks/         # Task .md files (canonical)
docs/adr/           # Architecture Decision Records
tests/              # pytest test suite
Dockerfile          # Server image
docker-compose.yml  # Local dev setup
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/register` | Register (student/mentor/admin) |
| POST | `/auth/login` | Login, returns JWT |
| GET | `/auth/me` | Current user info |
| GET | `/tasks` | List all tasks (metadata) |
| GET | `/tasks/<id>` | Get full task (statement + stub) |
| GET | `/tasks/<id>/hints` | Progressive hints (rules → example → signature) |
| POST | `/check` | Run checker server-side, return test results |
| POST | `/progress/push` | Push student progress |
| GET | `/progress/<student>` | Get student progress (mentor/admin) |
| GET | `/health` | Health check |

## Commands

```bash
# Server
podman compose up -d              # Start server
podman compose logs -f            # View logs
podman compose down -v            # Stop + wipe DB

# Tests
uv run pytest                     # All tests
uv run pytest tests/test_server_check.py -v

# Extension
cd vscode-ego && npx tsc -p .     # Compile TS
cd vscode-ego && npx @vscode/vsce package --allow-missing-repository  # Build .vsix

# Lint
uv run ruff check .
uv run ruff format .
```

## Task Format

Tasks are `.md` files in `docs/tasks/<block>/<task>.md`:

````markdown
# Задача F1: Найди первый критический баг

**Блок:** F — Базовые паттерны
**Сложность:** easy
**Темы:** find, linear search

## Условие

В баг-трекере нужно найти первый критический баг...

## Пример

```python
task_f1_find_critical(bugs)
# -> "Crash on login"
```

<details>
<summary>Эталонное решение</summary>

```python
def task_f1_find_critical(bugs):
    for b in bugs:
        if b["severity"] == "critical":
            return b["title"]
    return ""
```

</details>

## Тесты

```python
[
    (([{"id": "B1", "severity": "critical", "title": "Crash"}],), "Crash", "basic"),
    (([],), "", "empty list"),
]
```
````

Parser extracts: statement (without solution), stub (with `pass`), reference solution, test cases.

## Documentation

- [ADR-0001: Platform Architecture](docs/adr/0001-platform-architecture.md)
- [ADR-0014: VSCode Extension as Primary UI](docs/adr/0014-vscode-extension.md)
- [AGENTS.md](AGENTS.md) — full project guide for AI agents

## License

MIT
