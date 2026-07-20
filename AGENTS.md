# Agent Instructions

This project uses **bd (beads)** for issue tracking. Run `bd onboard` to get started.

## Project Overview

**ego-trainer** — platform for junior developers to practice coding tasks with auto-checking.
Tasks are markdown files (.md) with statement + reference solution + tests. Students write
solutions in .py stubs, run `check`, get test results. Server tracks progress.

### Architecture (ADR-0001, ADR-0014, ADR-0016)

```
ego-tasks (separate git repo)       ← prod canonical content (ADR-0016)
   ↓ sync (cron / manual): clone → parse → DB meta + cache
docs/tasks/*.md                     ← monorepo fixture only (dev/tests)
   ↓ parser
ego core (parser, runner, checker)  ← Python library
   ↓
ego-server (FastAPI + SQLite)       ← HTTP API, sandbox check, progress
   ↓
vscode-ego (VSCode extension)       ← primary UI (ADR-0014)
ego CLI                             ← secondary, for CI/scripts
ego_tui (textual)                   ← FROZEN per ADR-0014
```

### Tech Stack

| Layer | Tech | Notes |
|-------|------|-------|
| Core | Python 3.11+, Pydantic v2 | `ego/` package |
| Server | FastAPI, SQLite, JWT, uvicorn | `ego_server/` package |
| Extension | TypeScript, VSCode API | `vscode-ego/` — primary UI |
| CLI | Python (argparse) | `ego` entry-point — secondary |
| TUI | textual | `ego_tui/` — FROZEN (ADR-0014) |
| Tests | pytest, pytest-cov | `tests/` — 264 passed, 6 skipped |
| Container | podman/docker compose | `Dockerfile`, `docker-compose.yml` |

### Project Structure

```
ego-trainer/
├── ego/                    # Core library (parser, runner, checker, models)
│   ├── parser.py           # .md -> Task (statement, stub, solution, tests)
│   ├── runner.py           # Subprocess sandbox (timeout 5s, no network)
│   ├── checker.py          # Compare student vs reference on test cases
│   ├── models.py           # Pydantic: Task, Manifest, Progress, Run, Config
│   ├── progress.py         # Progress upsert, run log write
│   └── cli/                # ego CLI (init, check, pull, list)
├── ego_server/             # FastAPI server
│   ├── main.py             # App + router registration
│   ├── db.py               # SQLite schema + init
│   ├── auth.py             # JWT auth, roles (student/mentor/admin)
│   ├── config.py           # Env-based settings (EGO_DB_PATH, EGO_JWT_SECRET)
│   ├── deps.py             # FastAPI deps (CurrentUser, DbDep, require_role)
│   ├── models.py           # API DTOs (TaskMeta, TaskFull, CheckRequest, etc.)
│   └── routers/
│       ├── auth.py         # POST /auth/register, /auth/login, GET /auth/me
│       ├── tasks.py        # GET /tasks, /tasks/<id>, /tasks/<id>/hints
│       ├── check.py        # POST /check (server-side checker + progress)
│       └── progress.py     # POST /progress/push, GET /progress/<student>
├── ego_tui/                # Textual TUI — FROZEN (ADR-0014)
├── vscode-ego/             # VSCode extension — primary UI
│   ├── src/
│   │   ├── extension.ts    # Activate, commands, status bar
│   │   ├── api.ts          # HTTP client to ego-server
│   │   ├── treeProvider.ts # TreeView sidebar (blocks -> tasks)
│   │   └── resultsPanel.ts # Webview for test results
│   ├── package.json        # Commands, views, configuration
│   └── tsconfig.json
├── docs/
│   ├── adr/                # Architecture Decision Records
│   │   ├── 0001-platform-architecture.md
│   │   └── 0014-vscode-extension.md
│   └── tasks/              # Task .md files (git canonical, D2)
│       ├── block_f_simple/ # Block F — basic patterns
│       ├── block_h_more_domains/  # Block H — variety
│       └── ...
├── tests/                  # pytest tests (264 passed, 6 skipped)
├── Dockerfile              # ego-server image
├── docker-compose.yml      # Local dev: podman compose up -d
├── pyproject.toml          # uv project, deps: pydantic, fastapi, etc.
└── AGENTS.md               # This file
```

## Common Commands

```bash
# Python (uv)
uv run pytest                          # Run all tests
uv run pytest tests/test_server_check.py -v  # Run specific test file
uv run ego-server migrate              # Init SQLite schema
uv run ego-server admin import-tasks --docs-dir docs/tasks  # Import tasks to DB
uv run uvicorn ego_server.main:app --reload  # Start server (dev)

# Server (podman/docker)
podman compose up -d                   # Start server on :8000
podman compose logs -f                 # View logs
podman compose down                    # Stop
podman compose down -v                 # Stop + wipe DB
# Server: http://localhost:8000
# Swagger: http://localhost:8000/docs
# Health: http://localhost:8000/health

# VSCode extension
cd vscode-ego && npx tsc -p .          # Compile TypeScript
cd vscode-ego && npx @vscode/vsce package --allow-missing-repository  # Build .vsix
code --install-extension vscode-ego/ego-trainer-0.1.0.vsix  # Install

# Lint
uv run ruff check .                    # Lint
uv run ruff format .                   # Format
```

<!-- BEGIN BEADS INTEGRATION v:1 profile:minimal hash:ca08a54f -->
## Beads Issue Tracker

This project uses **bd (beads)** for issue tracking. Run `bd prime` to see full workflow context and commands.

### Quickstart

