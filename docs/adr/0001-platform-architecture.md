# ADR-0001: Platform Architecture (MVP)

**Status:** Accepted
**Date:** 2026-07-19
**Supersedes:** none
**Related:** beads epics `ego-trainer-93h`, `ego-trainer-8bv`, `ego-trainer-bmh`, `ego-trainer-x4f`

## Context

У нас есть 33 задачи в `docs/tasks/<block>/<task>.md` (контент-слой, Markdown). Нужно построить платформу: студент решает задачи, проверяется автоматически, ментор видит прогресс. MVP scope = CLI + TUI + Server. AI и Web-dashboard — post-MVP.

При обсуждении было рассмотрено несколько альтернатив (Dolt как сервер, Go-сервер, генерация .py из Markdown, runtime exec, distributed git-подобная модель). Часть из них была отвергнута как overkill для MVP.

## Decisions

### D1. Стек: Python-only + uv

**Decision:** Весь MVP на Python. Менеджер пакетов — `uv`.

**Rationale:** textual (TUI) живёт только в Python. Один язык — проще тестировать и деплоить. uv быстрый, современный дефолт, lock-файл из коробки.

**Alternatives rejected:**
- Go-сервер (как beads) — Dolt first-class SDK, но два языка усложняют MVP.
- poetry — медленнее uv, менее современный.

### D2. Хранение задач: Git canonical

**Decision:** `.md` файлы в git — canonical источник. Сервер при `pull` читает их через ego core parser. БД сервера хранит meta + прогресс, не контент.

**Rationale:** git-diff показывает эволюцию задач. Ментор правит `.md` в VS Code, коммитит, деплоит. Знакомо и прозрачно.

**Alternatives rejected:**
- БД canonical (TEXT-колонки) — двойной источник правды, нужна команда импорта.
- Git canonical + БД cache — сложнее, разница с выбранной минимальна.

### D3. Версионирование: SemVer

**Decision:** Каждая задача имеет `version: "MAJOR.MINOR.PATCH"`. Major — breaking (изменился интерфейс функции, тесты, эталон). Minor — добавление тестов/уточнение условия. Patch — typo/форматирование.

**Rationale:** Гранулярно, студент видит «у тебя решение для v1.0, актуальная v2.0».

**Alternatives rejected:**
- Auto-increment revision — не видно breaking это или нет.
- Content-hash + breaking-флаг — детерминировано, но hash не читаем.

### D4. Эталон (solution): локально в кеше

**Decision:** `ego pull` тянет эталон в `.ego/cache/sol/<block>/<task>.py`. Скрыт от TUI. `ego check` выполняет локально (оффлайн). Не паримся про DRM.

**Rationale:** Check работает без сервера. Сервер не выполняет чужой код (security). Если студент подсматривает — ментор видит по количеству попыток.

**Alternatives rejected:**
- Эталон только на сервере — check не работает оффлайн, сервер = SPOF.
- Encrypted локально — overkill для MVP, Python-код всё равно достанут.

### D5. Структура клиента: `.ego/` + `tasks/`

**Decision:**
```
project/
  tasks/                          # видимая папка студента
    <block>/
      <task>.md                   # условие (видимый doc)
      <task>.py                   # stub → редактируется → решение студента
  .ego/                           # скрытая meta
    config.yaml                   # server URL, token, student_id
    manifest.yaml                 # что выгружено (id, version, hash)
    progress.json                 # прогресс по задачам
    runs/<task>-<ts>.log          # логи прогонов
    cache/
      sol/<block>/<task>.py       # эталон (скрыт от TUI)
```

**Rationale:** Студент работает в видимой `tasks/` (как раньше), мета спрятана. Stub редактируется на месте — привычный UX.

### D6. Offline режим: `ego check --local`

**Decision:** `ego check --local <task>` парсит `docs/tasks/*.md` напрямую, без `.ego/manifest.yaml` и без сервера.

**Rationale:** При git-canonical парсер уже в либе — offline режим практически бесплатен (5 строк кода). Нужен для: разработки платформы (MVP без сервера), тестирования платформы (pytest), ментора (быстро проверить новую задачу).

### D7. Сервер: FastAPI + SQLite (MVP) → Postgres (прод)

**Decision:** FastAPI + SQLite для MVP, та же схема мигрирует на Postgres.

**Rationale:** Zero-config SQLite — легко стартовать. FastAPI — знакомый стек, async, OpenAPI. Postgres — прод, та же SQL-схема.

### D8. Auth: JWT + roles

**Decision:** JWT-токены. Roles: `student`, `mentor`, `admin`. `ego login` получает токен, хранит в `.ego/config.yaml`.

**Rationale:** Стандарт, просто, stateless. Роли покрывают все UX-сценарии.

### D9. Сервер не выполняет студенческий код

**Decision:** Сервер хранит meta + прогресс, но НИКОГДА не выполняет решения студента. `ego check` всегда локален. `ego push` отправляет лог прогона + hash решения.

**Rationale:** Security (не запускаем чужой код на сервере), scalability (нагрузка на клиентах), offline-friendly.

### D10. Прогресс хранится per-version

**Decision:** `progress (student_id, task_id, version, status, ...)`. Если задача обновилась до новой version, прогресс по старой сохраняется, но помечается `stale`.

**Rationale:** Если эталон обновился breaking-образно, старое решение может не проходить — но мы не теряем историю. Студент видит «для v1.0 решено, для v2.0 надо пересдать».

### D11. Синхронизация (pull/push) — corner cases

