"""Content-repo sync configuration (ADR-0016 D16.3).

PR 1 (this file): supports ``file://`` URLs only — no git auth, no cron.
PR 2 will extend with ``https://`` URL + auth (token/ssh) + ref + cron
schedule + env overrides (``EGO_TASKS_REPO_URL``, ``EGO_TASKS_REF``, ...).

Config sources (priority: env > content.yaml > defaults):
- ``EGO_TASKS_REPO_URL`` — content-repo URL (``file:///path`` or local path)
- ``EGO_TASKS_LOCAL_PATH`` — where to clone/copy content (defaults to
  ``.ego-server/tasks-repo``)
- ``EGO_TASKS_SYNC_ON_STARTUP`` — ``true``/``false`` (default ``false`` in PR 1)
"""

from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

from pydantic import BaseModel, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class TasksRepoConfig(BaseModel):
    """Content-repo sync settings (PR 1: file:// only).

    Per ADR-0016 D16.3: URL, ref, auth, local_path, sync schedule.
    PR 1 implements only the subset needed for local sync:
    - ``url`` must be ``file://`` or a local filesystem path.
    - ``local_path`` is where content is read from (for file://, this is
      the parsed path itself; for git URLs in PR 2, it's the clone dir).
    - ``on_startup`` controls auto-sync on server start.
    """

    url: str = ""  # 'file:///path/to/ego-tasks' or '/path/to/ego-tasks'
    local_path: Path = Path(".ego-server/tasks-repo")
    on_startup: bool = False
    # PR 2 fields (declared here for forward-compat, ignored in PR 1):
    ref: str = "main"
    auth_type: str = "none"  # none | token | ssh
    sync_schedule: str = ""  # cron expression; '' = manual only

    @field_validator("url")
    @classmethod
    def _validate_url(cls, v: str) -> str:
        if not v:
            return v
        # Accept file:// URLs and bare local paths.
        if v.startswith("file://"):
            return v
        if "://" in v and not v.startswith("file://"):
            # PR 2 will handle https://; PR 1 rejects non-file URLs.
            raise ValueError(
                f"PR 1 supports only file:// or local paths; got: {v!r}. "
                f"git remote sync is implemented in PR 2."
            )
        return v

    @property
    def resolved_local_path(self) -> Path:
        """Resolve the local filesystem path to read content from.

        For ``file://`` URLs, this is the parsed path. For bare local
        paths, it's the path itself. For git URLs (PR 2), this would be
        the clone directory.
        """
        if not self.url:
            return self.local_path
        if self.url.startswith("file://"):
            parsed = urlparse(self.url)
            # file:///C:/path -> /C:/path -> strip leading slash on Windows
            p = Path(parsed.path)
            return p
        # Bare local path.
        return Path(self.url)


class ContentSettings(BaseSettings):
    """Env-driven settings for content-repo sync.

    Env vars (priority over defaults in :class:`TasksRepoConfig`):
    - ``EGO_TASKS_REPO_URL``
    - ``EGO_TASKS_LOCAL_PATH``
    - ``EGO_TASKS_SYNC_ON_STARTUP``
    """

    model_config = SettingsConfigDict(env_prefix="EGO_TASKS_", env_file=".env", extra="ignore")

    repo_url: str = ""
    local_path: Path = Path(".ego-server/tasks-repo")
    on_startup: bool = False

    def to_config(self) -> TasksRepoConfig:
        """Build a :class:`TasksRepoConfig` from env-loaded values."""
        return TasksRepoConfig(
            url=self.repo_url,
            local_path=self.local_path,
            on_startup=self.on_startup,
        )


# Module-level singleton (loaded once; tests may reload).
content_settings = ContentSettings()
