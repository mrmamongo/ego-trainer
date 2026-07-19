# ADR-0015: VSCode Extension UI Flow

**Status:** Accepted
**Date:** 2026-07-20
**Related:** ADR-0014, beads `ego-trainer-8bv.9` (+ subtasks)

## Context

ADR-0014 определил VSCode extension как primary UI, но не описал конкретный
user flow. После обсуждения с пользователем зафиксированы решения:

1. **Init wizard + Dashboard = custom HTML webview** (не native VSCode panels)
2. **Task view = webview** только для условия .md + логов/результатов.
   Код пользователь пишет в обычном VSCode .py editor.
3. **TreeView sidebar** для навигации (блоки → задачи)
4. **Auto welcome** при первом запуске + `Ego: Init` из Command Palette
5. **Mode switcher:** Server ↔ Offline (fallback)
6. **Dashboard = rich webview** со сводкой, фильтрами, таблицей задач

## Decision

### 1. First Launch → Welcome

Auto-open welcome webview когда: нет токена в SecretStorage ИЛИ нет `.ego/`
в workspace. 3 кнопки: Connect to Server / Use Offline / Skip.

```
┌─────────────────────────────────────────────────────────────┐
│ 1. FIRST LAUNCH (no .ego/, no token)                        │
│                                                             │
│    [Welcome webview]                                        │
│    ┌──────────────────────────────────┐                     │
│    │  Welcome to Ego Trainer          │                     │
│    │                                  │                     │
│    │  [ Connect to Server ]  → .9.2   │                     │
│    │  [ Use Offline ]        → .9.3   │                     │
│    │  [ Skip for now ]                │                     │
│    └──────────────────────────────────┘                     │
└─────────────────────────────────────────────────────────────┘
```

### 2. Init Wizard → Dashboard

После init (server или offline) **Dashboard открывается автоматически** —
первое что видит пользователь.

```
┌─────────────────────────────────────────────────────────────┐
│ 2. INIT WIZARD                                              │
│                                                             │
│  Server mode (.9.2):           Offline mode (.9.3):         │
│  ┌──────────────────┐          ┌──────────────────┐         │
│  │ 1. Server URL    │          │ 1. Scan docs/    │         │
│  │ 2. Health check  │          │    tasks/        │         │
│  │ 3. Login/Register│          │ 2. Create .ego/  │         │
│  │ 4. Token → Secret│          │ 3. Build manifest│         │
│  │ 5. Create .ego/  │          │ 4. Done          │         │
│  │ 6. Pull all tasks│          │                  │         │
│  │ 7. Done          │          │                  │         │
│  └──────────────────┘          └──────────────────┘         │
│         ↓ health fail ↓                                      │
│    "Server unreachable → Use Offline?" → .9.3               │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. DASHBOARD (opens automatically after init)   .9.5       │
│                                                             │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Ego Trainer          [Server] badge               │    │
│  │                                                    │    │
│  │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐               │    │
│  │  │  12  │ │  3   │ │  5   │ │  20  │               │    │
│  │  │passed│ │partial│ │ new  │ │total │               │    │
│  │  └──────┘ └──────┘ └──────┘ └──────┘               │    │
│  │  ████████████░░░░░░░  60% complete                 │    │
│  │                                                    │    │
│  │  Filter: [Block ▼] [Status ▼]                     │    │
│  │                                                    │    │
│  │  ┌─────┬───────────────┬──────┬───────┬─────────┐  │    │
│  │  │Task │ Title         │Status│Tests  │Actions  │  │    │
│  │  ├─────┼───────────────┼──────┼───────┼─────────┤  │    │
│  │  │ F1  │ Find critical │  ✓   │ 3/3   │Open Hints│  │    │
│  │  │ F2  │ Sanitize str  │  ◐   │ 1/3   │Open Hints│  │    │
│  │  │ F3  │ Join tables   │  ○   │ new   │Open Hints│  │    │
│  │  └─────┴───────────────┴──────┴───────┴─────────┘  │    │
│  │                                                    │    │
│  │  [ Pull All ]  [ Push Progress ]                  │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### 3. Task View: .py editor + webview

Клик на задачу (в Dashboard или TreeView) → открывает .py stub в editor
(Column 1) + Task view webview (Column 2). Код пишет в editor, не в webview.

```
┌─────────────────────────────────────────────────────────────┐
│ 4. TASK VIEW (click task in Dashboard or TreeView)  .9.6   │
│                                                             │
│  ┌─────────────────────┐  ┌────────────────────────────┐   │
│  │ Editor (Col 1)      │  │ Task view webview (Col 2)  │   │
│  │                     │  │                            │   │
│  │ task_f1.py          │  │ F1: Find critical bug      │   │
│  │                     │  │ Status: ✓ passed           │   │
│  │ def task_f1(bugs):  │  │ ─────────────────────────  │   │
│  │     # your code     │  │ ## Условие                 │   │
│  │     pass            │  │ В баг-трекере нужно...     │   │
│  │                     │  │                            │   │
│  │ ← user writes here  │  │ ## Пример                  │   │
│  │                     │  │ ```python                  │   │
│  │                     │  │ task_f1(bugs)              │   │
│  │                     │  │ # -> "Crash on login"      │   │
│  │                     │  │ ```                        │   │
│  │                     │  │ ─────────────────────────  │   │
│  │                     │  │ [Hint 1] [Hint 2] [Hint 3] │   │
│  │                     │  │  ↓ click reveals           │   │
│  │                     │  │  Правила: верни title...   │   │
│  │                     │  │ ─────────────────────────  │   │
│  │                     │  │ [Check]  [Open .py]        │   │
│  │                     │  │ ─────────────────────────  │   │
│  │                     │  │ Results (after check):     │   │
│  │                     │  │  ✓ test 1: basic           │   │
│  │                     │  │  ✗ test 2: empty list      │   │
│  │                     │  │    Expected: ""            │   │
│  │                     │  │    Got: None               │   │
│  └─────────────────────┘  └────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 4. Check Flow

