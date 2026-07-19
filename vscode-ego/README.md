# Ego Trainer

VSCode extension for the Ego practice platform — solve tasks, get auto-checked, track progress.

## Features

- **Task Tree** — sidebar with blocks and tasks, status icons (passed/partial/new)
- **Check Solution** — run your code against tests, see results in a rich panel
- **Pull Tasks** — download task statements and stubs from server
- **Push Progress** — sync your progress to the server
- **Hints** — progressive hints (rules → example → function signature)
- **My Progress** — overview of all tasks with test counts and attempts
- **Status Bar** — current task status at a glance

## Commands

| Command | Description |
|---------|-------------|
| `Ego: Login` | Register/login to ego-server |
| `Ego: Set Server URL` | Configure server endpoint |
| `Ego: Check Current Task` | Run checker on active .py file |
| `Ego: Pull Tasks` | Pull specific block or task from server |
| `Ego: Pull All Tasks` | Pull all tasks from server |
| `Ego: Push Progress to Server` | Sync local progress to server |
| `Ego: List Tasks` | QuickPick with all tasks |
| `Ego: Show Task Statement` | Open .md condition in preview |
| `Ego: Show Hints` | Progressive hints for current task |
| `Ego: My Progress` | Progress table in markdown preview |

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `ego.serverUrl` | `http://localhost:8000` | Ego server URL |
| `ego.autoCheckOnSave` | `false` | Auto-check when saving .py |

## Requirements

- An ego-server instance running (see [ego-trainer](https://github.com/ego-trainer) repo)
- Python 3.11+ on server side

## Architecture

Extension = thin UI. All logic (parser, checker, runner, sandbox) lives on the
ego-server (FastAPI). Extension communicates via HTTP/JSON.

See ADR-0014 in the main repo for architecture details.
