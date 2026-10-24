# Task Authoring Guide — Content Catalog (ADR-0016)

This document describes how to create and version tasks in the ego-trainer
content repository. It covers both the **new catalog layout** (ADR-0016 D16.6)
and the **legacy fixture layout** (`docs/tasks/block_*/`).

> **TL;DR for new tasks:** use the catalog layout. Create `catalog.yaml` at
> repo root, then `projects/<id>/project.yaml`, `folders/<id>/folder.yaml`,
> and `task_<slug>.md` + `.solution.py` + `.tests.py` sidecars.
> Optional theory cards (`lesson_<slug>.md`) live in the folder too — see §3.4.

---

## 1. Repository Layout

### 1.1 Catalog mode (new, preferred)

```
ego-tasks/                              ← content-repo root
├── catalog.yaml                        ← table of contents (list of projects)
└── projects/
    └── <project_id>/                   ← e.g. junior-core
        ├── project.yaml                ← project metadata + version policy
        └── folders/
            └── <folder_id>/            ← e.g. block_f_simple
                ├── folder.yaml         ← folder (block) metadata
                ├── lesson_<slug>.md    ← optional theory card (+ frontmatter)
                ├── task_<slug>.md      ← task statement (+ YAML frontmatter)
                ├── task_<slug>.solution.py   ← reference solution (sidecar)
                └── task_<slug>.tests.py      ← test cases (sidecar)
```

### 1.2 Legacy fixture mode (backward-compatible)

```
docs/tasks/                             ← no catalog.yaml, no project.yaml
└── block_f_simple/                     ← folder = directory name
    ├── task_f1.md                      ← H1 + bold meta (no frontmatter)
    ├── task_f1.solution.py
    └── task_f1.tests.py
```

Legacy mode auto-creates a synthetic project `fixture` with
`version_policy: auto_minor`. No YAML configs needed, but you lose
SemVer enforcement (any content change silently bumps minor version).

**Use catalog mode for all new work.**

---

## 2. YAML Configs

### 2.1 `catalog.yaml` (repo root)

Table of contents — lists all enabled projects.

```yaml
schema_version: 1
projects:
  - id: junior-core
    path: projects/junior-core
    enabled: true
  - id: algorithms
    path: projects/algorithms
    enabled: true
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `schema_version` | int | yes | Must be `1` |
| `projects[].id` | str | yes | Stable project identifier (matches directory slug) |
| `projects[].path` | str | yes | Relative path from repo root to project dir |
| `projects[].enabled` | bool | no | `false` = skip during sync (default: `true`) |

### 2.2 `project.yaml`

One per project directory. Defines curriculum-level metadata and the
**version policy** that governs how task version bumps are enforced.

```yaml
id: junior-core
name: "Junior Core"
description: "Core Python skills for junior developers"
version: "1.0.0"
order: 1
default_locale: ru
tags: [python, basics]
version_policy: declare
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | str | required | Stable identifier (matches directory slug) |
| `name` | str | required | Human-readable project name |
| `description` | str | `""` | Short description |
| `version` | str | `"1.0.0"` | SemVer of the curriculum pack (not individual tasks) |
| `order` | int | `0` | Sort order for UI display |
| `default_locale` | str | `"ru"` | Default locale for task statements |
| `tags` | list[str] | `[]` | Project-level tags |
| `version_policy` | `declare` \| `auto_minor` | `"declare"` | **See §4** |

### 2.3 `folder.yaml`

One per folder (block) directory. Groups related tasks.