Check запускается из Task view webview (кнопка) ИЛИ из Command Palette.
Результаты — в Task view (если открыт) или в отдельном panel (если закрыт).

```
┌─────────────────────────────────────────────────────────────┐
│ 5. CHECK FLOW                                              │
│                                                             │
│  [Check button in Task view]                                │
│  OR [Ego: Check command]                                    │
│  OR [status bar click → Dashboard → Open → Check]            │
│                          ↓                                  │
│  Server mode: POST /check → sandbox → CheckResponse          │
│  Offline mode: python -m ego check --local → CheckResult    │
│                          ↓                                  │
│  Results appear:                                            │
│    - In Task view webview (if open) ← primary               │
│    - In separate Test Results panel (if Task view closed)   │
│    - Status bar updates: "Ego: Server | F1 ✓ 3/3"           │
│    - TreeView icon updates: F1 → ✓                          │
│    - Dashboard table updates (on next refresh)              │
└─────────────────────────────────────────────────────────────┘
```

### 5. Hints: Progressive Reveal

3 кнопки в Task view: Hint 1 / Hint 2 / Hint 3. Клик раскрывает текст,
остаётся видимым. Reset при смене задачи.

```
[Hint 1] [Hint 2] [Hint 3]
 ↓ click Hint 1
 Правила: верни title первого critical бага...
 ↓ click Hint 2
 Пример: task_f1(bugs) -> "Crash on login"
 ↓ click Hint 3
 Сигнатура: def task_f1_find_critical(bugs: list[dict]) -> str
```

Levels: 1 = Правила, 2 = Пример, 3 = Сигнатура функции.

### 6. Persistent Elements

```
┌─────────────────────────────────────────────────────────────┐
│ 6. PERSISTENT ELEMENTS                                     │
│                                                             │
│  Sidebar (TreeView) .9.7:                                   │
│    ▾ Block F (3 tasks)                                      │
│       ✓ F1  3/3                                             │
│       ◐ F2  1/3                                             │
│       ○ F3  new                                             │
│    ▾ Block H (8 tasks)                                      │
│       ...                                                   │
│    Right-click: Open / Check / Hints / Pull                 │
│                                                             │
│  Status bar .9.8:                                           │
│    "Ego: Server | F1 ✓ 3/3"  ← click → Dashboard            │
│                                                             │
│  Mode switcher .9.4:                                        │
│    "Ego: Switch Mode" → Server / Offline                    │
│    Auto-fallback if server unreachable                      │
└─────────────────────────────────────────────────────────────┘
```

## Consequences

- **Init wizard + Dashboard = custom HTML** — больше кода, но полный
  контроль над UX. Не ограничены native VSCode panels.
- **Task view = webview для условия + результатов** — код в обычном
  editor. Пользователь получает LSP, autocomplete, git integration.
- **TreeView остаётся** для навигации — дёшево, нативно, привычно.
- **Mode switcher** — Server primary, Offline fallback. Переключение
  через команду, auto-fallback при недоступности сервера.
- **Status bar click → Dashboard** (не check) — dashboard = центральный
  hub.

## UI Framework: Svelte

Webview UI реализуется на **Svelte** (не vanilla JS, не React).

- **Почему Svelte:** компилируется в vanilla JS (~10KB), реактивность из
  коробки, простой синтаксис, маленький bundle.
- **Bundler:** esbuild (через `svelte-preprocess` + `esbuild-svelte`).
  Build шаг: `npm run compile` собирает .svelte → out/webview/.
- **CSP:** VSCode webview требует nonce для scripts. Svelte bundle
  подключается с nonce, inline styles разрешены.
- **Communication:** webview ↔ extension через `acquireVsCodeApi()`
  + `postMessage()`. Svelte store для state management.
- **Структура:**
  ```
  vscode-ego/src/
    extension.ts          # activate, commands
    api.ts                # HTTP client
    treeProvider.ts       # TreeView (native, не Svelte)
    webview/
      welcome.svelte      # Welcome screen
      dashboard.svelte    # Dashboard
      taskView.svelte     # Task view (condition + hints + results)
      results.svelte      # Test results (embedded in taskView)
      shared/
        store.ts          # Svelte store (state from extension)
        api.ts            # postMessage wrapper
  ```
- **Build:** `npm run compile` → tsc (extension) + esbuild (svelte)
  → `out/extension.js` + `out/webview/*.js`

## Implementation tasks (beads 8bv.9)

| Subtask | Priority | Description |
|---------|----------|-------------|
| .9.1 | P1 | Welcome webview (auto-open) |
| .9.2 | P1 | Init wizard: server mode |
| .9.3 | P1 | Init wizard: offline mode |
| .9.4 | P2 | Mode switcher |
| .9.5 | P1 | Dashboard webview |
| .9.6 | P1 | Task view webview |
| .9.7 | P2 | TreeView sidebar polish |
| .9.8 | P2 | Status bar |
| .9.9 | P2 | Offline check (Python in PATH) |

Dependencies:
```
.1 Welcome ──→ .2 Init server ──→ .5 Dashboard
                          └──→ .6 Task view
            ──→ .3 Init offline ──→ .9 Offline check
                          └──→ .4 Mode switcher ←── .2
.7 TreeView (independent)
.8 Status bar (independent)
```
