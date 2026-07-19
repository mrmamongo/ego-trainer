# ADR-0016: Tasks Content Repository + Sync

**Status:** Accepted
**Date:** 2026-07-19
**Supersedes:** ADR-0001 D2 (частично — canonical остаётся git, но не monorepo `docs/tasks/`)
**Related:** beads `ego-trainer-u4i` (Content Repo Sync), `ego-trainer-gdl` (Ops dashboard), ADR-0001 D3 (SemVer)

## Context

ADR-0001 D2 зафиксировал: задачи живут как `.md` в git, сервер импортирует
meta в SQLite. На практике контент лежал в том же репозитории платформы
(`docs/tasks/`). Это смешивает:

- релизы платформы (ego core, server, extension) и релизы учебного контента;
- права: кто может менять код vs кто пишет задачи;
- деплой: правка опечатки в условии требует rebuild/redeploy платформы.

Нужен отдельный content-repo и явный sync на сервер (cron и/или вручную),
с конфигом URL / auth / ветки.

## Decision

### D16.1. Canonical = отдельный git-репозиторий задач

**Decision:** Учебный контент живёт в отдельном репозитории (например
`ego-tasks`). Платформа (`ego-trainer`) его **не** содержит как prod-источник.

Формат файлов без изменений (см. `docs/TESTS_DESIGN.md`):

```
ego-tasks/
├── block_f_simple/
│   ├── task_f1.md
│   ├── task_f1.solution.py
│   └── task_f1.tests.py
└── ...
```

**Rationale:** независимый lifecycle контента, отдельные права доступа,
git-diff и PR review на задачах без шума от кода платформы.

**Monorepo `docs/tasks/`:** остаётся **dev/test fixture** (pytest, offline
smoke, локальная разработка без внешнего git). Не prod-canonical.

### D16.2. Сервер синкает repo → parse → DB

**Decision:** `ego-server` клонирует/пуллит content-repo в локальный cache,
парсит через ego core, upsert'ит meta в SQLite (как текущий
`admin import-tasks`, по `content_hash` / SemVer).

```
ego-tasks (git)                    ego-server
┌──────────────────┐               ┌─────────────────────────────┐
│ block_*/task_*   │  sync         │ clone/pull → local_path     │
│ .md + sidecars   │ ───────────►  │ parser → tasks / versions   │
└──────────────────┘  cron / UI    │ cache → student pull        │
                                   └─────────────────────────────┘
```

Pipeline:

1. `git fetch` + checkout configured `ref`
2. walk `**/*.md` (+ `.solution.py` / `.tests.py` sidecars)
3. `ego.parser` → `Task`
4. upsert DB (`content_hash` skip / SemVer bump, как `bmh.6`)
5. обновить cache для student `pull`
6. записать sync log: sha, added/updated/skipped/errors, timestamp

**Триггеры:**

| Триггер | Когда |
|---------|--------|
| Cron | schedule из конфига (час / день / custom cron) |
| Manual | `ego-server admin sync-tasks` + кнопка в админке |
| On startup | опционально (`on_startup: true`) |

Webhook (push → sync) — post-v1.

### D16.3. Конфиг: URL, auth, ref (ветка)

**Decision:** настройки content-repo задаются на сервере (файл + env для
секретов). **Ветка / ref обязательно конфигурируема** — не захардкожена.

```yaml
# .ego-server/content.yaml  (пример; путь/формат — реализация)
tasks_repo:
  url: "https://github.com/org/ego-tasks.git"
  ref: "main"                      # branch | tag | sha — через конфиг
  auth:
    type: none | token | ssh       # v1: none + token; ssh — следующая итерация
    # token из env, не из файла:
    # EGO_TASKS_TOKEN
    # ssh_key_path: /run/secrets/tasks_deploy_key
  local_path: "/app/.ego-server/tasks-repo"
  sync:
    schedule: "0 * * * *"          # cron; null/empty = только вручную
    on_startup: true
```

Env-overrides (предложение для реализации):

| Env | Назначение |
|-----|------------|
| `EGO_TASKS_REPO_URL` | git URL |
| `EGO_TASKS_REF` | branch / tag / sha |
| `EGO_TASKS_AUTH_TYPE` | `none` \| `token` \| `ssh` |
| `EGO_TASKS_TOKEN` | PAT / deploy token |
| `EGO_TASKS_SYNC_SCHEDULE` | cron expression или empty |
| `EGO_TASKS_LOCAL_PATH` | clone directory |

**Rationale:** один сервер может смотреть на `main` (staging) или на
`release/2026-q3` / tag (prod) без смены кода.

### D16.4. Админка: Ops vs Content sync (не CMS)

**Decision:**

- **`ego-trainer-gdl`** — Ops dashboard ментора: студенты, прогресс,
  попытки, stale versions. Read-модель поверх SQLite.
- **`ego-trainer-u4i` (CRS)** — Content Repo Sync: конфиг repo, sync
  pipeline, cron/manual, API статуса. Не rich CMS.
- Правка задач — в `ego-tasks` (VS Code / PR). БД не становится
  canonical. In-browser editor задач — later, и только как git-backed
  writer в content-repo.

### D16.5. Offline / CI

**Decision:**

- Прод-сервер: только sync из `tasks_repo.url`.
- Локальная разработка платформы: `EGO_TASKS_REPO_URL=file:///.../docs/tasks`
  или `admin import-tasks --docs-dir docs/tasks` (legacy path остаётся
  для fixture).
- Student offline (`ego check --local`) по-прежнему может парсить
  локальный checkout content-repo или fixture.

## Consequences

**Положительные:**

- Контент и платформа версионируются независимо.
- Права и review на задачах отделены от кода.
- Staging/prod могут смотреть на разные `ref` через конфиг.
- Существующий parser + `import-tasks` переиспользуются как ядро sync.

**Отрицательные / риски:**

- Нужен git на runtime-образе сервера (или sync sidecar).
- Секреты (token / deploy key) — отдельный ops-контур.
- Рассинхрон: студент видит контент только после успешного sync
  (mitigation: sync log + alert в админке, `on_startup`).
- Monorepo fixture и prod-repo могут разъехаться — CI платформы
  должен либо вендорить snapshot, либо тянуть known-good ref.

## Out of scope (этот ADR)

- Webhook sync
- In-browser task editor / PR-from-UI
- SSH auth (после token)
- Перенос существующих `docs/tasks/` в новый remote (одноразовый
  bootstrap-скрипт — отдельная задача реализации)

## References

- ADR-0001 D2 / D3 — git canonical, SemVer
- `docs/TESTS_DESIGN.md` — формат `.md` + sidecars
- `ego_server` `admin import-tasks` — текущий upsert path
- beads: `ego-trainer-u4i` (CRS), `ego-trainer-gdl`
