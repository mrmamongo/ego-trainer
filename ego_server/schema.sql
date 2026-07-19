-- Ego server schema (SQLite).
-- See docs/adr/0001-platform-architecture.md (D7, D8, D10).
-- Idempotent: all statements use IF NOT EXISTS.

-- Канонический контент задач (meta, контент в git .md)
CREATE TABLE IF NOT EXISTS tasks (
  id           TEXT PRIMARY KEY,           -- 'F1', '1.5', 'A', etc.
  block        TEXT NOT NULL,              -- 'F', '1', 'A', ...
  slug         TEXT NOT NULL,              -- 'block_f_simple'
  task_id      TEXT NOT NULL,              -- 'F1', '1.5'
  title        TEXT NOT NULL,
  level        TEXT NOT NULL,              -- 'easy' | 'medium' | 'hard'
  tags         TEXT NOT NULL DEFAULT '[]', -- JSON array as text
  version      TEXT NOT NULL,              -- SemVer: '1.0.0'
  content_hash TEXT NOT NULL,              -- sha256(statement+stub+solution)
  breaking     INTEGER NOT NULL DEFAULT 0, -- 0/1, последнее изменение breaking?
  md_path      TEXT NOT NULL,              -- относительный путь к .md в git-репо сервера
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

CREATE INDEX IF NOT EXISTS idx_progress_student ON progress(student_id);
CREATE INDEX IF NOT EXISTS idx_progress_task ON progress(task_id);
CREATE INDEX IF NOT EXISTS idx_runs_student ON runs(student_id);
CREATE INDEX IF NOT EXISTS idx_runs_task ON runs(task_id);
CREATE INDEX IF NOT EXISTS idx_tasks_block ON tasks(block);
