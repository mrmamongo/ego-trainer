# ADR-0017: Collaborative Editing (Yjs + Monaco)

**Status:** Proposed (Phase 0 spike — pending implementation)
**Date:** 2026-10-06
**Related:** ADR-0014 (VSCode = primary UI), ADR-0016 (content repo + sync), beads: TBD

## Context

Платформа имеет два веб-фронта, оба раздаются `ego-server`:

- **Mentor admin (`admin-ui/`)** — Svelte 5 + esbuild. Monaco 0.52.2 уже
  интегрирован ([MonacoEditor.svelte](../../admin-ui/src/components/MonacoEditor.svelte)):
  один editor, модель на документ (`ego:///<id>`), Ctrl+S, тема `cogito-dark`.
  Task Studio редактирует `markdown / solution_py / tests_py` через
  `GET/PUT /admin/tasks/{id}/studio` с оптимистичной конкуренцией
  (`expected_version` + `expected_content_etag`, 409 на конфликт).
- **Student web UI (`ego_server/static/student*.js`)** — vanilla JS, код задачи
  read-only (`<pre>`), студенты решают в VS Code extension (ADR-0014).

Совместного редактирования нет; параллельная правка задачи двумя менторами
сегодня = гонка, которую ловит только etag-409 на save.

Три целевых сценария (поэтапно):

1. **M1 — менторы в Task Studio** (Monaco уже живёт здесь);
2. **M2 — ментор + студент** (совместный разбор решения студента);
3. **M3 — студенты вместе** (парное программирование, требует модерации).

## Decision

### D17.1. Стек: Yjs CRDT + y-monaco + ypy-websocket

**Decision:** Совместное редактирование строим на **Yjs** (CRDT) с привязкой
**y-monaco** (`MonacoBinding`) и серверным хабом **ypy-websocket** (Python,
ASGI), смонтированным как sub-app в существующий FastAPI.

**Rationale:**

- Yjs — де-факто стандарт CRDT; схождение без центрального lock-сервера,
  оффлайн-толерантность, компактный wire-формат (~30KB gz в бандле).
- `MonacoBinding` из y-monaco синхронизирует `Y.Text` ↔ Monaco model и даёт
  awareness: remote-курсоры/селекшены с именами и цветами.
- `ypy-websocket` — ASGI-приложение (так работает Jupyter Collaboration в
  проде): комнаты per-document, awareness-релей, персист опционален.
  Монтирование в существующий uvicorn-процесс → **без нового Node-сервиса и
  нового контейнера** (см. D17.4).
- Альтернативы отклонены:
  - **OT (ShareDB/ot.js)** — требует центральной очереди операций и
    transform-функций для каждого клиента; Yjs даёт схождение без них.
  - **Automerge** — экосистема Monaco-биндингов слабее.
  - **Liveblocks/PartyKit (SaaS)** — внешний вендор и данные студентов наружу.

### D17.2. Коллаб-документ ≠ канонический файл; сохранение через Studio API

**Decision:** Yjs-документ — это **draft-слой**, живущий только в коллаб-сессии.
Коммит в канонический content-repo идёт через существующий
`PUT /admin/tasks/{id}/studio` (validate → etag-check → атомарная запись → sync),
без изменений OCC-семантики.

**Rationale:** Yjs убирает конфликты *внутри сессии* (параллельный набор
сходится CRDT-ом), а OCC-etag по-прежнему защищает от правки канона *мимо*
коллаба (например, через git push в content-repo между сессиями). Не
изобретаем вторую систему версионирования: SemVer задач и etag остаются
единственным источником правды о том, что «сохранено».

### D17.3. Комнаты: room = `taskId::fileKey`, addressed per scenario

**Decision:** Формат комнаты — `scenario:taskId:fileKey`, где `scenario ∈
{studio, defense, pair}`:

- `studio:...` — файлы задач Task Studio (M1);
- `defense:...` — разбор решения студента (M2);
- `pair:...` — парное программирование (M3).

Каждая комната: свой Y.Doc, awareness, TTL-политика (жизнь без клиентов →
snapshot → выгрузка), макс. размер.

