# ADR-0016: Tasks Content Repository + Sync

**Status:** Accepted (PR 1 implemented: D16.6 catalog + D16.5 local sync; PR 2 pending: D16.2 git remote + D16.3 auth + cron)
**Date:** 2026-07-19
**Supersedes:** ADR-0001 D2 (частично — canonical остаётся git, но не monorepo `docs/tasks/`)
**Related:** beads `ego-trainer-8di` (Content Repo Sync), `ego-trainer-gdl` (Ops dashboard), ADR-0001 D3 (SemVer)

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

Формат **задачи** (statement / solution / tests) — как в
`docs/TESTS_DESIGN.md`. Раскладка репозитория — иерархия
**Project → Folder (block) → Task** (см. D16.6).

```
ego-tasks/
├── catalog.yaml                 # список проектов (или один default)
└── projects/
    └── junior-core/
        ├── project.yaml
        └── folders/
            └── block_f_simple/
                ├── folder.yaml
                ├── task_f1.md
                ├── task_f1.solution.py
                └── task_f1.tests.py
```

**Rationale:** независимый lifecycle контента, отдельные права доступа,
git-diff и PR review на задачах без шума от кода платформы.

**Monorepo `docs/tasks/`:** остаётся **dev/test fixture** (pytest, offline
smoke, локальная разработка без внешнего git). Не prod-canonical.
Legacy flat `docs/tasks/block_*/` мапится в один implicit project
`fixture` при локальном import.

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

### D16.6. Каталог: Project / Folder / Task + откуда sync meta

**Decision:** content-repo — не плоский список `.md`, а каталог с тремя
уровнями. Каждый уровень имеет свой YAML-конфиг; sync читает meta
оттуда (не из БД и не из git-tag alone).

#### Иерархия

| Уровень | Смысл | Пример id | Каталог |
|---------|--------|-----------|---------|
| **Project** | учебный курс / трек (один «продукт» контента) | `junior-core` | `projects/<slug>/` |
| **Folder** | тематический блок внутри проекта (бывш. `block_*`) | `block_f_simple` | `projects/<slug>/folders/<folder>/` |
| **Task** | одна задача | `F1` | файлы `task_<id>.{md,solution.py,tests.py}` |

- Один content-repo может содержать **несколько projects** (разные
  курсы / когорты / языки).
- Сервер при sync выбирает projects через `catalog.yaml` и/или
  `tasks_repo.projects: [junior-core]` в server config (default = все
  `enabled: true`).
- Student/mentor UI фильтрует по `project_id` (+ folder).
- Legacy fixture без `project.yaml` → synthetic project `fixture`,
  folder = имя директории `block_*`.

#### Конфиг-файлы

**`catalog.yaml`** (корень repo) — оглавление:

```yaml
schema_version: 1
projects:
  - id: junior-core
    path: projects/junior-core
    enabled: true
  - id: llm-track
    path: projects/llm-track
    enabled: false
```

**`project.yaml`** — meta курса:

```yaml
id: junior-core                 # стабильный id (= path slug)
name: "Junior Core"             # отображаемое название
description: "Базовый трек: паттерны → логи → домены"
version: "1.2.0"                # SemVer релиза курса (пакет)
order: 10                       # сортировка в UI
default_locale: ru
tags: [python, junior]
```

**`folder.yaml`** — meta блока/папки:

```yaml
id: block_f_simple              # стабильный id (slug директории)
code: F                         # короткий код блока ('F', '1', 'A')
name: "Базовые паттерны"        # название папки
description: "find, filter, count, all/any"
order: 10
level: easy                     # easy | medium | hard (опционально)
```

**`task_*.md`** — YAML frontmatter + тело условия. Frontmatter =
структурированная meta для sync; bold-строки в теле можно оставить
для читаемости statement, но **источник правды для sync = frontmatter**.

```markdown
---
id: F1
title: "Найди первый критический баг"
folder: block_f_simple          # опционально; default = parent dir
version: "1.1.0"                # SemVer задачи (D3) — обязательно
level: easy
tags: [find, linear search, first match]
---

# Задача F1: Найди первый критический баг
...
```

Sidecars рядом: `task_f1.solution.py`, `task_f1.tests.py` (имя файла
= `task_<slug>`; `id` в frontmatter может быть `F1`).

#### Откуда sync берёт поля

| Поле | Источник | Куда в DB / API |
|------|----------|-----------------|
| project.id / name / description / version / order | `project.yaml` | таблица `projects` |
| folder.id / code / name / description / order / level | `folder.yaml` | таблица `folders` (`slug`, `block`=code) |
| task.id | frontmatter `id` (fallback: parse H1) | `tasks.id` / `task_id` |
| task.title | frontmatter `title` (fallback: H1) | `tasks.title` |
| task.version | frontmatter `version` | `tasks.version` + `task_versions` |
| task.level / tags | frontmatter | `tasks.level`, `tasks.tags` |
| task.folder / project | path + frontmatter `folder` | FK → folder → project |
| statement / stub / solution / tests | `.md` + sidecars | cache + pull payload |
| content_hash | hash(statement+stub+solution[+tests meta]) | skip/update |
| content repo revision | git SHA после checkout `ref` | `sync_log.git_sha` |
| curriculum pack version | `project.yaml` `version` | `projects.version` (не путать с task SemVer) |

**Два «version», не смешивать:**

1. **`tasks_repo.ref` / git SHA** — какую ревизию content-repo засинкали
   (ветка/tag на сервере).
2. **`project.version`** — SemVer пакета курса («Junior Core 1.2»).
3. **`task.version`** — SemVer конкретной задачи (D3, progress
   per-version).

#### Политика version при sync

**Decision:** `task.version` **объявляется в файле** (frontmatter).
Авто-bump minor на сервере (текущий `import-tasks`) — legacy; для
нового каталога:

- content_hash не изменился → skip;
- hash изменился и `version` в файле ** Strictly greater** чем в DB →
  update + history row;
- hash изменился, а `version` не подняли → sync error для этой задачи
  (не молчаливый bump);
- опционально `version_policy: auto_minor` в `project.yaml` сохраняет
  старое поведение для миграции fixture.

Breaking: frontmatter `breaking: true` или major bump (`2.0.0` ←
`1.x`) → progress `stale` (как D3/D10).

#### Server config (дополнение к D16.3)

```yaml
tasks_repo:
  url: "https://github.com/org/ego-tasks.git"
  ref: "main"
  projects: ["junior-core"]     # empty / omit = все enabled в catalog.yaml
  # auth, local_path, sync — как в D16.3
```

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
- Мульти-tenant ACL «студент видит только project X» (закладываем
  `project_id` в схему; политика доступа — отдельная задача)

## References

- ADR-0001 D2 / D3 — git canonical, SemVer
- `docs/TESTS_DESIGN.md` — формат `.md` + sidecars
- `docs/CONTENT_CATALOG.md` — примеры YAML + field map (companion)
- `ego_server` `admin import-tasks` — текущий upsert path
- beads: `ego-trainer-u4i` (CRS), `ego-trainer-gdl`
