-- Accounts default to no access. Money is stored as integer millionths of USD.
CREATE TABLE IF NOT EXISTS ai_settings (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  settings_json TEXT NOT NULL,
  main_key TEXT NOT NULL DEFAULT '',
  guard_key TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS ai_accounts (
  student_id TEXT PRIMARY KEY REFERENCES students(id) ON DELETE CASCADE,
  enabled INTEGER NOT NULL DEFAULT 0,
  defense_required INTEGER NOT NULL DEFAULT 1,
  balance INTEGER NOT NULL DEFAULT 0,
  reserved INTEGER NOT NULL DEFAULT 0 CHECK (reserved >= 0),
  spent INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS ai_credits (
  student_id TEXT NOT NULL REFERENCES students(id) ON DELETE CASCADE,
  request_id TEXT NOT NULL,
  amount INTEGER NOT NULL,
  actor_id TEXT NOT NULL,
  created_at TEXT NOT NULL,
  PRIMARY KEY (student_id, request_id)
);

CREATE TABLE IF NOT EXISTS ai_submissions (
  id TEXT PRIMARY KEY,
  student_id TEXT NOT NULL REFERENCES students(id) ON DELETE CASCADE,
  task_id TEXT NOT NULL,
  version TEXT NOT NULL,
  solution_hash TEXT NOT NULL,
  student_code TEXT NOT NULL,
  statement_md TEXT NOT NULL,
  understanding TEXT NOT NULL DEFAULT 'pending',
  evidence_json TEXT NOT NULL DEFAULT '[]',
  created_at TEXT NOT NULL,
  UNIQUE(student_id, task_id, version, solution_hash)
);

CREATE TABLE IF NOT EXISTS ai_sessions (
  id TEXT PRIMARY KEY,
  student_id TEXT NOT NULL REFERENCES students(id) ON DELETE CASCADE,
  task_id TEXT NOT NULL,
  mode TEXT NOT NULL,
  submission_id TEXT REFERENCES ai_submissions(id) ON DELETE CASCADE,
  context_json TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'active',
  stage INTEGER NOT NULL DEFAULT 0,
  retries INTEGER NOT NULL DEFAULT 0,
  busy INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS ai_defense_per_submission
  ON ai_sessions(submission_id) WHERE mode = 'defend' AND status = 'active';

CREATE TABLE IF NOT EXISTS ai_messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id TEXT NOT NULL REFERENCES ai_sessions(id) ON DELETE CASCADE,
  role TEXT NOT NULL,
  content TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ai_requests (
  student_id TEXT NOT NULL REFERENCES students(id) ON DELETE CASCADE,
  request_id TEXT NOT NULL,
  session_id TEXT NOT NULL REFERENCES ai_sessions(id) ON DELETE CASCADE,
  reserved INTEGER NOT NULL,
  status TEXT NOT NULL DEFAULT 'running',
  response_json TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL,
  PRIMARY KEY(student_id, request_id)
);

CREATE TABLE IF NOT EXISTS ai_usage (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  student_id TEXT NOT NULL REFERENCES students(id) ON DELETE CASCADE,
  request_id TEXT NOT NULL,
  purpose TEXT NOT NULL,
  model TEXT NOT NULL,
  input_tokens INTEGER NOT NULL,
  output_tokens INTEGER NOT NULL,
  estimated INTEGER NOT NULL DEFAULT 0,
  cost INTEGER NOT NULL,
  outcome TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ai_usage_student ON ai_usage(student_id, id);
CREATE INDEX IF NOT EXISTS ai_submissions_student ON ai_submissions(student_id, created_at);
