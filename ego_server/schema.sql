-- Ego server schema (SQLite).
-- See docs/adr/0001-platform-architecture.md (D7, D8, D10)
-- and docs/adr/0016-tasks-content-repository.md (D16.6 catalog).
-- Idempotent: all statements use IF NOT EXISTS.

-- === Catalog (ADR-0016 D16.6) ===

-- Учебный курс / трек (один «продукт» контента)
CREATE TABLE IF NOT EXISTS projects (
  id           TEXT PRIMARY KEY,           -- 'junior-core' (стабильный id = path slug)
  name         TEXT NOT NULL,
  description  TEXT NOT NULL DEFAULT '',
  version      TEXT NOT NULL DEFAULT '1.0.0',  -- SemVer релиза курса (пакет)
  "order"      INTEGER NOT NULL DEFAULT 0,     -- UI sort (quoted: reserved word)
  default_locale TEXT NOT NULL DEFAULT 'ru',
  tags         TEXT NOT NULL DEFAULT '[]', -- JSON array as text
  version_policy TEXT NOT NULL DEFAULT 'declare',  -- declare | auto_minor
  created_at   TEXT NOT NULL,
  updated_at   TEXT NOT NULL
);

-- Тематический блок внутри проекта (бывш. block_*)
CREATE TABLE IF NOT EXISTS folders (
  id           TEXT NOT NULL,              -- 'block_f_simple' (slug директории)
  project_id   TEXT NOT NULL,              -- FK -> projects.id
  code         TEXT NOT NULL,              -- 'F', '1', 'A' (короткий код блока)
  name         TEXT NOT NULL,
  description  TEXT NOT NULL DEFAULT '',
  "order"      INTEGER NOT NULL DEFAULT 0, -- 'order' reserved in some SQL dialects
  level        TEXT,                       -- easy | medium | hard (nullable)
  created_at   TEXT NOT NULL,
  updated_at   TEXT NOT NULL,
  PRIMARY KEY (id, project_id)
);

-- Канонический контент задач (meta, контент в git .md)
CREATE TABLE IF NOT EXISTS tasks (
  id           TEXT PRIMARY KEY,           -- 'F1', '1.5', 'A', etc.
  block        TEXT NOT NULL,              -- 'F', '1', 'A', ... (legacy: = folder.code)
  slug         TEXT NOT NULL,              -- 'block_f_simple' (legacy: = folder.id)
  task_id      TEXT NOT NULL,              -- 'F1', '1.5' (= id, duplicated for API)
  title        TEXT NOT NULL,
  level        TEXT NOT NULL,              -- 'easy' | 'medium' | 'hard'
  tags         TEXT NOT NULL DEFAULT '[]', -- JSON array as text
  version      TEXT NOT NULL,              -- SemVer: '1.0.0'
  content_hash TEXT NOT NULL,              -- sha256(statement+stub+solution)
  breaking     INTEGER NOT NULL DEFAULT 0, -- 0/1, последнее изменение breaking?
  md_path      TEXT NOT NULL,              -- относительный путь к .md в git-репо сервера
  folder_id    TEXT,                       -- FK -> folders.id (nullable for legacy)
  project_id   TEXT,                       -- FK -> projects.id (nullable for legacy)
  created_at   TEXT NOT NULL,              -- ISO 8601
  updated_at   TEXT NOT NULL,
  UNIQUE(block, task_id)
);

-- История версий (для отката и объяснимости прогресса)
CREATE TABLE IF NOT EXISTS task_versions (
  task_id      TEXT NOT NULL,              -- FK на tasks.id (без FK в SQLite для простоты)
  version      TEXT NOT NULL,
  content_hash TEXT NOT NULL,
  breaking     INTEGER NOT NULL DEFAULT 0,
  md_path      TEXT NOT NULL,
  created_at   TEXT NOT NULL,
  PRIMARY KEY (task_id, version)
);

-- Студенты
CREATE TABLE IF NOT EXISTS students (
  id            TEXT PRIMARY KEY,          -- UUID
  username      TEXT NOT NULL UNIQUE,
  role          TEXT NOT NULL,             -- 'student' | 'mentor' | 'admin'
  password_hash TEXT NOT NULL,             -- bcrypt
  created_at    TEXT NOT NULL,
  last_login_at TEXT
);

-- Stable external identity; names/emails never implicitly link local accounts.
CREATE TABLE IF NOT EXISTS external_identities (
  issuer        TEXT NOT NULL,
  subject       TEXT NOT NULL,
  user_id       TEXT NOT NULL REFERENCES students(id) ON DELETE CASCADE,
  remote_username TEXT NOT NULL,
  created_at    TEXT NOT NULL,
  PRIMARY KEY (issuer, subject),
  UNIQUE (issuer, user_id)
);

