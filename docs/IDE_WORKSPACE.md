# IDE Workspace (/ide)

In-browser personal workspace with code editor, persisted **entirely in the
browser** (IndexedDB, DB `ego-ide`, store `files`). The server is a stateless
provider: JWT auth + task catalog + sandboxed checks. No server-side workspace
state.

## Entry point

- URL: `/ide` (both `/ide` and `/ide/`), shell `ego_server/static/ide.html`,
  no-store cache policy (same as student shell).
- Bundle: `admin-ui/src/ide/main.ts` → esbuild `ideOptions` →
  `ego_server/static/admin/ide.js` (IIFE, shares the admin worker
  `workers/editor.worker.js` and `theme.css`).

## Module layout (admin-ui/src/ide/)

| File | Role |
|---|---|
| `main.ts` | Mount entry — mounts `IdeApp.svelte` into `#app`. |
| `apiCore.js` / `api.ts` | Plain-JS injectable API factory (fetch/storage/event-target) + typed facade. Token key `ego_ide_token`; 401 → `ego:ide-session-expired` event. |
| `workspace.js` | IndexedDB workspace store: files + `::meta` singleton. Factory `createWorkspaceStore(idbFactory)` + browser singleton. |
| `IdeApp.svelte` | Full IDE screen: login gate, file explorer, task search & import, Monaco editor, test panel. |
| `api.test.mjs`, `workspace.test.mjs` | node:test suites (run: `node --test admin-ui/src/ide/api.test.mjs admin-ui/src/ide/workspace.test.mjs`). |

## Server contract (all pre-existing endpoints)

- `POST /auth/login`, `GET /auth/me` — session.
- `GET /tasks` — catalog list for search (client-side filter).
- `GET /tasks/{task_id}` — statement + `stub_py` for import into workspace.
- `POST /check {task_id, student_code}` — sandboxed test run; results panel.

Workspace file records carry an optional `task_id` link — that is what makes
the «Запустить тесты» button work; unlinked files get a task picker.

## Relation to ADR-0017 (collaborative editing)

This IDE is the single-user base layer. The phased collab plan (Yjs rooms
`scenario:taskId:file`) attaches to the same Monaco-per-file model structure;
browser-persisted workspace files become the `pair:` scenario documents in M3.
