"""Unit tests for deploy/release.py — the production release tool.

Only the pure parts and the lock are exercised here: no docker, no network.
Side effects are injected (Runner for subprocess, fetch for HTTP, getuid), see
``FakeRunner`` / ``FakeFetch`` below; ``dry_run`` and the rollback/registry
ordering are tested against those fakes too.
"""

from __future__ import annotations

import importlib.util
import json
import os
import sqlite3
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "deploy" / "release.py"


def _load():
    # Reuse one loaded copy: pytest may import this module under two names
    # (``tests.test_deploy_release`` and, with --import-mode=prepend, plain).
    if "deploy_release" in sys.modules:
        return sys.modules["deploy_release"]
    spec = importlib.util.spec_from_file_location("deploy_release", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module  # dataclasses look the module up
    spec.loader.exec_module(module)
    return module


release = _load()


# ---------------------------------------------------------------------------
# Asset reference extraction
# ---------------------------------------------------------------------------


def test_extract_assets_from_local_pages():
    html = (
        '<link rel="stylesheet" href="/static/admin/bundle.css">'
        '<link rel="icon" href="/static/branding/favicon-32.png?v=1">'
        '<script src="/static/admin/bundle.js" defer></script>'
        '<script src="/static/student.js?v=3"></script>'
    )
    assert release.extract_asset_refs(html) == [
        "/static/admin/bundle.css",
        "/static/branding/favicon-32.png",
        "/static/admin/bundle.js",
        "/static/student.js",
    ]


def test_extract_assets_ignores_non_assets_and_placeholders():
    html = (
        '<a href="#course">x</a>'
        '<img src="{{BRAND_LOGO_URL}}" alt="">'
        '<a href="/extension/download">vsix</a>'
        '<img src="https://example.invalid/static/x.png">'
        '<img src=/static/branding/cogito-mark.png alt="logo">'
        "<link rel='stylesheet' href='/static/student.css'>"
        '<link rel="alternate" href="//cdn.invalid/static/y.css">'
    )
    assert release.extract_asset_refs(html) == [
        "/static/branding/cogito-mark.png",
        "/static/student.css",
    ]


def test_extract_assets_deduplicates_and_respects_prefix():
    html = (
        '<script src="/static/a.js"></script><script src="/static/a.js?v=1"></script>'
        '<script src="/assets/b.js"></script>'
    )
    assert release.extract_asset_refs(html) == ["/static/a.js"]
    assert release.extract_asset_refs(html, prefix="/assets/") == ["/assets/b.js"]


def test_extract_assets_script_src_without_quotes_and_empty():
    assert release.extract_asset_refs("<script src=/static/x.js></script>") == ["/static/x.js"]
    assert release.extract_asset_refs("") == []
    assert release.extract_asset_refs('<script src="/static/"></script>') == []


def test_extract_assets_from_real_shipped_pages():
    """Every page bundle in the repo references at least one /static asset."""
    for name in ("admin.html", "ide.html", "student.html"):
        html = (REPO_ROOT / "ego_server" / "static" / name).read_text(encoding="utf-8")
        refs = release.extract_asset_refs(html)
        assert refs, name
        assert all(ref.startswith("/static/") for ref in refs)


# ---------------------------------------------------------------------------
# Count comparison
# ---------------------------------------------------------------------------


def _counts(**overrides):
    base = {"students": 10, "progress": 100, "runs": 300, "service_settings": 5}
    base.update(overrides.pop("base", {}))
    data = {
        "base": base,
        "stale": 2,
        "start_tasks": 239,
        "lessons": 71,
    }
    data.update(overrides)
    return data


def test_compare_counts_ok():
    before = _counts()
    after = _counts()
    assert release.compare_counts(after, before, {"start_tasks": 239}) == []


@pytest.mark.parametrize("table", ["students", "progress", "runs", "service_settings"])
def test_compare_counts_detects_changed_base_tables(table):
    after = _counts(base={table: 999})
    problems = release.compare_counts(after, _counts())
    assert any(table in p and "changed" in p for p in problems)


def test_compare_counts_detects_stale_progress():
    after = _counts(stale=200)
    problems = release.compare_counts(after, _counts())
    assert problems == ["check: progress rows with status 'stale' changed 2 -> 200"]


def test_compare_counts_flags_unexpected_catalog_change():
    after = _counts(start_tasks=240)
    problems = release.compare_counts(after, _counts())
    assert problems == ["check: start_tasks changed 239 -> 240"]


def test_compare_counts_mismatched_expectation():
    problems = release.compare_counts(_counts(), _counts(), {"start_tasks": 240}, "live")
    assert problems == ["live: expected start_tasks=240, got 239"]


def test_compare_counts_new_counter_requires_expect():
    after = _counts(new_project_tasks=3)
    problems = release.compare_counts(after, _counts())
    assert problems == ["check: counter new_project_tasks appeared (3) without --expect"]
    assert release.compare_counts(after, _counts(), {"new_project_tasks": 3}) == []


def test_compare_counts_expect_names_existing_counter():
    before = _counts()
    after = _counts(start_tasks=240)
    assert release.compare_counts(after, before, {"start_tasks": 240}) == []


def test_compare_counts_base_alias():
    problems = release.compare_counts(
        _counts(base={"students": 11}), _counts(), {"base.students": 10}
    )
    assert any("students rows changed" in p for p in problems)
    assert any("expected base.students=10, got 11" in p for p in problems)


def test_compare_counts_missing_counter_is_reported():
    before = _counts()
    after = {k: v for k, v in before.items() if k != "lessons"}
    # A counter that vanished (table dropped by a bad release) must be caught.
    assert release.compare_counts(after, before) == [
        "check: counter lessons disappeared (was 71)"
    ]
    # ... also when it was pinned with --expect.
    assert release.compare_counts(after, before, {"lessons": 71}) == [
        "check: expected lessons=71, got None"
    ]


def test_read_counts_and_check_sql(tmp_path):
    db = tmp_path / "ego.db"
    with sqlite3.connect(db) as conn:
        for table in release.BASE_TABLES:
            conn.execute(f"CREATE TABLE {table} (id INTEGER PRIMARY KEY, status TEXT)")
        conn.execute("CREATE TABLE tasks (project_id TEXT, folder_id TEXT, version TEXT)")
        conn.execute("CREATE TABLE lessons (id INTEGER PRIMARY KEY)")
        conn.executemany(
            "INSERT INTO tasks VALUES (?, ?, ?)",
            [("python-start", "f1", "1.0"), ("python-start", "f2", "1.0"), ("xl-a", "xl_a", "1.1.0")],
        )
        conn.execute("INSERT INTO progress (status) VALUES ('stale')")
        conn.execute("INSERT INTO lessons DEFAULT VALUES")
    counts = release.read_counts(db, {"python-start_folders": 2, "my_proj_tasks": 0})
    assert counts["base"]["progress"] == 1
    assert counts["stale"] == 1
    assert counts["start_tasks"] == 2
    assert counts["start_folders"] == 2
    assert counts["xla_tasks"] == 1
    assert counts["lessons"] == 1
    assert counts["python-start_folders"] == 2
    assert counts["my_proj_tasks"] == 0


def test_check_sql_rejects_unknown_counter():
    with pytest.raises(release.ConfigError):
        release.check_sql({"start_task": 239})  # typo of start_tasks
    with pytest.raises(release.ConfigError):
        release.check_sql({"start_tasks": -1})


def test_check_sql_quotes_project_names():
    sql = release.check_sql({"we'ird_tasks": 1})["we'ird_tasks"]
    assert "we''ird" in sql


# ---------------------------------------------------------------------------
# .env image replacement
# ---------------------------------------------------------------------------


def test_replace_env_image_preserves_the_rest():
    env = "EGO_JWT_SECRET=abc\nCOGITO_IMAGE=ego-trainer:old\nEGO_X=1\n"
    new = release.replace_env_image(env, "git.born-in-july.ru/mrmamongo/cogito:v2026.10.24")
    assert new == (
        "EGO_JWT_SECRET=abc\n"
        "COGITO_IMAGE=git.born-in-july.ru/mrmamongo/cogito:v2026.10.24\n"
        "EGO_X=1\n"
    )
    assert release.env_image(new) == "git.born-in-july.ru/mrmamongo/cogito:v2026.10.24"


def test_replace_env_image_is_literal():
    env = "COGITO_IMAGE=a\\1\\g<0>$$x\nOTHER=\\1\n"
    new = release.replace_env_image(env, "ego-trainer:\\1")
    assert new == "COGITO_IMAGE=ego-trainer:\\1\nOTHER=\\1\n"


@pytest.mark.parametrize(
    "env",
    ["EGO_X=1\n", "COGITO_IMAGE=a\nCOGITO_IMAGE=b\n"],
)
def test_replace_env_image_requires_exactly_one_line(env):
    with pytest.raises(release.ConfigError):
        release.replace_env_image(env, "ego-trainer:new")


@pytest.mark.parametrize("image", ["", " leading", "a\nb", "a\rb"])
def test_replace_env_image_rejects_bad_refs(image):
    with pytest.raises(release.ConfigError):
        release.replace_env_image("COGITO_IMAGE=old\n", image)


def test_env_image_absent():
    assert release.env_image("EGO_X=1\n") is None


# ---------------------------------------------------------------------------
# Config parsing
# ---------------------------------------------------------------------------


def test_parse_expect():
    assert release.parse_expect(["start_tasks=239", "lessons = 71"]) == {
        "start_tasks": 239,
        "lessons": 71,
    }
    assert release.parse_expect([]) == {}
    assert release.parse_expect(None) == {}


@pytest.mark.parametrize("item", ["start_tasks", "start_tasks=x", "=5", "a=-1", "a=1.5"])
def test_parse_expect_rejects_garbage(item):
    with pytest.raises(release.ConfigError):
        release.parse_expect([item])


def test_parse_expect_rejects_conflict():
    with pytest.raises(release.ConfigError):
        release.parse_expect(["lessons=1", "lessons=2"])


def test_load_config_from_json(tmp_path):
    content = tmp_path / "python-start"
    content.mkdir()
    vsix = tmp_path / "cogito-0.2.0.vsix"
    vsix.write_bytes(b"PK")
    cfg_file = tmp_path / "release.json"
    cfg_file.write_text(
        json.dumps(
            {
                "name": "release-abc1234",
                "image": "ego-trainer:release-abc1234",
                "content": {"python-start": str(content)},
                "expect_current": "ego-trainer:release-61f3a2b",
                "expect": {"start_tasks": 239, "lessons": 71},
                "publish_vsix": str(vsix),
                "notes": "tuples and sets",
            }
        ),
        encoding="utf-8",
    )
    cfg = release.load_config(config_path=cfg_file, root=tmp_path)
    assert cfg.name == "release-abc1234"
    assert cfg.image == "ego-trainer:release-abc1234"
    assert cfg.expect_current == "ego-trainer:release-61f3a2b"
    assert cfg.content == {"python-start": content}
    assert cfg.expect == {"start_tasks": 239, "lessons": 71}
    assert cfg.publish_vsix == vsix
    assert cfg.notes == "tuples and sets"
    assert cfg.root == tmp_path
    assert cfg.release_dir == tmp_path / "releases" / "release-abc1234"
    assert cfg.backup_dir == cfg.release_dir / "backup"
    assert cfg.lock_path == tmp_path / "releases" / ".lock"
    assert cfg.new_image == "ego-trainer:release-abc1234"
    assert cfg.registry_image() == "git.born-in-july.ru/mrmamongo/cogito:release-abc1234"
    assert cfg.registry_image("v" + cfg.name).endswith(":vrelease-abc1234")


def test_load_config_cli_overrides_json(tmp_path):
    content = tmp_path / "python-start"
    content.mkdir()
    other = tmp_path / "xl-a"
    other.mkdir()
    cfg_file = tmp_path / "release.json"
    cfg_file.write_text(
        json.dumps(
            {
                "name": "content-old",
                "content": {"python-start": str(content)},
                "expect_current": "ego-trainer:a",
                "expect": {"start_tasks": 1},
            }
        ),
        encoding="utf-8",
    )
    cfg = release.load_config(
        config_path=cfg_file,
        name="content-new",
        content=[f"xl-a={other}"],
        expect=["lessons=71"],
        root=tmp_path,
    )
    assert cfg.name == "content-new"
    assert cfg.content == {"python-start": content, "xl-a": other}
    assert cfg.expect == {"start_tasks": 1, "lessons": 71}
    assert cfg.image is None
    assert cfg.new_image == "ego-trainer:a"  # content-only: image stays


def test_load_config_rejects_missing_name_and_current(tmp_path):
    content = tmp_path / "c"
    content.mkdir()
    with pytest.raises(release.ConfigError):
        release.load_config(expect_current="ego-trainer:a", content=[f"c={content}"])
    with pytest.raises(release.ConfigError):
        release.load_config(name="r1", content=[f"c={content}"])
    with pytest.raises(release.ConfigError):
        release.load_config(name="r1", expect_current="ego-trainer:a")


def test_load_config_rejects_nothing_to_release(tmp_path):
    with pytest.raises(release.ConfigError, match="nothing to release"):
        release.load_config(name="r1", expect_current="ego-trainer:a")


@pytest.mark.parametrize(
    "kwargs",
    [
        {"name": "../evil"},
        {"name": "r1", "image": "bad image"},
        {"content": ["no-equals-sign"]},
        {"content": ["../x={dir}"]},
        {"expect": ["start_tasks=abc"]},
        {"expect": ["start_task=1"]},
    ],
)
def test_load_config_rejects_bad_values(tmp_path, kwargs):
    content = tmp_path / "c"
    content.mkdir()
    args = {"name": "r1", "expect_current": "ego-trainer:a", "content": [f"c={content}"]}
    args.update(kwargs)
    if isinstance(args.get("content"), list):
        args["content"] = [item.replace("{dir}", str(content)) for item in args["content"]]
    if "name" not in kwargs:
        args["name"] = "r1"
    with pytest.raises(release.ConfigError):
        release.load_config(**args)


def test_load_config_rejects_bad_json(tmp_path):
    path = tmp_path / "r.json"
    path.write_text("{not json", encoding="utf-8")
    with pytest.raises(release.ConfigError, match="not valid JSON"):
        release.load_config(config_path=path)
    path.write_text(json.dumps({"name": "r1", "surprise": 1}), encoding="utf-8")
    with pytest.raises(release.ConfigError, match="unknown keys"):
        release.load_config(config_path=path)
    path.write_text(json.dumps([1, 2]), encoding="utf-8")
    with pytest.raises(release.ConfigError, match="JSON object"):
        release.load_config(config_path=path)
    with pytest.raises(release.ConfigError, match="not found"):
        release.load_config(config_path=tmp_path / "missing.json")


def test_load_config_rejects_missing_dirs_and_vsix(tmp_path):
    with pytest.raises(release.ConfigError, match="does not exist"):
        release.load_config(
            name="r1", expect_current="ego-trainer:a", content=[f"c={tmp_path / 'nope'}"]
        )
    with pytest.raises(release.ConfigError, match="vsix file not found"):
        release.load_config(
            name="r1", expect_current="ego-trainer:a", publish_vsix=str(tmp_path / "x.vsix")
        )


def test_load_config_rejects_bad_expect_types_in_json(tmp_path):
    path = tmp_path / "r.json"
    path.write_text(
        json.dumps({"name": "r1", "expect_current": "ego-trainer:a", "expect": {"lessons": "71"}}),
        encoding="utf-8",
    )
    with pytest.raises(release.ConfigError):
        release.load_config(config_path=path)


# ---------------------------------------------------------------------------
# Lock
# ---------------------------------------------------------------------------


def test_lock_is_exclusive_and_released(tmp_path):
    lock = tmp_path / "releases" / ".lock"
    fd = release.acquire_lock(lock)
    try:
        assert lock.exists()
        assert f"pid={os.getpid()}" in lock.read_text()
        with pytest.raises(release.LockBusy, match="another release is running"):
            release.acquire_lock(lock)
    finally:
        release.release_lock(lock, fd)
    assert not lock.exists()
    # Released: a second release can acquire it again.
    fd2 = release.acquire_lock(lock)
    release.release_lock(lock, fd2)
    assert not lock.exists()


def test_lock_release_is_idempotent(tmp_path):
    lock = tmp_path / ".lock"
    fd = release.acquire_lock(lock)
    release.release_lock(lock, fd)
    release.release_lock(lock, fd)  # second call must not raise
    release.release_lock(lock, None)
    assert not lock.exists()


def test_lock_removed_after_failed_release(tmp_path, capsys):
    """run_release releases the lock in finally even when a step aborts."""
    cfg = release.Config(name="r1", expect_current="ego-trainer:a", root=tmp_path)
    code = release.run_release(cfg, run=as_runner(FakeRunner()))  # missing .env
    assert code == release.EXIT_ABORT
    assert "missing" in capsys.readouterr().err
    assert not cfg.lock_path.exists()


def test_lock_busy_exit_code(tmp_path, capsys):
    cfg = release.Config(name="r1", expect_current="ego-trainer:a", root=tmp_path)
    cfg.release_dir.mkdir(parents=True)
    fd = release.acquire_lock(cfg.lock_path)
    try:
        assert release.run_release(cfg, run=as_runner(FakeRunner())) == release.EXIT_LOCKED
    finally:
        release.release_lock(cfg.lock_path, fd)
    assert "another release is running" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# Cleanup plan / disk formatting
# ---------------------------------------------------------------------------


def test_cleanup_targets_keeps_only_running():
    images = [
        "git.born-in-july.ru/mrmamongo/cogito:release-old",
        "ego-trainer:release-new",
        "ego-trainer:release-old",
        "postgres:16",
        "git.born-in-july.ru/mrmamongo/cogito:<none>:<none>",
        "ego-trainer:release-new",
    ]
    assert release.cleanup_targets(images, "ego-trainer:release-new") == [
        "ego-trainer:release-old",
        "git.born-in-july.ru/mrmamongo/cogito:release-old",
    ]


def test_cleanup_targets_empty():
    assert release.cleanup_targets([], "ego-trainer:x") == []


def test_format_disk():
    df = (
        "Filesystem      Size  Used Avail Use% Mounted on\n"
        "/dev/sda1        40G   12G   27G  31% /\n"
    )
    assert release.format_disk(df) == "/dev/sda1        40G   12G   27G  31% /"
    assert release.format_disk([]) == "unknown"
    assert release.format_disk("") == "unknown"


# ---------------------------------------------------------------------------
# Dry run and orchestration order (with injected side effects)
# ---------------------------------------------------------------------------


class FakeRunner:
    """Records argv; returns canned output per command family."""

    def __init__(self, outputs=None, failing=()):
        self.calls: list[list[str]] = []
        self.outputs = outputs or {}
        self.failures = tuple(failing)

    def __call__(self, argv, check=True, read_empty=""):
        self.calls.append(list(argv))
        joined = " ".join(argv)
        out = self.outputs.get(argv[0], "")
        if callable(out):
            out = out(argv)  # may raise CommandFailed (e.g. a missing image)
        if check and tuple(argv) in self.failures:
            raise release.CommandFailed(f"command failed: {joined}")
        return out


def as_runner(fake: FakeRunner, dry_run: bool = False) -> release.Runner:
    """Wrap a FakeRunner (returns stdout) into the ``(code, stdout, stderr)`` Runner.

    Read-only commands (``mutating=False``) reach ``fake`` even in dry-run
    mode, exactly like the real Runner; mutating ones are only printed.
    """
    return release.Runner(lambda argv: (0, fake(argv), ""), dry_run=dry_run)


class FakeFetch:
    """Serves every path with 200; records (port, path)."""

    def __init__(self, fail_paths=()):
        self.calls: list[tuple[int, str]] = []
        self.fail_paths = set(fail_paths)

    @property
    def paths(self):
        return [path for _port, path in self.calls]

    def __call__(self, port, path, tries=1):
        self.calls.append((port, path))
        if path in self.fail_paths:
            return 404, b""
        if path == "/static/student.css":
            return 200, b'body{} [data-theme="dark"] {}'
        if path == "/extension/latest":
            return 200, b'{"version": "0.2.0"}'
        return 200, b'<script src="/static/a.js"></script>'


def _make_prod(root: Path, image="ego-trainer:cur"):
    (root / "data" / "extension").mkdir(parents=True)
    (root / "content" / "projects" / "python-start").mkdir(parents=True)
    (root / "content" / "catalog.yaml").write_text("x")
    (root / "data" / "ego.db").parent.mkdir(parents=True, exist_ok=True)
    (root / ".env").write_text(f"EGO_X=1\nCOGITO_IMAGE={image}\n")
    (root / "compose.yaml").write_text("name: cogito\n")
    with sqlite3.connect(root / "data" / "ego.db") as conn:
        for table in release.BASE_TABLES:
            conn.execute(f"CREATE TABLE {table} (id INTEGER PRIMARY KEY, status TEXT)")
        conn.execute("CREATE TABLE tasks (project_id TEXT, folder_id TEXT, version TEXT)")
        conn.execute("CREATE TABLE lessons (id INTEGER PRIMARY KEY)")
    return root


def _docker_outputs(
    current: str = "ego-trainer:cur",
    images: str = "ego-trainer:cur\n",
    image_ids: dict[str, str] | None = None,
):
    """Canned ``docker`` CLI answers for the read-only commands.

    ``docker inspect cogito-cogito-server-1`` → JSON with ``Config.Image`` =
    ``current`` (as Docker prints it); ``docker image inspect <ref> --format
    {{.Id}}`` → the id of ``<ref>`` (a ref missing from ``ids`` simulates an
    absent image: CommandFailed). ``docker images`` lists ``images``;
    mutating commands return "".
    """
    # ego-trainer:cur is what runs now; ego-trainer:new is the rebuilt image
    # (locally present, different id); anything else is absent unless passed.
    ids = {"ego-trainer:cur": "id-running", "ego-trainer:new": "id-new"}
    ids.update(image_ids or {})

    def docker(argv):
        # Ignore "--format ..." options so dispatch is by subject only.
        words = [arg for arg in argv if arg != "--format" and not arg.startswith("{{")]
        if words[:3] == ["docker", "image", "inspect"]:
            if words[3] not in ids:
                raise release.CommandFailed(f"no such image: {words[3]}")
            return ids[words[3]]
        if words[:3] == ["docker", "inspect", release.LIVE_CONTAINER]:
            return json.dumps([{"Config": {"Image": current}}])
        if words[:2] == ["docker", "images"]:
            return images
        return ""

    return {
        "docker": docker,
        "df": "Filesystem Size Used Avail Use% Mounted on\n/dev/sda1 40G 1G 39G 3% /\n",
    }


def _new_image_release(root: Path, **kwargs):
    """A release that rebuilds the same app: running image == new image id."""
    kwargs.setdefault("name", "r1")
    return release.Config(name=kwargs.pop("name"), expect_current="ego-trainer:cur",
                          image="ego-trainer:new", root=root, **kwargs)


def test_dry_run_prints_plan_without_side_effects(tmp_path, capsys):
    root = _make_prod(tmp_path)
    content = tmp_path / "incoming" / "new-python-start"
    content.mkdir(parents=True)
    (content / "project.yaml").write_text("x")
    cfg = _new_image_release(root, content={"python-start": content},
                             expect={"start_tasks": 239})
    fake = FakeRunner()
    fetch = FakeFetch()
    code = release.run_release(
        cfg, run=as_runner(fake, dry_run=True), fetch=FakeFetch(), dry_run=True
    )
    assert code == release.EXIT_OK
    out = capsys.readouterr().out
    assert "DRY RUN" in out and "DRY RUN OK" in out
    assert "running image must : ego-trainer:cur" in out
    assert "new image          : ego-trainer:new" in out
    assert "[dry-run] docker run -d --name rel-candidate" in out
    assert "[dry-run] docker exec rel-candidate ego-server admin sync-tasks" in out
    assert "[dry-run] docker compose --project-directory" in out
    assert "COGITO_IMAGE=ego-trainer:new" in out
    assert "[dry-run] docker push -q " in out
    assert "DEPLOY OK" not in out  # only the real run prints DEPLOY OK
    # Only read-only docker commands ran (the plan is built from live state);
    # nothing mutating, no HTTP, no files written.
    assert all(argv[:2] in (["docker", "inspect"], ["docker", "images"])
               for argv in fake.calls), fake.calls
    assert fetch.calls == []
    assert not cfg.release_dir.exists()
    assert not cfg.lock_path.exists()
    assert (root / ".env").read_text() == "EGO_X=1\nCOGITO_IMAGE=ego-trainer:cur\n"
    assert sorted(p.name for p in (root / "content" / "projects").iterdir()) == ["python-start"]


def test_dry_run_content_only(tmp_path, capsys):
    root = _make_prod(tmp_path)
    content = tmp_path / "new"
    content.mkdir()
    cfg = release.Config(
        name="content-f610d0b",
        expect_current="ego-trainer:cur",
        content={"xl-a": content},
        root=root,
    )
    fake = FakeRunner(_docker_outputs())
    assert release.run_release(
        cfg, run=as_runner(fake, dry_run=True), fetch=FakeFetch(), dry_run=True
    ) == release.EXIT_OK
    out = capsys.readouterr().out
    assert "new image          : (none — content/extension only)" in out
    assert "switch image" not in out
    assert "image unchanged: ego-trainer:cur" in out
    assert "[dry-run] docker push -q git.born-in-july.ru/mrmamongo/cogito:content-f610d0b" in out
    assert all(argv[:2] in (["docker", "inspect"], ["docker", "images"])
               for argv in fake.calls), fake.calls
    assert not cfg.release_dir.exists()


def test_expect_current_mismatch_aborts_before_any_change(tmp_path, capsys):
    root = _make_prod(tmp_path)
    cfg = release.Config(
        name="r1", expect_current="ego-trainer:other", image="ego-trainer:new", root=root
    )
    fake = FakeRunner(_docker_outputs())
    assert release.run_release(cfg, run=as_runner(fake), fetch=FakeFetch()) == (
        release.EXIT_ABORT
    )
    err = capsys.readouterr().err
    assert "running image is 'ego-trainer:cur', expected 'ego-trainer:other'" in err
    assert not any(argv[:2] == ["docker", "run"] for argv in fake.calls)
    assert (root / ".env").read_text().endswith("COGITO_IMAGE=ego-trainer:cur\n")
    assert not cfg.lock_path.exists()


def test_missing_local_image_aborts(tmp_path, capsys):
    root = _make_prod(tmp_path)
    cfg = release.Config(
        name="r1", expect_current="ego-trainer:cur", image="ego-trainer:nowhere", root=root
    )
    fake = FakeRunner(_docker_outputs())  # ego-trainer:new is unknown
    assert release.run_release(cfg, run=as_runner(fake), fetch=FakeFetch()) == (
        release.EXIT_ABORT
    )
    assert "is not present locally" in capsys.readouterr().err
    assert not any(argv[:2] == ["docker", "run"] for argv in fake.calls)


def test_container_image_reads_config_image():
    """The guard compares Config.Image of the running container (not its id)."""
    cfg = release.Config(name="r1", expect_current="ego-trainer:cur")

    def func(argv):  # only the plain `docker inspect <container>` form
        assert argv == ["docker", "inspect", release.LIVE_CONTAINER], argv
        return 0, json.dumps([{"Id": "container-id",
                               "Config": {"Image": "ego-trainer:61f3a2b"}}]), ""

    rel = release.Release(cfg, run=release.Runner(func))
    assert rel.running_image() == "ego-trainer:61f3a2b"


def test_container_image_missing():
    cfg = release.Config(name="r1", expect_current="ego-trainer:cur")
    rel = release.Release(cfg, run=release.Runner(lambda argv: (1, "", "no such object")))
    with pytest.raises(release.CommandFailed, match="no such object"):
        rel.running_image()


def test_image_ref_absent_is_none():
    cfg = release.Config(name="r1", expect_current="ego-trainer:cur")
    rel = release.Release(
        cfg, run=release.Runner(lambda argv: (1, "", "Error: No such image: ego-trainer:x"))
    )
    assert rel.image_ref("ego-trainer:x") is None


def test_failed_live_check_rolls_back_env_and_content(tmp_path, capsys):
    root = _make_prod(tmp_path)
    live_dir = root / "content" / "projects" / "python-start"
    (live_dir / "project.yaml").write_text("old")
    (live_dir / "keep.md").write_text("kept")
    content = tmp_path / "new"
    content.mkdir()
    (content / "project.yaml").write_text("new")  # replaces the dir content
    cfg = _new_image_release(root, content={"python-start": content})

    class LivePanelBroken(FakeFetch):
        """The candidate port is fine, the live port 404s on /panel."""

        def __call__(self, port, path, tries=1):
            if port == release.LIVE_PORT and path == "/panel":
                self.calls.append((port, path))
                return 404, b""
            return super().__call__(port, path, tries)

    fake = FakeRunner(_docker_outputs())
    code = release.run_release(
        cfg, run=as_runner(fake), fetch=LivePanelBroken(), getuid=lambda: 1000
    )
    captured = capsys.readouterr()
    assert code == release.EXIT_ABORT
    assert "ROLLED BACK" in captured.err
    assert "live: GET /panel -> 404" in captured.err
    # .env restored, old content restored, compose up ran twice (switch + rollback).
    assert (root / ".env").read_text() == "EGO_X=1\nCOGITO_IMAGE=ego-trainer:cur\n"
    assert (live_dir / "project.yaml").read_text() == "old"
    assert (live_dir / "keep.md").read_text() == "kept"
    assert (cfg.backup_dir / "content" / "python-start" / "project.yaml").read_text() == "old"
    assert (cfg.backup_dir / "ego-pre-release.db").exists()
    ups = [argv for argv in fake.calls if "up" in argv]
    assert len(ups) == 2
    # No registry push after a failed release.
    assert not any(argv[:2] == ["docker", "push"] for argv in fake.calls)
    assert not cfg.lock_path.exists()


def test_failed_rollback_is_reported(tmp_path, capsys):
    root = _make_prod(tmp_path)
    cfg = release.Config(name="r1", expect_current="ego-trainer:cur", root=root)

    class AlwaysBad(FakeFetch):
        def __call__(self, port, path, tries=1):
            return 500, b""

    fake = FakeRunner(_docker_outputs())
    assert release.run_release(cfg, run=as_runner(fake), fetch=AlwaysBad()) == (
        release.EXIT_ABORT
    )
    assert "ROLLBACK INCOMPLETE" in capsys.readouterr().err


def test_registry_push_and_cleanup_after_success(tmp_path, capsys):
    root = _make_prod(tmp_path)
    cfg = _new_image_release(root)
    images = (
        "git.born-in-july.ru/mrmamongo/cogito:r0\n"
        "ego-trainer:new\n"
        "ego-trainer:cur\n"
        "postgres:16\n"
    )
    fake = FakeRunner(_docker_outputs(images=images))
    assert release.run_release(
        cfg, run=as_runner(fake), fetch=FakeFetch(), getuid=lambda: 1000
    ) == release.EXIT_OK
    out = capsys.readouterr().out
    assert out.rstrip().endswith("DEPLOY OK")
    # The new image is tagged (not re-tagged wrongly) and pushed twice.
    tags = [argv for argv in fake.calls if argv[:2] == ["docker", "tag"]]
    assert tags == [
        ["docker", "tag", "ego-trainer:new", "git.born-in-july.ru/mrmamongo/cogito:r1"],
        ["docker", "tag", "ego-trainer:new", "git.born-in-july.ru/mrmamongo/cogito:vr1"],
    ]
    assert [argv[-1] for argv in fake.calls if argv[:2] == ["docker", "push"]] == [
        "git.born-in-july.ru/mrmamongo/cogito:r1",
        "git.born-in-july.ru/mrmamongo/cogito:vr1",
    ]
    assert [argv[-1] for argv in fake.calls if argv[:2] == ["docker", "rmi"]] == [
        "ego-trainer:cur",
        "git.born-in-july.ru/mrmamongo/cogito:r0",
    ]
    assert ["docker", "image", "prune", "-f"] in fake.calls
    assert ["docker", "builder", "prune", "-f"] in fake.calls
    assert "disk: /dev/sda1" in out
    assert (root / ".env").read_text().endswith("COGITO_IMAGE=ego-trainer:new\n")
    assert not cfg.lock_path.exists()
    # The throwaway candidate dir is removed; only backup/ and the lock parent remain.
    assert sorted(p.name for p in cfg.release_dir.iterdir()) == ["backup"]


def test_content_only_tags_running_image(tmp_path, capsys):
    root = _make_prod(tmp_path)
    content = tmp_path / "new"
    content.mkdir()
    cfg = release.Config(
        name="content-f610d0b", expect_current="ego-trainer:cur", content={"xl-a": content},
        root=root,
    )
    fake = FakeRunner(_docker_outputs())
    assert release.run_release(
        cfg, run=as_runner(fake), fetch=FakeFetch(), getuid=lambda: 1000
    ) == release.EXIT_OK
    assert any(
        argv == ["docker", "tag", "ego-trainer:cur",
                 "git.born-in-july.ru/mrmamongo/cogito:content-f610d0b"]
        for argv in fake.calls
    )
    assert not any(argv[:2] == ["docker", "push"] and argv[-1].endswith(":ego-trainer:cur")
                   for argv in fake.calls)
    assert (root / ".env").read_text() == "EGO_X=1\nCOGITO_IMAGE=ego-trainer:cur\n"


def test_live_counter_change_rolls_back(tmp_path, capsys, monkeypatch):
    """A live sync that flips progress rows to 'stale' aborts the release."""
    root = _make_prod(tmp_path)
    with sqlite3.connect(root / "data" / "ego.db") as conn:
        conn.execute("INSERT INTO progress (status) VALUES ('done')")
    content = tmp_path / "new"
    content.mkdir()
    (content / "project.yaml").write_text("new")
    cfg = release.Config(
        name="r1", expect_current="ego-trainer:cur", content={"python-list": content},
        root=root,
    )
    fake = FakeRunner(_docker_outputs())
    real_sync = release.Release.sync_tasks

    def sync_tasks(self, container):
        if container == release.LIVE_CONTAINER:  # candidate sync leaves DB intact
            with sqlite3.connect(self.cfg.live_db) as conn:
                conn.execute("INSERT INTO progress (status) VALUES ('stale')")

    monkeypatch.setattr(release.Release, "sync_tasks", sync_tasks)
    try:
        code = release.run_release(cfg, run=as_runner(fake), fetch=FakeFetch())
    finally:
        monkeypatch.setattr(release.Release, "sync_tasks", real_sync)
    assert code == release.EXIT_ABORT
    assert "progress rows with status 'stale' changed 0 -> 1" in capsys.readouterr().err
    assert not any(argv[:2] == ["docker", "push"] for argv in fake.calls)
    # The new project dir was rolled back away (it did not exist before).
    assert not (root / "content" / "projects" / "python-list").exists()


def test_dry_run_vsix_does_not_publish_or_check_unpublished_metadata(tmp_path, capsys):
    root = _make_prod(tmp_path)
    vsix = tmp_path / "cogito-0.2.3.vsix"
    vsix.write_bytes(b"PK")
    cfg = release.Config(
        name="extension-0.2.3", expect_current="ego-trainer:cur",
        publish_vsix=vsix, root=root,
    )
    fake = FakeRunner(_docker_outputs())
    fetch = FakeFetch()
    code = release.run_release(
        cfg, run=as_runner(fake, dry_run=True), fetch=fetch, dry_run=True
    )
    assert code == release.EXIT_OK
    assert "DRY RUN OK" in capsys.readouterr().out
    assert fetch.calls == []
    assert not cfg.incoming_vsix().exists()
    assert not cfg.release_dir.exists()
    assert not cfg.lock_path.exists()
    assert not any("publish-extension" in argv for argv in fake.calls)


def test_publish_vsix_checks_extension_latest(tmp_path, capsys):
    root = _make_prod(tmp_path)
    vsix = tmp_path / "cogito-0.2.0.vsix"
    vsix.write_bytes(b"PK")
    cfg = release.Config(
        name="r1", expect_current="ego-trainer:cur", publish_vsix=vsix, root=root
    )
    fake = FakeRunner(_docker_outputs())
    fetch = FakeFetch()
    assert release.run_release(
        cfg, run=as_runner(fake), fetch=fetch, getuid=lambda: 1000
    ) == release.EXIT_OK
    exec_calls = [argv for argv in fake.calls if argv[:2] == ["docker", "exec"]]
    assert any("publish-extension" in argv for argv in exec_calls)
    assert "/extension/latest" in fetch.paths
    assert (root / "incoming" / "r1" / "cogito.vsix").read_bytes() == b"PK"
    assert (cfg.backup_dir / "extension").is_dir()


def test_publish_vsix_already_in_incoming(tmp_path):
    root = _make_prod(tmp_path)
    vsix = root / "incoming" / "r1" / "cogito.vsix"
    vsix.parent.mkdir(parents=True)
    vsix.write_bytes(b"PK")
    cfg = release.Config(
        name="r1", expect_current="ego-trainer:cur", publish_vsix=vsix, root=root
    )
    assert release.run_release(
        cfg, run=as_runner(FakeRunner(_docker_outputs())), fetch=FakeFetch(),
        getuid=lambda: 1000,
    ) == release.EXIT_OK
    assert vsix.read_bytes() == b"PK"


def test_dry_run_publish_vsix_writes_nothing(tmp_path, capsys):
    root = _make_prod(tmp_path)
    vsix = tmp_path / "cogito-0.2.0.vsix"
    vsix.write_bytes(b"PK")
    cfg = release.Config(
        name="r1", expect_current="ego-trainer:cur", publish_vsix=vsix, root=root
    )
    fake = FakeRunner(_docker_outputs())
    code = release.run_release(
        cfg, run=as_runner(fake, dry_run=True), fetch=FakeFetch(), dry_run=True
    )
    assert code == release.EXIT_OK
    assert "would check /extension/latest" in capsys.readouterr().out
    assert not (root / "incoming" / "r1").exists()


def test_main_help():
    with pytest.raises(SystemExit) as excinfo:
        release.main(["--help"])
    assert excinfo.value.code == 0


def test_main_usage_errors(capsys):
    with pytest.raises(SystemExit) as excinfo:
        release.main([])  # missing --name / --expect-current
    assert excinfo.value.code == release.EXIT_USAGE
    assert "--expect-current" in capsys.readouterr().err


def test_main_dry_run_off_the_server(tmp_path, monkeypatch, capsys):
    """Off the server (no /opt/cogito) the dry run aborts cleanly, no traceback."""
    monkeypatch.setattr(release, "ROOT", tmp_path / "no-such-prod-root")
    content = tmp_path / "c"
    content.mkdir()
    code = release.main(
        [
            "--name", "r1",
            "--expect-current", "ego-trainer:cur",
            "--content", f"python-start={content}",
            "--expect", "start_tasks=0",
            "--dry-run",
        ],
        run=release.Runner(lambda argv: (0, "", "")),
        fetch=FakeFetch(),
        getuid=lambda: 1000,
    )
    assert code == release.EXIT_ABORT
    assert "run this tool on the prod server" in capsys.readouterr().err


def test_build_parser_defaults():
    parser = release.build_parser()
    args = parser.parse_args(
        ["--name", "r", "--image", "x", "--content", "a=/b", "--content", "c=/d",
         "--expect", "k=1"]
    )
    assert args.content == ["a=/b", "c=/d"]
    assert args.expect == ["k=1"]
    assert args.dry_run is False
    assert args.no_dark_theme_check is False
