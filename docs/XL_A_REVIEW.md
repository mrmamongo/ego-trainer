# XL-A: review and grading contracts

Date: 2026-10-02. Scope: XL-A01–XL-A27 and their Cogito import/check path.

The source pack remains nine independent `student.py` mini-stories. The
`docs/tasks/XL-A/catalog/` export contains the publishable catalog, explicit
starters, reference implementations and smoke/full cases. Deliberate starter
bugs remain present. XL-A25 is a behavior-preserving refactoring exercise;
passing its tests does not establish that the refactoring was completed.

## External review

The requested Bifrost/Pi review used an isolated snapshot at repository
revision `9eadfa0`. MiMo V2.6 Pro produced no review before its ten-minute
budget; the process was terminated after 748 seconds. This is a technical
timeout, not a verdict on review reasoning.

After explicit user approval, `deepseek/deepseek-flash` completed a second
Pi opinion run. Model Eval Hub run: `0e0b5c35-274a-41ec-b61b-ff094dd105db`.
Reported duration: 404 seconds; 70,081 input tokens, 16,380 output tokens,
46 tool calls and four tool errors. Monetary cost was not reported.

The reviewer returned its opinion in the transcript rather than the requested
`REVIEW.md`, and omitted the requested 27-row coverage matrix. The parent
reviewed the claims and independently checked the generated tests/references.

| Review claim | Parent assessment | Result |
| --- | --- | --- |
| A02 old contiguous-tail code differs from pinned context | Deliberate modification baseline; already explained in its contract | Preserve starter; keep helper-independent exported task |
| Source group header defines an incomplete shared chunk shape | Incorrect: the header defines no shared chunk schema; A11 explicitly requires `tokens` | No invented cross-task input requirement |
| A13 combined lookup errors deserve an explicit case | Useful coverage suggestion; business checks require both lookups to succeed | Test lookup/validation ordering and full/already-joined precedence |
| A12 empty and repeated unknown references deserve boundary cases | Useful coverage suggestion; behavior already specified | Include explicit empty, duplicate and unknown-source cases |
| A27 cached steps should bypass argument-reference resolution | Useful clarification | Clarify original contract; test cached announcement after a noncritical dependency failure |
| A22 fails to specify replacing a dictionary leaf with a scalar | Incorrect: the contract explicitly names a final dictionary as `path_conflict` | Keep rule; test the conflict without silently widening valid input |
| A24 needs input-mutation checks | Correct grading requirement; deep copying is already part of the contract | Observe inputs and returned-object isolation in the subprocess |
| A05 starter can duplicate reward IDs | The intentionally seeded bug | Smoke must reject that starter |

The opinion is accepted with repair: it contributed a concrete clarification
and coverage suggestions, but contained incorrect claims and missed delivery
requirements. It is not evidence for changing model routing preferences.

An independent review of the completed tests also found missing isolation
assertions in A19 and A25. These were added: intentionally broken variants
that return the original input containers on rejection are now rejected in
three and nine cases respectively. The references still pass, as does the
behavior-preserving A25 starter.

## Platform changes needed for fair grading

- Explicit `.student.py` sidecars preserve intentional bugs, modification
  baselines and GIVEN helpers in the code delivered to students.
- Opt-in value comparison ignores dictionary insertion order while preserving
  scalar/container types and sequence ordering. Legacy repr comparison remains
  the default. A16 shortage-key ordering is presentation guidance.
- Opt-in input observation catches mutation even when the return value matches.
- Alias fixtures reconstruct shared nested objects inside the subprocess;
  output-isolation checks detect shallow return copies where the task forbids them.
- Helper composition and refactoring quality remain manual review criteria.

## Catalog transition

The requested visible catalog is XL-A only. Existing source files, task rows,
task versions, progress and run history must remain intact. Project/task
archive flags hide older content from catalog listings and assistant search;
historical task access remains available. Activating old projects restores
their visibility. Import must succeed before the visible-project set changes.

## Verified release

Published to `https://cogito.born-in-july.ru` on 2026-10-02.

| Check | Result |
| --- | --- |
| Catalog | 27 tasks, nine folders; nine bug, nine modification, nine new-code tasks |
| Reference implementations | 287/287 cases: 81 smoke and 206 full |
| Learner starters | 81 smoke executions; all unfinished tasks rejected, A25 behavior accepted |
| Linux release image | Complete corpus passed; final A19/A25 isolation changes also passed with negative controls |
| Parser/import/task API fixtures | 51 passed |
| Checker, runner, decorated cases, archive and sync regressions | 138 passed in the combined Windows run; one legacy subprocess case was partial, then passed on its isolated rerun |
| Studio validate/save, including explicit starter preservation | 61 passed, two skipped |
| Ruff | Passed for changed implementation, validation scripts and catalog code |
| Live API | Exactly XL-A01–XL-A27; nine folders; learner solution access remains hidden |
| Preserved records | 33 old tasks and versions, two progress rows and two run rows; checksums verified across 23 protected table snapshots |
| Preserved source | All 108 existing source files unchanged |
| Service | Container healthy; public HTTPS `/health` returned `ok` |

The release image is `ego-trainer:xl-a-20261002`, based on the then-current
`ego-trainer:cogito-admin-68ea1dd`. Only the checker/parser/catalog changes
were overlaid; the existing administration interface is inherited from that
deployed image. New content is mounted separately at `/content/projects/xl-a`.

The server backup is `/opt/cogito/backups/xl-a-20261002T183817Z/`: SQLite
backup, previous catalog/content, compose configuration and image marker.
Private configuration remains on the server. The transition record verifies
the import (27 added, zero errors) and old-record checksums. Old project
`junior` is disabled in `catalog.yaml` and archived in the database.

To repeat local validation:

```console
python scripts/build_xl_a_catalog.py --check
python -m scripts.verify_xl_a_catalog
```

On a slow Windows host, `--timeout 10` gives each subprocess additional startup
time. The production runner and the Linux verification use the default five
seconds. Structural requirements such as helper composition and refactoring
quality still need mentor review.

Beads task `ego-trainer-23g` is closed. The configured database has no Dolt
remote, so `bd dolt push` could not run; this pre-existing setup issue is
tracked by `ego-trainer-hf8`. A selected export of this release's closed task
is preserved in `.beads/xl-a-release-issue.jsonl` and published with the code.