```bash
bd ready               # Find available work (no blockers)
bd list --status open  # All open issues
bd show <id>           # View issue details (e.g. bd show ego-trainer-8bv.9)
bd create --title "..." --type task --priority P1 --parent <epic>  # Create task
bd update <id> --status closed     # Close task
bd update <id> --status deferred   # Defer task
bd dep add <child> <parent>        # Add dependency (child blocked by parent)
bd search "keyword"                # Search issues by text
```

### Current State (Wave 8)

| Epic | Status | Notes |
|------|--------|-------|
| 93h Foundation | done | Core library complete |
| 8bv CLI | done | Extension UI (8bv.9) shipped on feature tip |
| bmh Server | done | FastAPI + SQLite + Docker |
| x4f TUI | frozen | ADR-0014 — VSCode extension replaces TUI |
| u4i Content Repo Sync | open | ADR-0016 — separate ego-tasks repo + sync |
| 9u7 Hypothesis | deferred | Post-MVP |
| bbe AI Assistant | deferred | Post-MVP |
| bd2 Content blocks | deferred | Post-MVP |
| gdl Mentor Ops Dashboard | deferred | Post-MVP — progress only, not CMS |

**Next:** implement `ego-trainer-u4i` (tasks-repo sync) per ADR-0016; `gdl` stays Ops.

### Rules

- Use `bd` for ALL task tracking — do NOT use TodoWrite, TaskCreate, or markdown TODO lists
- Run `bd prime` for detailed command reference and session close protocol
- Use `bd remember` for persistent knowledge — do NOT use MEMORY.md files

## Key Design Decisions (ADRs)

- **ADR-0001**: Platform architecture — .md as canonical, parser, sandbox runner, SQLite MVP
- **ADR-0014**: VSCode extension = primary UI, TUI frozen, CLI secondary
- **ADR-0015**: VSCode extension UI flow — welcome, init wizard, dashboard, task view, check flow
- **ADR-0016**: Tasks content repo — separate git, server sync (cron/manual), configurable URL/auth/ref; catalog = Project → Folder → Task (see docs/CONTENT_CATALOG.md)
- **Task Format**: separate .solution.py + .tests.py with @case/@before/@after hooks (see docs/TESTS_DESIGN.md)

See `docs/adr/` for full text.

## Session Completion

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** - Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **PUSH TO REMOTE** - This is MANDATORY:
   ```bash
   git pull --rebase
   bd dolt push
   git push
   git status  # MUST show "up to date with origin"
   ```
5. **Clean up** - Clear stashes, prune remote branches
6. **Verify** - All changes committed AND pushed
7. **Hand off** - Provide context for next session

**CRITICAL RULES:**
- Work is NOT complete until `git push` succeeds
- NEVER stop before pushing - that leaves work stranded locally
- NEVER say "ready to push when you are" - YOU must push
- If push fails, resolve and retry until it succeeds
<!-- END BEADS INTEGRATION -->

## Non-Interactive Shell Commands

**ALWAYS use non-interactive flags** with file operations to avoid hanging on confirmation prompts.

Shell commands like `cp`, `mv`, and `rm` may be aliased to include `-i` (interactive) mode on some systems, causing the agent to hang indefinitely waiting for y/n input.

**Use these forms instead:**
```bash
# Force overwrite without prompting
cp -f source dest           # NOT: cp source dest
mv -f source dest           # NOT: mv source dest
rm -f file                  # NOT: rm file

# For recursive operations
rm -rf directory            # NOT: rm -r directory
cp -rf source dest          # NOT: cp -r source dest
```

**Other commands that may prompt:**
- `scp` - use `-o BatchMode=yes` for non-interactive
- `ssh` - use `-o BatchMode=yes` to fail instead of prompting
- `apt-get` - use `-y` flag
- `brew` - use `HOMEBREW_NO_AUTO_UPDATE=1` env var

## Cursor Cloud specific instructions

Dependencies are refreshed automatically on VM startup (`uv sync --all-extras` for Python, `npm install --prefix vscode-ego` for the extension). `uv` is preinstalled on `PATH`. Standard lint/test/build/run commands are in the "Common Commands" section above.

Non-obvious caveats:

- **No Docker/podman in this environment.** Ignore the `podman compose up -d` instructions. Run the server directly instead: `uv run ego-server migrate`, then `uv run ego-server admin import-tasks --docs-dir docs/tasks`, then `uv run uvicorn ego_server.main:app --host 0.0.0.0 --port 8000`. The `migrate` + `import-tasks` steps are required before the catalog is populated on a fresh DB (`.ego-server/ego.db`).
- **`/check` returns `status: "no_tests"` (0/0) for every task.** The `docs/tasks/*.md` files ship only a statement + reference solution — they contain no `@case` tests. This is expected, not a bug. The checker's real pass/fail logic is exercised by the `pytest` suite (`tests/test_server_check.py`), which builds synthetic tasks with tests. Both the server `/check` and `ego check --local` still run end-to-end (parse task, run student code, record progress).
- **VSCode is not installed**, so the `vscode-ego` extension can't be launched here. It is a thin HTTP client to the server; build/verify it with `npx tsc -p .` (compiles clean) and test its backend via the server API (curl/Swagger at `http://localhost:8000/docs`).
- **`uv run ruff check .` reports pre-existing lint findings** (mostly `E741`/unused imports in `tests/`). These are not caused by environment setup.
- `ego check --local <id>` needs the student solution at `tasks/<block-lower>/task_<id>.py` (e.g. `tasks/f/task_f1.py`); `ego pull` requires a running server, so create the file manually in offline mode.