-- Five-minute OAuth handoff. Provider tokens are never stored here.
CREATE TABLE IF NOT EXISTS oauth_flows (
  state_hash    TEXT PRIMARY KEY,
  issuer        TEXT NOT NULL,
  client_id     TEXT NOT NULL,
  redirect_uri  TEXT NOT NULL,
  verifier      TEXT NOT NULL,
  challenge     TEXT NOT NULL,
  browser_hash  TEXT,
  callback_port INTEGER,
  ticket_hash   TEXT,
  phase         TEXT NOT NULL DEFAULT 'pending',
  user_id       TEXT REFERENCES students(id) ON DELETE CASCADE,
  expires_at    INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS mentor_grants (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  actor_id      TEXT NOT NULL,
  user_id       TEXT NOT NULL,
  created_at    TEXT NOT NULL
);

-- Прогресс (per-version — решено для конкретной версии задачи)
CREATE TABLE IF NOT EXISTS progress (
  student_id   TEXT NOT NULL,
  task_id      TEXT NOT NULL,
  version      TEXT NOT NULL,              -- на какой версии задачи сдавал
  status       TEXT NOT NULL,              -- 'new' | 'partial' | 'passed' | 'stale'
  attempts     INTEGER NOT NULL DEFAULT 0,
  passed_tests INTEGER NOT NULL DEFAULT 0,
  total_tests  INTEGER NOT NULL DEFAULT 0,
  last_run_at  TEXT,
  PRIMARY KEY (student_id, task_id, version)
);

-- Логи прогонов (для ментора)
CREATE TABLE IF NOT EXISTS runs (
  id            TEXT PRIMARY KEY,          -- UUID
  student_id    TEXT NOT NULL,
  task_id       TEXT NOT NULL,
  version       TEXT NOT NULL,
  solution_hash TEXT NOT NULL,             -- sha256 решения студента
  status        TEXT NOT NULL,             -- 'passed' | 'failed' | 'error' | 'timeout'
  log           TEXT NOT NULL,             -- stdout/stderr, обрезано (например, до 8KB)
  created_at    TEXT NOT NULL
);

-- === Sync log (ADR-0016 D16.2) ===
-- Каждый запуск sync-tasks (cron/manual) пишет строку сюда.
CREATE TABLE IF NOT EXISTS sync_log (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  started_at    TEXT NOT NULL,               -- ISO 8601
  finished_at   TEXT,                        -- NULL пока идёт sync
  source        TEXT NOT NULL,               -- 'manual' | 'cron' | 'startup'
  repo_url      TEXT NOT NULL DEFAULT '',    -- что синкали (file:// path или git URL)
  git_sha       TEXT,                        -- revision content-repo (PR 2: git; PR 1: NULL)
  status        TEXT NOT NULL DEFAULT 'running',  -- running | success | failed | partial
  added         INTEGER NOT NULL DEFAULT 0,  -- new tasks inserted
  updated       INTEGER NOT NULL DEFAULT 0,  -- existing tasks updated
  skipped       INTEGER NOT NULL DEFAULT 0,  -- unchanged (content_hash match)
  errors        INTEGER NOT NULL DEFAULT 0,  -- parse/upsert failures
  error_details TEXT NOT NULL DEFAULT ''     -- multiline: per-task errors
);

CREATE INDEX IF NOT EXISTS idx_progress_student ON progress(student_id);
CREATE INDEX IF NOT EXISTS idx_progress_task ON progress(task_id);
CREATE INDEX IF NOT EXISTS idx_runs_student ON runs(student_id);
CREATE INDEX IF NOT EXISTS idx_runs_task ON runs(task_id);
CREATE INDEX IF NOT EXISTS idx_tasks_block ON tasks(block);
CREATE INDEX IF NOT EXISTS idx_tasks_folder ON tasks(folder_id);
CREATE INDEX IF NOT EXISTS idx_tasks_project ON tasks(project_id);

CREATE TABLE IF NOT EXISTS service_settings (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  revision INTEGER NOT NULL,
  config_json TEXT NOT NULL,
  api_key_encrypted TEXT NOT NULL DEFAULT '',
  updated_at TEXT NOT NULL,
  updated_by TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS admin_chat_sessions (
  id TEXT PRIMARY KEY,
  owner_id TEXT NOT NULL REFERENCES students(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_chat_owner ON admin_chat_sessions(owner_id, updated_at);

CREATE TABLE IF NOT EXISTS admin_chat_messages (
  id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL REFERENCES admin_chat_sessions(id) ON DELETE CASCADE,
  role TEXT NOT NULL,
  content TEXT NOT NULL DEFAULT '',
  status TEXT NOT NULL DEFAULT 'complete',
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_chat_messages ON admin_chat_messages(session_id, created_at);
CREATE UNIQUE INDEX IF NOT EXISTS idx_chat_active ON admin_chat_messages(session_id)
  WHERE status = 'streaming';

CREATE TABLE IF NOT EXISTS admin_chat_proposals (
  id TEXT PRIMARY KEY,
  message_id TEXT NOT NULL REFERENCES admin_chat_messages(id) ON DELETE CASCADE,
  kind TEXT NOT NULL,
  title TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_folders_project ON folders(project_id);
CREATE INDEX IF NOT EXISTS idx_sync_log_started ON sync_log(started_at);