**Rationale:** Один формат адресации на все три сценария с первого дня, чтобы
M2/M3 не ломали M1. `taskId::file` (как ключ вкладок в EditorWorkspace)
совпадает с `docKey()` — не плодим вторую схему идентификаторов.

### D17.4. Транспорт: ws-эндпоинт `/collab/{room}` в существующем uvicorn

**Decision:** `ypy-websocket` монтируется на `/collab/{room}` внутри
`ego_server.main:app`. Аутентификация — существующий JWT (query-param `token`
или первый message), авторизация ролей per-scenario: `studio` → mentor/admin,
`defense` → mentor/admin + владелец-студент, `pair` → студенты.

**Rationale:** `uvicorn[standard]` (websockets) уже в зависимостях;
отдельный Node-процесс для коллаба не нужен (Jupyter Collaboration —
прецедент «Python-only» коллаб-стека в проде). TrustedHost/CORS не мешают
ws-upgrade. JWT в query-param логируется — скоординировать с политикой логов.

### D17.5. Персист: in-memory + снапшоты Y-state в SQLite

**Decision:** Дефолт — комнаты в памяти процесса; при закрытии комнаты
(последний клиент ушёл) Y-state снапшотится в таблицу `collab_drafts`
(room, ydoc state, updated_at). При следующем открытии комнаты state
загружается из снапшота. Snapshot ≤ каждые N минут при активности.

**Rationale:** Для M1 (десятки менторов) SQLite-снапшоты достаточны; полноценный
ystore (LevelDB/Redis) — отложенная оптимизация, интерфейс снапшотов оставляем
единым, чтобы подключить без переделки комнат.

### D17.6. Фазы

| Phase | Scope | Exit criteria |
|---|---|---|
| **P0 spike** | Зависимости; `/collab/{room}` echo-хаб без auth; `MonacoBinding` на активную модель в Studio; 2 вкладки браузера сходятся | Ручной smoke: два окна, один док, курсоры видны, текст сходится после refresh/reconnect |
| **P1 MVP** | JWT-auth на ws; комнаты `studio:*`; presence (имя/роль/цвет); снапшоты в `collab_drafts`; UI: «кто в документе», индикатор unsaved-collab | Два ментора редактируют одну задачу; save через Studio API проходит; etag-409 сценарий протестирован |
| **P2 UX** | Remote cursors & selections; follow-mode; «коммит из коллаба» (validate+save пайплайн из черновика); reconnect (уведомления, авто-реверс) | UX-ревью менторами |
| **P3 M2/M3** | Сценарии `defense:*` (студенческий UI получает Monaco), `pair:*` + модерация | Ревью сценария с курсовым составом |

### D17.7. Риски

- **y-monaco ↔ monaco 0.52 совместимость** — закрывается спайком P0.
- **Awareness over query-param JWT** — токен в URL попадает в логи; вариант:
  первый ws-message auth или cookie. Решение — в P1.
- **Мульти-воркер uvicorn** — комнаты прибиты к процессу; для M1 (1 worker)
  ок, горизонтальное масштабирование потребует Redis pub/sub — отложено.
- **Студенческий UI без сборки** — Monaco в студенческий UI попадёт через
  static import-map или мини-bundle; детали в P3 (может пересечься с планом
  миграции student UI на Svelte).
- **bd недоступен в этой копии репо** (legacy Dolt workspace от bd 0.62.0,
  требуется миграция) — beads-таски на фазы не заведены; завести после
  `bd` migration.

## Consequences

- Коллаб-сессии не конфликтуют с OCC-save: коммит — явное действие через
  Studio API, collab-state не «сохраняется» сам по себе.
- Присутствие (presence) и курсоры — чисто клиентский awareness, сервер
  только релеит.
- Добавляется таблица `collab_drafts` (миграция schema.sql) и ws-роут;
  канонический pipeline (parse → DB → sync) не меняется.
- VS Code extension (ADR-0014) не затрагивается; интеграция коллаба туда —
  отдельное решение (возможно Yjs over ws в extension host).