```yaml
id: block_f_simple
code: F
name: "Базовые паттерны"
description: "Linear search, filtering, first-match patterns"
order: 1
level: easy
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | str | required | Stable identifier (matches directory slug) |
| `code` | str | required | Short block code shown in UI: `F`, `1`, `A`, ... |
| `name` | str | required | Human-readable folder name |
| `description` | str | `""` | Short description |
| `order` | int | `0` | Sort order within project |
| `level` | `easy` \| `medium` \| `hard` \| null | `null` | Default difficulty (can be overridden per task) |

> **If `folder.yaml` is missing**, the walker synthesizes one from the
> directory name: `block_f_simple` → code `F`, name "Block F Simple".
> This is a convenience for migration — prefer explicit YAML.

---

## 3. Task Files

Each task consists of **three required files** and an optional starter with a shared basename:

| File | Purpose |
|------|---------|
| `task_<slug>.md` | Statement (what the student sees) + YAML frontmatter (sync meta) |
| `task_<slug>.solution.py` | Reference solution (hidden from students, used by checker) |
| `task_<slug>.tests.py` | Test cases via `@case` decorator (run against student + reference) |
| `task_<slug>.student.py` | Optional explicit starter for debugging, modifications and GIVEN helpers; otherwise generated from the reference signature |

### 3.1 `task_<slug>.md` — statement + frontmatter

The `.md` file has two parts:

1. **YAML frontmatter** (between `---` delimiters) — sync metadata,
   source of truth for versioning (ADR-0016 D16.6).
2. **Markdown body** — the task statement shown to students.

```markdown
---
id: F1
title: "Найди первый критический баг"
version: "1.0.0"
level: easy
tags: [find, linear-search, first-match]
breaking: false
---

# Задача F1: Найди первый критический баг

## Условие

В баг-трекере нужно быстро найти первый критический баг в списке.
Функция перебирает список багов и возвращает заголовок первого,
у которого `severity == "critical"`.

## Аргументы

- `bugs` — список словарей вида `[{"id": "B1", "severity": "critical", "title": "Crash"}, ...]`

## Возвращает

Строку — значение поля `"title"` первого бага с `severity == "critical"`.
Если такого бага нет — пустую строку `""`.

## Пример

```python
bugs = [
    {"id": "B1", "severity": "minor", "title": "Typo"},
    {"id": "B2", "severity": "critical", "title": "Crash on login"},
]
task_f1_find_critical(bugs)
# -> "Crash on login"
```
```

#### Frontmatter fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | str | required | Task identifier: `F1`, `1.5`, `A3`, ... |
| `title` | str | required | Human-readable title (shown in UI) |
| `version` | str | `"1.0.0"` | SemVer of this task (see §4) |
| `level` | `easy` \| `medium` \| `hard` | `"easy"` | Difficulty (overrides folder-level) |
| `tags` | list[str] | `[]` | Topic tags for filtering |
| `folder` | str \| null | `null` | Override folder id (default: parent directory name) |
| `breaking` | bool | `false` | Marks a breaking change (invalidates prior progress) |
| `theory` | list[str] | `[]` | Ordered lesson ids shown before the task (see §3.4) |

#### Markdown body conventions

- **`## Условие`** (required) — the problem statement.
- **`## Аргументы`** (optional) — parameter descriptions.
- **`## Возвращает`** (optional) — return value description.
- **`## Правила`** (optional) — constraints / rules.
- **`## Пример`** (optional) — usage example with code block.

> **No `<details>` block needed** in catalog mode — the solution lives in
> the `.solution.py` sidecar. The legacy `<details><summary>Эталонное
> решение</summary>` block is still supported as a fallback if no
> `.solution.py` sidecar exists, but prefer sidecars for new tasks.

### 3.2 `task_<slug>.solution.py` — reference solution

A plain Python file with the reference implementation. The function name
**must** match the pattern `task_<slug_with_underscores>`:

```python
def task_f1_find_critical(bugs):
    for b in bugs:
        if b["severity"] == "critical":
            return b["title"]
    return ""
```

Rules:
- One main function per file (name = `task_` + slug with `_`).
- No `if __name__ == "__main__"` guard needed.
- No imports of ego internals — pure solution code.
- The function signature is extracted to generate the student stub.

### 3.3 `task_<slug>.tests.py` — test cases

Uses the `@case` decorator from `ego.testing`:

```python
from ego.testing import case

@case(
    args=([{"id": "B1", "severity": "critical", "title": "Crash"}],),
    expected="Crash",
    description="one critical bug",
    level="smoke",
)
@case(
    args=([],),
    expected="",
    description="empty list",
    level="smoke",
)
@case(
    args=([{"id": "B1", "severity": "minor", "title": "Typo"}],),
    expected="",
    description="no critical bugs",
    level="smoke",
)
def task_f1_find_critical(a0):
    ...
```

