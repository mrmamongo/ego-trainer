# ADR-0014: VSCode Extension как primary UI (вместо TUI)

**Status:** Accepted
**Date:** 2026-07-20
**Supersedes:** ADR-0001 D13 (частично — TUI заморожен)
**Related:** beads `ego-trainer-8bv.8`, `ego-trainer-x4f` (заморожен)

## Context

ADR-0001 планировал три entry-points: CLI, TUI (textual), Server. TUI был
primary UI для студента. После реализации TUI skeleton (x4f.1) и начала
x4f.2 (экран задачи с редактором) стало ясно:

- **Junior devs уже живут в VSCode.** Просить их переключаться в терминал
  для решения задач — лишний friction. TUI даёт худший editor experience
  чем VSCode (нет LSP, autocomplete, git integration, extensions).
- **textual pilot тесты нестабильны** на Windows (timing issues с
  `post_message`, `pause`). 3 из 12 тестов x4f.2 падают из-за race
  conditions в pilot, не из-за багов в коде.
- **VSCode extension даёт бесплатно:** real editor, Problems panel,
  CodeLens, TreeView sidebar, status bar, QuickPick, markdown preview,
  diagnostics API. TUI пришлось бы всё это reimplement.

## Decision

**VSCode extension = primary UI для студента.** TUI заморожен на уровне
skeleton (x4f.1), задачи x4f.2/3/4/5 deferred.

### Архитектура: Regular extension + ego-server

```
┌─────────────────┐     HTTP/JSON      ┌──────────────────┐
│  VSCode         │ ←────────────────→ │  ego-server       │
│  Extension      │                    │  (FastAPI)        │
│  (TypeScript)   │                    │                   │
│                 │                    │  ┌──────────────┐ │
│  - TreeView     │  GET /tasks        │  │ ego core      │ │
│  - Editor       │  POST /check       │  │ (parser,      │ │
│  - Problems     │  POST /progress    │  │  checker,     │ │
│  - Status bar   │  GET /progress     │  │  runner)      │ │
│  - CodeLens     │                    │  └──────────────┘ │
│                 │                    │  SQLite           │
└─────────────────┘                    └──────────────────┘
```

Extension = тонкий UI. Вся логика (парсинг, checker, runner) — на сервере.

### Новый endpoint: POST /check

Сервер запускает checker серверно (sandbox), возвращает `CheckResult`.
Это отличается от текущего `POST /progress/push` (который только хранит
уже вычисленный результат). `POST /check`:

1. Принимает `task_id` + `student_code`
2. Парсит .md из БД → Task
3. Запускает `run_check(task, student_code)` в sandbox
4. Сохраняет progress + run log
5. Возвращает `CheckResult` (passed/failed/tests/diff)

### CLI остаётся

CLI (`ego check`, `ego pull`, `ego list`) не удаляется. Он нужен для:
- Offline разработки (`--local`)
- CI/CD testing
- Менторов (быстрая проверка задач)
- Extension может вызывать CLI как fallback (offline mode)

### TUI заморожен

`ego_tui/app.py` остаётся в репо (skeleton работает), но:
- x4f.2/3/4/5 → deferred
- Не тратим время на починку pilot тестов
- Может быть revisited post-MVP если кому-то нужен terminal-only UI

## Consequences

- **+** Лучший UX для студентов (real editor, autocomplete, diagnostics)
- **+** Меньше кода в Python (не нужно reimplement editor в textual)
- **+** Бесплатно: Problems panel, CodeLens, status bar, TreeView
- **−** Новый стек: TypeScript + VSCode Extension API
- **−** Нужен `POST /check` на сервере (sandbox на сервере = security risk)
- **−** Extension distribution через VSCode Marketplace (отдельный процесс)
- **−** TUI тесты заморожены (3 failing pilot tests остаются)

## Security: sandbox на сервере

`POST /check` запускает student code на сервере. Это требует sandbox:
- timeout 5s (уже есть в `ego.runner`)
- no network (уже есть)
- blocked imports (уже есть)
- temp dir (уже есть)
- **NEW:** resource limits (CPU, memory) — нужен docker/cgroups для prod

Для MVP (localhost) — приемлемо. Для prod — Docker container per check
или gVisor/kata-containers.
