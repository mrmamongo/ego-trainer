# ego-trainer

ego-trainer is a learning platform for practicing programming tasks with an
automated checker. The VS Code extension is the student interface. The web
admin console provides service settings, student progress, a task catalog and
an AI assistant for administrators.

> **Private pilot only.** Do not expose this service to the public internet.
> Student code runs in a subprocess sandbox that does not provide hardened OS
> isolation. Public launch is blocked by Beads issue `ego-trainer-41s`.

## Private pilot quick start

Use a private checkout of the platform repository and a disposable local copy
of the task catalog. The server mounts that catalog read-write because Task
Studio can save reviewed task edits.

1. Create a `.env` file in the repository root with a random
   `EGO_JWT_SECRET` of at least 32 characters, a Fernet-compatible
   `EGO_SETTINGS_ENCRYPTION_KEY`, and an absolute `EGO_CONTENT_PATH` pointing
   to the catalog directory. Keep `.env` out of version control.
2. Start the server and create the first administrator:

   ```sh
   docker compose up -d --build
   docker compose exec ego-server ego-server admin create-user \
     --username admin --password '<unique-strong-password>' --role admin
   ```

3. Open <http://127.0.0.1:8000/> and sign in. Configure the service and,
   optionally, an OpenAI-compatible AI provider under **Settings**.
4. Visit <http://127.0.0.1:8000/health> to confirm the server is responding.

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for secret setup, catalog
mounting, settings behavior, backups and pilot limitations.

## Pilot capabilities

- Create administrator accounts with the server CLI; manage users and review
  student progress in the admin console.
- Mount a local task catalog into the server. The catalog remains file-based;
  The Monaco workspace provides a searchable task-file tree, multi-file tabs,
  per-task drafts and explicit validation/save to the mounted files. See
  [the authoring workflow](docs/TASK_AUTHORING.md#9-browser-editor-and-docked-ai-chat).
- Work alongside the docked admin AI chat while editing tasks. The chat retains
  input/history when hidden and captures the active task when sending a message.
- Change operational settings in the admin console when they are not locked by
  deployment environment variables.
- Connect an OpenAI-compatible chat-completions provider. The admin AI can
  inspect service/catalog context and prepare proposals. An administrator must
  review a proposal and explicitly save it; chat does not directly modify
  settings or task files.
- Use the VS Code extension as the student-facing task interface.

## Content source and sync status

For a pilot, use a local catalog directory mounted at `/content`. The platform
repository's `docs/tasks/` remains a development fixture; it is not the
production canonical source. Keep the mounted directory under version control
and back it up separately from the server database.

Remote Git fetch/checkout, repository authentication and scheduled sync are
not implemented yet (`ego-trainer-8di.2`). Do not assume that changing a Git
branch or pushing a commit will update a running pilot. Sync the mounted local
catalog explicitly after updating it.

## Documentation

- [Private pilot deployment](docs/DEPLOYMENT.md)
- [Architecture decisions](docs/adr/)
- [Task format](docs/TESTS_DESIGN.md)