#### `@case` parameters

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `args` | tuple | yes | Positional arguments to pass to the task function. **Must be a tuple** — for a single list arg, write `([1, 2, 3],)` not `([1, 2, 3])` |
| `expected` | any | yes | Expected return value (compared by `==`) |
| `description` | str | `""` | Human-readable test case description |
| `level` | `"smoke"` \| `"full"` | `"smoke"` | Test tier: `smoke` = quick checks, `full` = comprehensive corpus |

#### Hooks (optional)

```python
from ego.testing import case, before, after

@before
def setup():
    """Runs before each case. Must return a dict (context)."""
    return {"mock_db": connect_test_db()}

@after
def teardown(task_func, case_result, ctx):
    """Runs after each case. Receives (function, CaseResult, context)."""
    ctx["mock_db"].close()

@case(args=(...,), expected=..., level="full")
def task_x(a0):
    ...
```

#### Static rules (`@rules`, optional)

```python
from ego.testing import case, rules

@rules(
    forbid_names=["sorted"],
    messages={"sorted": "Сортировку нужно написать самому"},
)
@case(args=([1, 3], [2]), expected=[1, 2, 3], description="merge")
@case(args=([], [1]), expected=[1], description="empty + one")
def task_li21_merge_sorted(a, b):
    ...
```

`@rules` checks the student's **code** (AST), not only return values — use it
when the statement says «не используй `sorted`», «напиши функцию
`parse_command`», etc.

| Param | Description |
|-------|-------------|
| `forbid_names` | Bare names used anywhere (`sorted(...)`, `x = max`) |
| `forbid_methods` | Attribute calls (`x.sort(...)`, `s.replace(...)`) |
| `forbid_imports` | `import math`, `from math import ...` (also `math.sqrt(...)` calls) |
| `forbid_nodes` | `ast` node class names: `Global`, `Lambda`, `ListComp`, `While`, ... |
| `require_functions` | Top-level functions that must exist (name only) |
| `allow_in` | Functions exempt from `forbid_*` (besides the built-in `given_*` exemption) |
| `messages` | Russian text per rule key: `"sorted"`, `"sort"`, `"math"`, `"Global"` |

- Stackable with `@case` in any order; only one `@rules` per task function.
- Arguments are validated when the module is imported (unknown ast node →
  `ValueError`).
- Each violation is one failing result placed before the cases:
  «Правило: нельзя использовать `sorted` (строка 7)» /
  «Правило: нужна функция `parse_command`». Cases still run, but the task
  cannot reach `passed` while a rule fails.
- The reference solution is checked with the same rules by
  `scripts/verify_*_catalog.py`, so the reference must obey its own rules too.
- `@rules` is **not** part of `content_hash` (tests are not hashed). When
  adding rules to a published task, **bump `version`** in the frontmatter so
  sync applies the change.

#### Test levels

- **`smoke`** — fast, runs on every check (student + server). 3-5 cases.
- **`full`** — comprehensive, runs with `ego check --level full` or
  `ego check --full`. Can be 20+ cases.
- **`all`** — filter keyword meaning "smoke + full".

> **Hypothesis `@scenario`** (property-based tests) is post-MVP (epic 9u7)
> and not yet supported. Use explicit `@case` for now.

### 3.4 `lesson_<slug>.md` — theory card (optional)

A lesson is a short Markdown "card" that explains a concept before the tasks
that need it (catalog layout only; legacy folders ignore `lesson_*.md`).
Lessons are **not** graded: no solution, no tests, no `@case`.

```markdown
---
id: roles-accumulator        # unique across the whole content repo
title: "Накопитель"
order: 2                     # sort inside the folder, default 0
version: "1.0.0"             # informational, default "1.0.0"
---

# Накопитель

Переменная-сумматор хранит результат и растёт в цикле....
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | str | required | Unique lesson id; pattern `[A-Za-z0-9][A-Za-z0-9._-]{0,63}` |
| `title` | str | first `# H1`, else `id` | Human-readable title |
| `order` | int | `0` | Sort inside the folder |
| `version` | str | `"1.0.0"` | Informational only — no SemVer gate |

Link lessons to a task with `theory:` in the task frontmatter (ordered ids):

```yaml
---
id: L03
title: "Сумма в цикле"
version: "1.0.0"
theory: [roles-accumulator, roles-counter]
---
```

