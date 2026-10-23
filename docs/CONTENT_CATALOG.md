# Content catalog: projects, folders, tasks

Companion to [ADR-0016](adr/0016-tasks-content-repository.md) § D16.6.

## Layout

```
ego-tasks/
├── catalog.yaml
└── projects/
    └── <project_id>/
        ├── project.yaml
        └── folders/
            └── <folder_id>/
                ├── folder.yaml
                ├── lesson_<slug>.md          ← optional theory card
                ├── task_<slug>.md
                ├── task_<slug>.solution.py
                └── task_<slug>.tests.py
```

Legacy fixture (`docs/tasks/block_*/` without YAML) imports as:

- project `fixture`
- folder = directory name (`block_f_simple`)
- task meta from H1 + bold lines; version default `1.0.0` + `version_policy: auto_minor`
- no lessons (`lesson_*.md` in a legacy folder is ignored)

## catalog.yaml

```yaml
schema_version: 1
projects:
  - id: junior-core
    path: projects/junior-core
    enabled: true
```

## project.yaml

| Field | Required | Sync → |
|-------|----------|--------|
| `id` | yes | `projects.id` |
| `name` | yes | display name |
| `description` | no | Ops / student catalog |
| `version` | yes | curriculum pack SemVer |
| `order` | no | UI sort (default 0) |
| `tags` | no | filters |
| `version_policy` | no | `declare` (default) \| `auto_minor` |

## folder.yaml

| Field | Required | Sync → |
|-------|----------|--------|
| `id` | yes | `folders.id` / slug |
| `code` | yes | short block code (`F`, `1`, …) → legacy `tasks.block` |
| `name` | yes | display name |
| `description` | no | catalog blurb |
| `order` | no | UI sort inside project |
| `level` | no | easy \| medium \| hard |

## task frontmatter

```yaml
---
id: F1
title: "Найди первый критический баг"
folder: block_f_simple   # optional if matches parent dir
version: "1.1.0"
level: easy
tags: [find, linear search]
breaking: false
theory: [roles-accumulator]   # optional, ordered lesson ids
---
```

| Field | Required | Sync → |
|-------|----------|--------|
| `id` | yes | `tasks.id` |
| `title` | yes | `tasks.title` |
| `version` | yes* | `tasks.version` (*unless `auto_minor`) |
| `level` | yes | `tasks.level` |
| `tags` | no | `tasks.tags` |
| `folder` | no | resolve folder; default = parent dirname |
| `breaking` | no | force stale progress on sync |
| `theory` | no | ordered lesson ids → `tasks.theory` (JSON); not graded |

Body of `.md` = statement (see `TESTS_DESIGN.md`). Solution/tests = sidecars.

## lesson frontmatter (theory cards)

A theory card is a `lesson_<slug>.md` file next to the tasks of a folder.
It has no solution/tests and is never graded; tasks reference it through
`theory: [<lesson id>, ...]`.

```yaml
---
id: roles-accumulator        # unique across the whole content repo
title: "Накопитель"
order: 2                     # sort inside folder, default 0
version: "1.0.0"             # informational, default "1.0.0"
---
<markdown body>
```

| Field | Required | Sync → |
|-------|----------|--------|
| `id` | yes | `lessons.id` (PK; pattern `[A-Za-z0-9][A-Za-z0-9._-]{0,63}`) |
| `title` | no | `lessons.title` (default: first `# H1` of the body, else the id) |
| `order` | no | `lessons."order"` (default 0) |
| `version` | no | `lessons.version` (informational — no SemVer gate) |
| body | — | `lessons.body_md` (markdown after the frontmatter) |

`lessons.content_hash` = sha256 over id/title/order/version + body. There is
no version-bump requirement for lessons: a changed hash is applied in place.
Missing or malformed frontmatter, an unsafe id, or a **duplicate id** (the
second file) is a counted sync error and the card is skipped.

## Three versions (do not mix)

| Name | Where | Meaning |
|------|--------|---------|
| Git revision | server `tasks_repo.ref` → `sync_log.git_sha` | which commit of content-repo is live |
| Project version | `project.yaml` `version` | release of the whole course pack |
| Task version | task frontmatter `version` | SemVer of one task; progress is per this version |

## Sync rules (declare policy)

1. Unchanged `content_hash` → skip task
2. Changed hash + file `version` > DB version → update
3. Changed hash + version not bumped → **error** (task skipped, sync continues with failure count)
4. Major bump or `breaking: true` → mark prior progress `stale`

## Sync rules (theory cards)

1. Lessons are upserted by id; a changed `content_hash` updates the row
   (title/order/version/folder/body). Counts `lessons_added`,
   `lessons_updated`, `lessons_deleted` are reported in the sync result.
2. Lessons of a synced project whose `lesson_*.md` disappeared are **deleted**
   (lessons of other, unsynced projects are untouched).
3. Duplicate lesson id in one repo → **error** for the second card.
4. Task `theory` is refreshed on **every** sync, even when the task hash and
   version are unchanged (a theory-only edit is reported as `updated` and adds
   no `task_versions` row). Theory never triggers the version-bump error.
5. A `theory` id that matches no lesson is a **warning**: one
   `THEORY <task>: lesson '<id>' not found; warning only` line in
   `sync_log.error_details`; the task is imported normally and the error count
   is not incremented.
6. Lessons are synced after a project's tasks, so a new lesson and a task that
   references it can land in the same sync without a warning.