**Decision:** См. таблицу corner cases в `docs/adr/0001-corner-cases.md` (позже). Ключевые моменты:
- `pull` сверяет hash локального `.md` с серверным. Если отличаются и нет локальных правок — silently обновляет. Если есть локальные правки — warns.
- `push` не доверяет клиенту: принимает только лог прогона с `passed=True` + hash решения + hash эталона + version. «Решено» на сервере = есть лог с passed=True.
- Breaking-change в новой version → warns при pull, прогресс по старой помечается `stale`.

### D12. Sandbox для `ego check`

**Decision:** Решение студента выполняется в subprocess с ограничениями:
- timeout 5s (от `while True`)
- без network
- temp dir как cwd
- запрещённые imports (`os.system`, `subprocess`, `socket`, `urllib`) → warns
- stdout/stderr перехватывается, обрезается до N символов

**Rationale:** Защита от зацикливания, сетевых exfil, file-system доступа.

### D13. Разделение CLI (три entry-point'а)

**Decision:** Три отдельных CLI-инструмента, каждый со своим entry-point в `pyproject.toml`:
- `ego` — клиент (студент): `init`, `list`, `check`, `pull`, `push`. Точка входа `ego.cli.main:main`.
- `ego-server` — сервер: `run` (uvicorn), `migrate` (init schema), `admin import` (залить .md в БД), `admin create-user`. Точка входа `ego_server.cli:main`.
- `ego-tui` — TUI: `start` (запуск textual-приложения). Точка входа `ego_tui.cli:main`.

**Rationale:** Роли разделены — студенту не нужны серверные команды, ментору не нужен TUI. Чистые интерфейсы, меньше путаницы. Каждый entry-point тянет только нужные extras.

### D14. Сервер в Docker

**Decision:** `ego_server` деплоится через Docker:
- `Dockerfile` в корне (или `ego_server/Dockerfile`) — multi-stage: build wheels → runtime на slim Python.
- `docker-compose.yml` — сервис `ego-server`, том для `.ego-server/` (SQLite), порт 8000.
- `.dockerignore` — исключает `.venv/`, `.ego/`, `__pycache__/`, `.beads/`, `docs/` (кроме задач — сервер читает их через mount или COPY при build).
- Базовый образ: `python:3.11-slim`.
- WSGI/ASGI server: `uvicorn` (dev) или `gunicorn -k uvicorn.workers.UvicornWorker` (prod).

**Rationale:** Воспроизводимый деплой, изоляция, легко переключиться на Postgres (добавить сервис в compose). Ментор/админ поднимает одной командой `docker compose up`.

### D15. Тесты в .md (явные кейсы, Hypothesis — post-MVP)

**Decision:** Формат .md расширен секцией `## Тесты` с явными кортежами:
```python
[
    (input1, expected1, "happy path"),
    (input2, expected2, "edge: пустой список"),
    (input3, expected3, "edge: None"),
]
```
Checker прогоняет все кейсы, считает `passed=2, total=3`, показывает diff. Hypothesis property-based testing — post-MVP (эпик `ego-trainer-9u7`), strategies в `ego/strategies/<block>/<task>.py`.

**Rationale:** Явные кейсы — ментор контролирует edge cases, читаемо, просто. Hypothesis — мощно, но усложняет MVP. Существующие 33 .md остаются как reference (без тестов), новые задачи — по полному формату.

**Alternatives rejected:**
- Только Hypothesis — strategy для каждой задачи всё равно писать, сложнее для доменных задач.
- Только явные кортежи навсегда — теряем автоматическое покрытие edge cases.

## Architecture (слои)

```
┌────────────────────────────────────────────────────────────────┐
│  ego server (FastAPI + SQLite)                                 │
│    auth (JWT + roles) · /tasks · /progress/push · /progress/:s │
│    admin import: .md -> БД meta (через ego core parser)        │
└────────────────────────────────────────────────────────────────┘
                          ▲                ▲
                          │ pull/push      │ read-only (post-MVP web)
                          │                │
┌─────────────────────────┐   ┌──────────────────────────────────┐
│  ego client             │   │  ego web (post-MVP)              │
│  CLI (init/check/...)   │   │  Svelte SPA, менторский дашборд  │
│  TUI (textual)          │   └──────────────────────────────────┘
│  ego core (lib)         │
│    parser · runner · checker · progress                       │
└─────────────────────────┘
```

## Consequences

**Положительные:**
- Один язык — простая разработка, тесты, деплой.
- Offline-режим бесплатный при git-canonical.
- Сервер не запускает чужой код — security & scalability.
- SemVer даёт гранулярный контроль версий.
- Git-diff на `docs/tasks/` видит эволюцию контента.

**Отрицательные / риски:**
- Эталон виден студенту через `cat` — плагиат не детектируется в MVP. Post-MVP: hash + LLM-сравнение.
- Нет multi-student на одной машине — `.ego/config.yaml` хранит один student_id.
- Логи прогонов могут содержать секреты — `ego push --dry-run` + обрезка.
- Семантика «breaking change» субъективна — ментор решает при импорте.

## Open questions (post-MVP)

- AI-ассистент: LLM-клиент (OpenAI-совместимый), статичные hints + LLM-fallback, interviewer mode.
- Web Dashboard: Svelte + shadcn-svelte, real-time прогресс.
- Block I (LLM components) и расширение существующих блоков.
- Плагиат-детекция.

## References

- `docs/tasks/` — 33 задачи как canonical-контент.
- `docs/JUNIOR.md`, `docs/MENTOR.md`, `docs/TASKS.md` — профили и карта.
- beads epics: `ego-trainer-93h` (Foundation), `ego-trainer-8bv` (CLI), `ego-trainer-bmh` (Server), `ego-trainer-x4f` (TUI).