Sync rules (see also `CONTENT_CATALOG.md` → *Sync rules (theory cards)*):

- lessons are upserted by id; a changed body/meta is applied in place;
- a lesson whose file disappears is deleted on the next sync of its project;
- a **duplicate lesson id** is a sync error for the second file;
- `theory` is refreshed on every sync and never needs a version bump — a
  theory-only edit does not affect `content_hash` or grading;
- a `theory` id with no matching lesson is a **warning** in the sync log
  (`error_details`), not an error: the task still imports.

Students read lessons through the API: `GET /lessons` (list of
`LessonMeta`) and `GET /lessons/<id>` (adds `body_md`). `TaskMeta.theory`
and the new `project_*` / `folder_*` fields are additive — old clients can
ignore them.

---

## 4. Versioning Policy (SemVer)

Each task has a `version` field (SemVer: `MAJOR.MINOR.PATCH`). The sync
pipeline enforces version bumps when task content changes.

### 4.1 `declare` policy (default for catalog mode)

The author **must explicitly bump** the version in frontmatter when
changing task content. The sync pipeline checks:

| Scenario | Result |
|----------|--------|
| Content unchanged + declared version unchanged | **skipped** (no action) |
| Declared version increased, even with unchanged hash | **updated** (version/metadata/tests are refreshed) |
| Declared version decreased | **error** (version rollback rejected) |
| Content changed + `version` in file > DB version | **updated** |
| Content changed + `version` not bumped | **error** (task skipped, sync log records it) |
| `breaking: true` in frontmatter | prior student progress marked **stale** |
| Major version bump (e.g. `1.x` → `2.x`) | prior student progress marked **stale** |

`content_hash` = SHA-256 of `statement_md + stub_py + solution_py`.
Changing whitespace or comments in the solution **does** change the hash.
Test sidecars are not part of this hash — including `@rules` declarations. In
`declare` mode, bump the task version for test-only changes (new `@case`, new
`@rules`) so sync refreshes the tests; do not rely on hash changes.

### 4.2 `auto_minor` policy (default for legacy fixture)

The sync pipeline **silently bumps** the minor version on any content
change. No explicit version bump required. This is the old behavior for
`docs/tasks/` without YAML.

| Scenario | Result |
|----------|--------|
| Content unchanged | **skipped** |
| Content changed | **updated** (version auto-bumped: `1.0.0` → `1.1.0` → `1.2.0` → ...) |

Use `auto_minor` only for legacy compatibility or rapid prototyping.
**Prefer `declare`** for production content — it prevents accidental
silent changes from invalidating student progress.

### 4.3 When to bump

| Change type | Bump | Example |
|-------------|------|---------|
| Fix typo in statement | patch: `1.0.0` → `1.0.1` | cosmetic |
| Add a test case | minor: `1.0.0` → `1.1.0` | non-breaking |
| Reword statement (same semantics) | minor: `1.0.0` → `1.1.0` | non-breaking |
| Change expected output / function signature | major: `1.0.0` → `2.0.0` | **breaking** |
| Change solution algorithm (same I/O) | minor: `1.0.0` → `1.1.0` | non-breaking |
| Add `breaking: true` to frontmatter | any bump | marks progress stale regardless |

---

## 5. Sync Workflow

### 5.1 Local sync (PR 1 — current)

```bash
# Sync from a local content-repo directory:
ego-server admin sync-tasks --from /path/to/ego-tasks

# Or from docs/tasks/ (legacy):
ego-server admin sync-tasks --from docs/tasks

# With source tag (for sync_log):
ego-server admin sync-tasks --from /path/to/ego-tasks --source cron
```

### 5.2 Via HTTP API

```bash
# Trigger sync (admin only):
curl -X POST http://localhost:8000/admin/sync-tasks \
  -H "Authorization: Bearer <admin-jwt>" \
  -H "Content-Type: application/json" \
  -d '{"path": "/path/to/ego-tasks"}'

# View sync log:
curl http://localhost:8000/admin/sync/log \
  -H "Authorization: Bearer <jwt>"

# Latest sync status:
curl http://localhost:8000/admin/sync/status \
  -H "Authorization: Bearer <jwt>"
```

### 5.3 Sync log

Each sync run writes a row to `sync_log`:

