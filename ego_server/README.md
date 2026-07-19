# ego_server

FastAPI server for ego platform. See `docs/adr/0001-platform-architecture.md`.

## Run (dev)

```bash
uv run uvicorn ego_server.main:app --reload
```

Default SQLite path: `.ego-server/ego.db` (created on first run).

## Endpoints (skeleton, most return 501)

- `GET  /health` — healthcheck
- `POST /auth/login` — login (501)
- `POST /auth/register` — register (501)
- `GET  /tasks` — list task metadata (501)
- `GET  /tasks/{id}` — full task with content (501)
- `POST /progress/push` — push run result (501)
- `GET  /progress/{student_id}` — mentor view (501)

## Schema

See `schema.sql`. Tables: `tasks`, `task_versions`, `students`, `progress`, `runs`.
