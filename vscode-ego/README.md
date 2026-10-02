# Cogito for VS Code

VSCode extension for the Ego practice platform — solve tasks, get auto-checked, track progress.

## Features

- **Cogito sidebar** — separate Activity Bar entry with tasks, statements, progressive hints and results on the left
- **Tutor chat** — native Secondary Side Bar on the right; follows the active task, keeps its conversation, and reads current unsaved code without editing files
- **Check Solution** — run your code against tests; results have a separate tab and a collapsed detailed log
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

- VS Code **1.106+** (native Secondary Side Bar contributions)
- An ego-server instance running (see [ego-trainer](https://github.com/ego-trainer) repo)
- Python 3.11+ on server side

## Layout and sign-in

Open **Cogito** in the Activity Bar. Select a task: its condition stays in the
left sidebar, the Python editor stays in the centre, and `Ego: Учебный ассистент`
opens the chat on the right. VS Code can move these views through its native
view context menu. The extension never rearranges other extensions' views.

Students need server-granted AI access, available budget and configured main
and reviewing models. The sidebar shows why help is unavailable. Model calls,
review before display, billing and understanding defense stay on the server.

Forgejo login returns through the extension's VS Code URI handler. Choosing
**Copy** in the external-link dialog keeps the attempt pending: paste that
same URL into a browser, complete login and allow the return to VS Code.
You can copy the link again or cancel through the login notification. The
attempt expires after at most five minutes; reloading the window requires a
new attempt.

## Architecture

Extension = thin UI. All logic (parser, checker, runner, sandbox) lives on the
ego-server (FastAPI). Extension communicates via HTTP/JSON.

See ADR-0014 in the main repo for architecture details.