| Column | Description |
|--------|-------------|
| `started_at` / `finished_at` | UTC timestamps |
| `source` | `manual` \| `cron` \| `startup` |
| `repo_url` | Path or URL synced from |
| `git_sha` | Git revision (NULL in PR 1; populated in PR 2) |
| `status` | `success` \| `partial` \| `failed` |
| `added` / `updated` / `skipped` / `errors` | Per-task counts (`LESSON ...` errors included) |
| `error_details` | Newline-separated error and warning lines (incl. `THEORY ...` warnings) |

The `POST /admin/sync-tasks` response also reports lesson counts
(`lessons_added`, `lessons_updated`, `lessons_deleted`); they are not
stored as `sync_log` columns.

---

## 6. Complete Example: Creating a New Task

### Step 1: Add project to `catalog.yaml`

```yaml
schema_version: 1
projects:
  - id: junior-core
    path: projects/junior-core
    enabled: true
```

### Step 2: Create `projects/junior-core/project.yaml`

```yaml
id: junior-core
name: "Junior Core"
version: "1.0.0"
version_policy: declare
```

### Step 3: Create folder `projects/junior-core/folders/block_f_simple/folder.yaml`

```yaml
id: block_f_simple
code: F
name: "Базовые паттерны"
level: easy
```

### Step 4: Create task files

`task_f1.md`:
```markdown
---
id: F1
title: "Найди первый критический баг"
version: "1.0.0"
level: easy
tags: [find, linear-search]
---

# Задача F1: Найди первый критический баг

## Условие

В баг-трекере нужно найти первый критический баг.

## Аргументы

- `bugs` — список словарей с ключами `id`, `severity`, `title`

## Возвращает

Строку — `title` первого бага с `severity == "critical"`, или `""`.
```

`task_f1.solution.py`:
```python
def task_f1_find_critical(bugs):
    for b in bugs:
        if b["severity"] == "critical":
            return b["title"]
    return ""
```

`task_f1.tests.py`:
```python
from ego.testing import case

@case(
    args=([{"id": "B1", "severity": "critical", "title": "Crash"}],),
    expected="Crash",
    description="one critical bug",
    level="smoke",
)
@case(
    args=([],),
    expected="",
    description="empty list",
    level="smoke",
)
@case(
    args=([{"id": "B1", "severity": "minor", "title": "Typo"}],),
    expected="",
    description="no critical",
    level="smoke",
)
def task_f1_find_critical(a0):
    ...
```

### Step 5: Sync

```bash
ego-server admin sync-tasks --from /path/to/ego-tasks
# Output: Sync from /path/to/ego-tasks: added=1, updated=0, skipped=0, errors=0
```

### Step 6: Updating an existing task

When you change task content (statement, solution, or tests):

1. **Bump `version`** in the `.md` frontmatter:
   - Non-breaking change: `1.0.0` → `1.1.0` (minor)
   - Breaking change: `1.0.0` → `2.0.0` (major) or add `breaking: true`
2. Run sync again:
   ```bash
   ego-server admin sync-tasks --from /path/to/ego-tasks
   # Output: added=0, updated=1, skipped=0, errors=0
   ```

If you forget to bump the version:
```
Sync from /path/to/ego-tasks: added=0, updated=0, skipped=0, errors=1
Errors:
  VERSION F1: content changed but version not bumped (file v1.0.0 <= DB v); skipping
```

---

## 7. Naming Conventions

| Entity | Pattern | Example |
|--------|---------|---------|
| Project directory | `projects/<snake_case_id>/` | `projects/junior_core/` |
| Project id | snake_case | `junior_core` |
| Folder directory | `folders/<snake_case_id>/` | `folders/block_f_simple/` |
| Folder id | snake_case (usually `block_<code>_<topic>`) | `block_f_simple` |
| Folder code | short uppercase | `F`, `1`, `A` |
| Task files | `task_<slug>.{md,solution.py,tests.py}` | `task_f1.md` |
| Task id (frontmatter) | uppercase, dot-separated | `F1`, `1.5`, `A3` |
| Task function name | `task_<slug_with_underscores>` | `task_f1_find_critical` |
| Lesson file | `lesson_<slug>.md` | `lesson_roles_accumulator.md` |
| Lesson id (frontmatter) | lowercase, hyphen-separated, unique repo-wide | `roles-accumulator` |

