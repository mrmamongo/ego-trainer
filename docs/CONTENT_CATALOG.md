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
                ├── task_<slug>.md
                ├── task_<slug>.solution.py
                └── task_<slug>.tests.py
```

Legacy fixture (`docs/tasks/block_*/` without YAML) imports as:

- project `fixture`
- folder = directory name (`block_f_simple`)
- task meta from H1 + bold lines; version default `1.0.0` + `version_policy: auto_minor`

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

Body of `.md` = statement (see `TESTS_DESIGN.md`). Solution/tests = sidecars.

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