The **slug** in filenames is derived from the task id: `F1` → `f1`,
`1.5` → `1_5`, `A3` → `a3`. The function name extends the slug with a
descriptive suffix: `task_f1_find_critical`.

---

## 8. Validation Checklist

Before syncing a new task, verify:

- [ ] `catalog.yaml` lists the project with `enabled: true`
- [ ] `project.yaml` exists with correct `id` and `version_policy`
- [ ] `folder.yaml` exists with `id`, `code`, and `name`
- [ ] `task_<slug>.md` has YAML frontmatter with `id`, `title`, `version`
- [ ] `task_<slug>.solution.py` has a function named `task_<slug>_*`
- [ ] `task_<slug>.tests.py` has at least one `@case` with `level="smoke"`
- [ ] `args` in `@case` is a **tuple** (note the trailing comma for single-arg cases)
- [ ] `expected` in `@case` matches what the reference solution returns
- [ ] If `@rules` is used: the reference solution obeys the rules itself and the
      starter's `given_*` helpers do not break them
- [ ] Version is `1.0.0` for a new task
- [ ] No `<details>` block in `.md` (use `.solution.py` sidecar instead)
- [ ] Every `theory:` id exists as a `lesson_*.md` with that frontmatter `id`
- [ ] Lesson ids are unique across the whole content repo

---

## 9. Browser editor and docked AI chat

Open **Каталог задач** in the admin console. The explorer shows projects,
folders, tasks and each task's Markdown, reference solution and test sidecars.
Filter by title or task ID and collapse branches to keep the tree manageable.

Files open in Monaco tabs. Switching between tasks keeps their unsaved buffers,
undo history and cursor/scroll position in this browser tab. A dot marks a
modified file. **Сохранить** and **Ctrl/Cmd+S** save all three files of the
active task together; other tasks' drafts remain unsaved. **Проверить** validates
task structure, Python syntax, smoke-case presence and version/etag before
saving. Execution of curriculum cases uses the normal checker workflow.

In `declare` mode, increase the Markdown frontmatter version before saving.
**Версия +patch** explicitly updates the version in the current draft; it does
not save automatically. Choose an appropriate minor/major version manually for
changes that require it. If the server rejects a stale version or etag, the
local buffers remain available. Reloading, reverting or closing a modified file
asks before discarding edits. Leaving the editor also warns about drafts in
other open tasks.

The admin-only AI chat is docked on the right. Hide/reopen or resize it without
losing its input or session; **Диалоги** opens history. A message captures the
currently selected task when sent, and **Остановить** interrupts a streamed
reply. The task context is the saved server content. Review task proposals in
the editor, then validate and explicitly save the candidate. Settings proposals
open the normal Settings review flow. The standalone AI page remains available.

On narrow screens, **Файлы** opens the explorer and selecting a file returns to
the editor. The chat opens as a side overlay. Mentors can browse the files in
read-only mode. Same-user re-login after session expiry preserves in-memory
editor drafts; refreshing/closing the browser tab still requires dealing with
unsaved changes. Persistent draft recovery is a later roadmap stage.

This first editor stage handles the three files belonging to existing tasks.
Full YAML editing and file creation/rename/move are tracked in the next roadmap
stages (`ego-trainer-1f9.2` and `ego-trainer-1f9.3`).

---

## 10. Reference

- **ADR-0016**: Content repository design decisions (`docs/adr/0016-tasks-content-repository.md`)
- **ADR-0001 D3**: SemVer policy for tasks
- **TESTS_DESIGN.md**: `@case` / `@before` / `@after` design rationale
- **Source code**:
  - `ego/catalog.py` — YAML models + parsers
  - `ego/content_repo.py` — repo walker (catalog + legacy)
  - `ego/parser.py` — `.md` → `Task` parser
  - `ego/testing.py` — `@case` / `@rules` decorators
  - `ego/static_rules.py` — static (AST) rule evaluation
  - `ego_server/sync.py` — sync pipeline + SemVer enforcement (incl. theory cards)
  - `ego_server/routers/lessons.py` — `GET /lessons`, `GET /lessons/<id>`
