"""Runner — executes Python code in a subprocess sandbox.

Используется ego.checker для запуска решения студента и эталона
в одинаковых условиях (timeout, no network, temp dir, blocked imports).

Формы запуска:

- :func:`run_code` — произвольный код в пустой временной папке;
- :func:`run_function` — одна функция (``task_*``), аргументы передаются
  как литералы, сравнивается ``repr`` результата;
- :func:`run_project` — проект из нескольких файлов (ADR-0018 D18.4):
  импорт функции модуля (``target="module.func"``) или запуск точки
  входа (``entry="main.py"``) с вводом.

See ADR-0001 D12 (sandbox для ego check), D9 (сервер не выполняет
студенческий код — check всегда локален).
"""

from __future__ import annotations

import fnmatch
import inspect
import json
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any

from ego.errors import SandboxError
from ego.exec_helpers import (
    _ego_import_function,
    _ego_mutable_ids,
    _ego_normalize,
    _ego_program_failure,
    _ego_same_file,
    _ego_same_value,
    _ego_watch_imports,
)


# Зависимости, которые студенту запрещено использовать
# (защита от exfil, file system access).
BLOCKED_IMPORTS: set[str] = {
    "os", "subprocess", "socket", "urllib", "http", "ctypes",
    "multiprocessing", "threading", "signal", "asyncio",
    "shutil", "pathlib", "pickle", "marshal",
}

#: Defaults of ``Folder.workspace`` (ADR-0018 D18.1).
DEFAULT_ENTRY = "main.py"
DEFAULT_INCLUDE = ("*.py",)
DEFAULT_MAX_FILES = 20
DEFAULT_MAX_BYTES = 200_000

#: Directories a student's project never writes (ADR-0018 D18.4).
_RESERVED_DIRS = (".cogito", "__pycache__", ".venv")

#: stdout size cap of a program run: a runaway ``print()`` is not a result.
MAX_PROGRAM_OUTPUT = 200_000

#: Modules the project wrapper loads on its own in import mode: ``importlib``
#: (the wrapper imports it after the pre-existing snapshot) and ``os`` /
#: ``traceback`` (importing a student module goes through them). A warning for
#: them is not the student's import and would make every run look broken, so
#: it is dropped; a module the student really imported (``asyncio``,
#: ``threading``, ``subprocess``, …) is still reported.
_WRAPPER_IMPORTS = frozenset({"importlib", "traceback", "os"})


@dataclass
class RunResult:
    """Результат выполнения кода в sandbox."""

    stdout: str
    stderr: str
    returncode: int
    timed_out: bool = False
    blocked_import: str | None = None
    exception: str | None = None


@dataclass
class ProgramResult(RunResult):
    """Результат запуска точки входа или вызова функции модуля проекта.

    ``files`` — разобранный ``@program(expect_files=...)``:
    ``{path: (actual_json | None, diff)}``; ``diff`` пуст, когда файл
    совпал с ожидаемым. В режиме ``target`` ``stdout`` — нормализованный
    вывод программы (без хвостовых пробелов и последнего перевода строки),
    а ``returncode`` и ``stderr`` относятся к самому вызову.
    """

    files: dict[str, tuple[Any, str]] = field(default_factory=dict)


def run_code(
    code: str,
    *,
    timeout: float = 5.0,
    block_network: bool = True,
    blocked_imports: set[str] | None = None,
    extra_env: dict[str, str] | None = None,
) -> RunResult:
    """Execute Python code in a subprocess sandbox.

    Args:
        code: Python source code to execute.
        timeout: Max execution time in seconds (default 5.0).
        block_network: If True, set EGORUNNER_NO_NETWORK=1 env var (sandbox-side hint)
            and clear proxies. Real network blocking is best-effort (no seccomp on MVP).
        blocked_imports: Module names that cause a soft warning (in stderr) but NOT
            execution failure. Default: BLOCKED_IMPORTS. Use empty set to disable.
        extra_env: Extra env vars for the subprocess.

    Returns:
        RunResult with stdout, stderr, returncode, timed_out, blocked_import, exception.

    Sandbox:
        - subprocess.run with timeout, capture stdout/stderr
        - temp dir as cwd (created via tempfile.mkdtemp, removed afterwards)
        - ``-S`` flag: skip the ``site`` module so venv site-packages / editable
          installs (e.g. ``import ego``) are NOT on ``sys.path``. Stdlib is still
          available (added by the interpreter core, not by ``site``).
        - PYTHONPATH set to empty (no project imports)
        - PROXY/HTTP_PROXY cleared
        - student code wrapped in a runner script that catches exceptions and prints
          them as a special marker that we parse
    """
    tmp_dir = Path(tempfile.mkdtemp(prefix="ego-runner-"))
    try:
        # The wrapper may leave a pre-existing snapshot line; it is removed
        # here since the caller only sees the student's own output.
        wrapper = _build_wrapper(code, blocked=_blocked_set(blocked_imports))
        script_path = tmp_dir / "_ego_runner.py"
        script_path.write_text(wrapper, encoding="utf-8")
        raw = _run_subprocess(
            [sys.executable, "-S", str(script_path)],
            cwd=tmp_dir,
            timeout=timeout,
            block_network=block_network,
            extra_env=extra_env,
        )
        raw.stdout = _strip_sentinel(raw.stdout)
        return raw
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def _strip_sentinel(stdout: str) -> str:
    """Remove the wrapper's ``===EGO_PRE_EXISTING===`` first line, if any."""
    sentinel = "===EGO_PRE_EXISTING==="
    if not stdout.startswith(sentinel):
        return stdout
    _, _, rest = stdout.partition("\n")
    return rest


def _blocked_set(blocked_imports: set[str] | None) -> set[str]:
    """Requested blocked modules (``None`` → :data:`BLOCKED_IMPORTS`)."""
    return BLOCKED_IMPORTS if blocked_imports is None else blocked_imports


# === Sandbox wrapper ===

# Only `import sys` at the top: the "pre-existing blocked modules" snapshot must
# not see wrapper-internal imports (site already pulled in os, etc.).
_WRAPPER_HEAD = '''import sys


# === Blocked-import detection ===
_BLOCKED = {{ {blocked_str} }}

# Which blocked modules were in sys.modules BEFORE student code / project
# import. With only `import sys` above, this should be empty for typical
# blocks; project mode moves a module here when the wrapper or the import
# machinery (not the student's code) is what loaded it.
_pre_existing = {{m for m in sorted(_BLOCKED) if m in sys.modules}}
print("===EGO_PRE_EXISTING===" + ",".join(_pre_existing))

# Blocked modules reported so far. Project mode fills `_deferred_blocks`
# when a trace says a function was entered: a module loaded then was imported
# by the student's code, not by importing the project module.
_deferred_blocks = set()
_reported_blocks = set()


def _report_block(m):
    _reported_blocks.add(m)
    print(f"WARNING: blocked import: {{m}}", file=sys.stderr)


def _ego_trace(frame, event, arg):
    """`sys.settrace` hook of project mode: note the project function's call.

    The wrapper installs it only for import mode. Returning a local tracer
    for the wrapper's own files keeps the per-line overhead out of them; the
    called function's file is covered by ``_ego_watch_imports``.
    """
    if event == "call" and frame.f_code.co_name == _ego_call_name:
        _ego_called[0] = True
        # The call loaded `marshal` (it compiled the function's code): the
        # interpreter's own, not an import of the student's code.
        _pre_existing.add("marshal")
        for _ego_module in sorted(_BLOCKED):
            if _ego_module in sys.modules and _ego_module not in _pre_existing:
                _deferred_blocks.add(_ego_module)
    if frame.f_code.co_filename in _ego_wrapper_files or not _ego_called[0]:
        # The wrapper's own frames and the ones before the call.
        return _ego_trace
    return None


def _check_blocked_after():
    """Print WARNING for any blocked module that is in sys.modules now
    but was NOT there before exec (i.e. student imported it)."""
    for m in sorted(_BLOCKED):
        if m in sys.modules and m not in _pre_existing:
            _report_block(m)
            return m
    return None


def _print_traceback():
    """Format current exception as a simple traceback without `traceback` module."""
    exc_type, exc_value, exc_tb = sys.exc_info()
    if exc_type is None:
        return
    print(f"{{exc_type.__name__}}: {{exc_value}}", file=sys.stderr)
    # Walk the traceback chain for a minimal stack print
    tb = exc_tb
    while tb is not None:
        frame = tb.tb_frame
        co = frame.f_code
        lineno = tb.tb_lineno
        print(f'  File "{{co.co_filename}}", line {{lineno}}, in {{co.co_name}}', file=sys.stderr)
        tb = tb.tb_next


'''


def _build_wrapper(code: str, *, blocked: set[str]) -> str:
    """Build a wrapper Python script that runs student code and reports results.

    Wrapper does:
        - detects blocked imports by inspecting sys.modules AFTER exec
          (since `import os` in exec'd code may hit cached modules without
          firing the `import` audit event)
        - catches exceptions, prints structured traceback to stderr
        - normal ``print()`` s go to stdout

    Note: We deliberately only `import sys` at the top (NOT `os`, `traceback`,
    `importlib`, etc.) so that wrapper-internal imports don't pollute
    sys.modules with blocked modules. The exception handler formats the
    traceback manually via sys.exc_info() rather than using the `traceback`
    module (which transitively imports `os` on some platforms).
    """
    blocked_str = ", ".join(repr(m) for m in sorted(blocked))
    return (
        _WRAPPER_HEAD.format(blocked_str=blocked_str)
        + "# === Execute student code ===\n"
        + f"_code = {code!r}\n"
        # Not "__main__": a student's `if __name__ == "__main__": main()` (an input()
        # loop for running the program locally) must not start during checks.
        + '_namespace = { "__name__": "student", "__file__": "<ego-runner>" }\n'
        + '''
try:
    exec(_code, _namespace)
    _check_blocked_after()
except SystemExit as e:
    if e.code not in (None, 0):
        print(f"SystemExit({e.code})", file=sys.stderr)
        sys.exit(int(e.code) if isinstance(e.code, int) else 1)
except Exception:
    print("===EGO_EXCEPTION===", file=sys.stderr)
    _print_traceback()
    sys.exit(1)
'''
    )


def _parse_output(
    stdout: str, stderr: str, returncode: int, *, timed_out: bool
) -> RunResult:
    """Parse wrapper output, extract blocked import warnings and exceptions.

    blocked_import is set to the FIRST blocked top-level module detected
    (e.g. "os" not "os.path"), so tests checking "os" don't get tripped
    up by the order of submodule imports.
    """
    blocked = None
    exception = None
    clean_stderr = stderr
    for line in stderr.splitlines():
        if line.startswith("WARNING: blocked import: "):
            mod = line.split("WARNING: blocked import: ", 1)[1].strip()
            top = mod.split(".")[0]
            if blocked is None:
                blocked = top
        elif line.startswith("===EGO_EXCEPTION==="):
            exception = "yes"  # traceback follows in clean_stderr
    return RunResult(
        stdout=stdout,
        stderr=clean_stderr,
        returncode=returncode,
        timed_out=timed_out,
        blocked_import=blocked,
        exception=exception,
    )


def _run_subprocess(
    command: list[str],
    *,
    cwd: Path,
    timeout: float,
    block_network: bool,
    extra_env: dict[str, str] | None = None,
    stdin: str | None = None,
) -> RunResult:
    """Subprocess step of both :func:`run_code` and project runs."""
    env: dict[str, str] = {
        "PYTHONPATH": "",  # no project imports
        "PYTHONIOENCODING": "utf-8",
        "PYTHONUTF8": "1",
    }
    if block_network:
        env["EGORUNNER_NO_NETWORK"] = "1"
        # Clear proxy env vars (best-effort)
        for k in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"):
            env[k] = ""
    if extra_env:
        env.update(extra_env)

    # Run. -S skips the site module so editable installs / site-packages are not
    # importable (prevents `import ego` leaking project code into the sandbox).
    try:
        proc = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(cwd),
            env={**os.environ, **env},  # inherit + override
            encoding="utf-8",
            errors="replace",
            input="" if stdin is None else stdin,
        )
        return _parse_output(proc.stdout, proc.stderr, proc.returncode, timed_out=False)
    except subprocess.TimeoutExpired as e:
        return RunResult(
            stdout=(
                e.stdout.decode("utf-8", errors="replace")
                if isinstance(e.stdout, bytes)
                else (e.stdout or "")
            ),
            stderr=(
                e.stderr.decode("utf-8", errors="replace")
                if isinstance(e.stderr, bytes)
                else (e.stderr or "")
            ),
            returncode=-1,
            timed_out=True,
        )
    except Exception as e:
        return RunResult(stdout="", stderr=str(e), returncode=-1, exception=type(e).__name__)


# === Function-level observation helpers ===

# Copied verbatim (source) into the wrapper: the sandbox cannot import ego.
_FUNCTION_HELPERS = (
    _ego_same_value,
    _ego_mutable_ids,
    _ego_program_failure,
    _ego_same_file,
    _ego_watch_imports,
    _ego_import_function,
)

# The call runs wherever ``_ego_func`` is bound: inside the exec'd namespace
# (``run_function``) or at wrapper top level (project import mode). The same
# template observes arguments/results in exactly the same way in both.
_CALL_TEMPLATE = '''# === Call function and print return value ===
_ego_args = list({args!r})
_ego_kwargs = {kwargs!r}
for _ego_target_path, _ego_source_path in {input_aliases!r}:
    _ego_source = _ego_args
    for _ego_part in _ego_source_path:
        _ego_source = _ego_source[_ego_part]
    _ego_target = _ego_args
    for _ego_part in _ego_target_path[:-1]:
        _ego_target = _ego_target[_ego_part]
    _ego_target[_ego_target_path[-1]] = _ego_source
if {check_inputs_unchanged!r}:
    from copy import deepcopy as _ego_deepcopy
    _ego_snapshot = _ego_deepcopy((_ego_args, _ego_kwargs))
_result = _ego_func(*_ego_args, **_ego_kwargs)
if {check_inputs_unchanged!r}:
    assert _ego_same_value((_ego_args, _ego_kwargs), _ego_snapshot), "input arguments were modified"
if {check_result_isolated!r}:
    assert not (_ego_mutable_ids(_result) & _ego_mutable_ids((_ego_args, _ego_kwargs))), "result shares mutable data with input"
print("===EGO_RETURN===")
print(repr(_result))
'''


def _call(
    args: tuple,
    kwargs: dict,
    input_aliases: tuple,
    check_inputs_unchanged: bool,
    check_result_isolated: bool,
) -> str:
    """Render :data:`_CALL_TEMPLATE`; ``_ego_func`` must already be bound."""
    return _CALL_TEMPLATE.format(
        args=args,
        kwargs=kwargs,
        input_aliases=input_aliases,
        check_inputs_unchanged=check_inputs_unchanged,
        check_result_isolated=check_result_isolated,
    )


# === Convenience: run a function with given args ===


def run_function(
    code: str,
    function_name: str,
    args: tuple = (),
    kwargs: dict | None = None,
    *,
    timeout: float = 5.0,
    block_network: bool = True,
    blocked_imports: set[str] | None = None,
    check_inputs_unchanged: bool = False,
    check_result_isolated: bool = False,
    input_aliases: tuple = (),
) -> RunResult:
    """Run a function from ``code`` with given args, capture its return value.

    The wrapper imports ``code``, then calls ``function_name(*args, **kwargs)``,
    prints the return value as ``repr`` (so caller can compare).

    Useful for checker: run student's ``task_X(...)`` and ref's ``task_X(...)``,
    compare reprs.

    Args:
        code: Python source defining the function.
        function_name: Function to call.
        args: Positional args.
        kwargs: Keyword args.
        timeout, block_network, blocked_imports: see :func:`run_code`.

    Returns:
        RunResult. If function returned, stdout contains
        ``"===EGO_RETURN===\\n<repr of return value>\\n"``.
    """
    kwargs = kwargs or {}
    observation_helpers = ""
    if check_inputs_unchanged or check_result_isolated:
        observation_helpers = "\n".join(
            inspect.getsource(fn) for fn in (_ego_same_value, _ego_mutable_ids)
        )
    call = _call(
        args, kwargs, input_aliases, check_inputs_unchanged, check_result_isolated
    )
    # NOTE: the caller is appended to `code` and exec'd inside `_namespace`.
    # Inside the exec'd code, `globals()` returns `_namespace`, so we use that
    # to look up the function. `traceback` is imported locally because it lives
    # in the wrapper's module globals, not in `_namespace`.
    caller = (
        "\n\n# === Call function and print return value ===\n"
        "import sys as _sys\n"
        "import traceback as _tb\n"
        f"{observation_helpers}\n"
        "try:\n"
        f"    _ego_func = globals().get({function_name!r})\n"
        "    if _ego_func is None:\n"
        '        print("===EGO_NO_FUNCTION===", file=_sys.stderr)\n'
        "        _sys.exit(1)\n"
        + _indent(call, "    ")
        + '''except Exception:
    print("===EGO_EXCEPTION===", file=_sys.stderr)
    _tb.print_exc()
    _sys.exit(1)
'''
    )
    full_code = code + caller
    result = run_code(
        full_code,
        timeout=timeout,
        block_network=block_network,
        blocked_imports=blocked_imports,
    )
    return result


def parse_return_value(stdout: str) -> str | None:
    """Extract the repr of return value from :func:`run_function` stdout.

    Returns ``None`` if no return value was printed.
    """
    marker = "===EGO_RETURN==="
    idx = stdout.find(marker)
    if idx < 0:
        return None
    after = stdout[idx + len(marker):].lstrip("\n")
    # Take first line as repr (may be multi-line, but keep simple)
    return after.rstrip("\n")


# === Project mode (ADR-0018 D18.4) ===


def workspace_config(
    workspace: dict | None = None,
    *,
    entry: str | None = None,
    include: list[str] | None = None,
    max_files: int | None = None,
    max_bytes: int | None = None,
) -> dict:
    """Normalise a workspace spec; explicit keywords win over ``workspace``."""
    merged: dict[str, Any] = {
        "entry": DEFAULT_ENTRY,
        "include": list(DEFAULT_INCLUDE),
        "max_files": DEFAULT_MAX_FILES,
        "max_bytes": DEFAULT_MAX_BYTES,
    }
    merged.update(workspace or {})
    for key, value in (
        ("entry", entry),
        ("include", include),
        ("max_files", max_files),
        ("max_bytes", max_bytes),
    ):
        if value is not None:
            merged[key] = value
    merged["include"] = [str(pattern) for pattern in merged["include"]]
    return merged


def check_project_path(path: str) -> str | None:
    """Why ``path`` is not an acceptable project file name (None = fine)."""
    if not isinstance(path, str) or not path:
        return "путь к файлу пустой"
    if "\\" in path:
        return f"путь `{path}` должен быть записан через `/`, а не `\\`"
    if path.startswith("/") or (len(path) > 1 and path[1] == ":"):
        return f"путь `{path}` абсолютный — файлы проекта задаются относительно папки проекта"
    parts = path.split("/")
    if ".." in parts:
        return f"путь `{path}` выходит за папку проекта (`..` запрещён)"
    if "" in parts or "." in parts:
        return f"путь `{path}` некорректен: лишние `/` или сегменты `.`"
    reserved = [part for part in parts if part in _RESERVED_DIRS]
    if reserved:
        return f"путь `{path}`: папку `{reserved[0]}/` писать нельзя"
    return None


def include_matches(path: str, include: list[str]) -> bool:
    """``*.py`` matches every basename; ``data/*.json`` — a path pattern."""
    name = PurePosixPath(path).name
    for pattern in include:
        if fnmatch.fnmatchcase(path, pattern):
            return True
        if "/" not in pattern and fnmatch.fnmatchcase(name, pattern):
            return True
    return False


def validate_project_files(files: dict[str, str], workspace: dict | None = None) -> list[str]:
    """Check a project submission against the workspace; Russian messages.

    Only relative POSIX paths are accepted: no ``..``, no absolute or
    backslash paths, no ``.cogito/``, ``__pycache__/`` or ``.venv/``. Every
    file must match ``include``; ``max_files`` and ``max_bytes`` (UTF-8 size
    of all contents) are enforced. Returns ``[]`` for a valid project.
    """
    if not isinstance(files, dict):
        return ["файлы проекта должны быть словарём {путь: содержимое}"]
    spec = workspace_config(workspace)
    errors: list[str] = []
    total = 0
    for path, content in files.items():
        problem = check_project_path(path)
        if problem is not None:
            errors.append(problem)
            continue
        if not isinstance(content, str):
            errors.append(f"содержимое `{path}` должно быть строкой")
            continue
        if not include_matches(path, spec["include"]):
            patterns = ", ".join(f"`{pattern}`" for pattern in spec["include"])
            errors.append(f"файл `{path}` не входит в проект (ожидаются: {patterns})")
            continue
        total += len(content.encode("utf-8"))
    if not errors and len(files) > spec["max_files"]:
        errors.append(
            f"в проекте {len(files)} файлов — это больше лимита {spec['max_files']}"
        )
    if not errors and total > spec["max_bytes"]:
        errors.append(
            f"проект занимает {total} байт — это больше лимита {spec['max_bytes']}"
        )
    return errors


def project_view(files: dict[str, str]) -> str:
    """Concatenated view of a project for AI and history (``# === path ===``)."""
    return "\n\n".join(f"# === {path} ===\n{files[path]}" for path in sorted(files))


def run_project(
    files: dict[str, str],
    *,
    target: str | None = None,
    entry: str | None = None,
    args: tuple = (),
    kwargs: dict | None = None,
    stdin: str = "",
    expected_stdout: str | None = None,
    match: str = "lines",
    expected_exit: int | None = None,
    expect_files: dict | None = None,
    workspace: dict | None = None,
    timeout: float = 5.0,
    block_network: bool = True,
    blocked_imports: set[str] | None = None,
    check_inputs_unchanged: bool = False,
    check_result_isolated: bool = False,
    input_aliases: tuple = (),
) -> ProgramResult:
    """Run a multi-file project in a temp copy (ADR-0018 D18.4).

    Exactly one of ``target`` (``"module.func"``: import the module and call
    the function; its ``repr`` follows ``===EGO_RETURN===`` in stdout) or
    ``entry`` (``python -S <entry>`` with ``stdin``) must be given; without an
    explicit ``entry`` the workspace entry (``main.py``) is used.

    Files are laid out at their relative paths in a fresh temp dir that is
    the working directory. In ``target`` mode the temp dir goes first on
    ``sys.path`` and the module runs under its own name, so its
    ``if __name__ == "__main__"`` block does not start.

    Raises:
        SandboxError: invalid ``files`` (see :func:`validate_project_files`)
            or an unknown ``match`` mode. A missing entry file is returned
            as an errored :class:`ProgramResult`, not raised.
    """
    errors = validate_project_files(files, workspace)
    if errors:
        raise SandboxError("; ".join(errors))
    if match not in ("exact", "lines", "contains"):
        raise SandboxError(f"неизвестный режим сравнения: {match!r}")
    target_name, func_name = _split_target(target) if target is not None else (None, None)
    if target_name is None:
        entry = entry if entry is not None else workspace_config(workspace)["entry"]

    tmp_dir = Path(tempfile.mkdtemp(prefix="ego-project-"))
    try:
        for path in sorted(files):
            # Paths passed validate_project_files, so they stay in tmp_dir.
            destination = tmp_dir.joinpath(*path.split("/"))
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(files[path], encoding="utf-8")

        if target_name is not None:
            result = _run_target(
                tmp_dir,
                target_name,
                func_name,
                args=args,
                kwargs=kwargs or {},
                check_inputs_unchanged=check_inputs_unchanged,
                check_result_isolated=check_result_isolated,
                input_aliases=input_aliases,
                timeout=timeout,
                block_network=block_network,
                blocked_imports=blocked_imports,
            )
        else:
            result = _run_entry(
                tmp_dir,
                entry=entry or DEFAULT_ENTRY,
                stdin=stdin,
                expected_stdout=expected_stdout or "",
                match=match,
                expected_exit=expected_exit,
                timeout=timeout,
                block_network=block_network,
            )

        if expect_files and not (result.exception or result.timed_out):
            _check_expected_files(result, tmp_dir, expect_files)
        return result
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def _split_target(target: str) -> tuple[str, str]:
    """``"commands.parse_command"`` → ``("commands", "parse_command")``."""
    module_name, _, func_name = target.rpartition(".")
    valid = module_name and all(
        part.isidentifier() for part in module_name.split(".")
    ) and func_name.isidentifier()
    if not valid:
        raise SandboxError(
            "target должен быть вида `модуль.функция` "
            f"(например, commands.parse_command), а не {target!r}"
        )
    return module_name, func_name


# Runs at the end of a call: top-level imports of the project module were
# reported by ``_ego_import_function`` already, blocked modules imported by
# the student's functions are reported now if the call failed (a successful
# call reports them the moment they load, from the import tracer).
_TARGET_BLOCKED_REPORT = """for _ego_name in sorted(_deferred_blocks):
    if _ego_name in sys.modules and _ego_name not in _reported_blocks:
        _report_block(_ego_name)
"""


def _wrapper_prefix(blocked_imports: set[str] | None) -> str:
    """Wrapper head + import-free helper sources, ready for project code."""
    blocked_str = ", ".join(repr(m) for m in sorted(_blocked_set(blocked_imports)))
    helpers = "\n\n".join(inspect.getsource(fn) for fn in _FUNCTION_HELPERS)
    return _WRAPPER_HEAD.format(blocked_str=blocked_str) + helpers + "\n"


def _indent(text: str, prefix: str) -> str:
    """Indent every non-empty line of ``text`` (for embedding inside ``try:``)."""
    return "".join(
        prefix + line if line.strip() else line
        for line in text.splitlines(keepends=True)
    )


_BLOCKED_WARNING = "WARNING: blocked import: "


def _blocked_warning_module(line: str) -> str | None:
    """Module name of a ``WARNING: blocked import: <module>`` line, else None."""
    if not line.startswith(_BLOCKED_WARNING):
        return None
    return line[len(_BLOCKED_WARNING) :].strip()


def _run_target(
    tmp_dir: Path,
    module_name: str,
    func_name: str,
    *,
    args: tuple,
    kwargs: dict,
    check_inputs_unchanged: bool,
    check_result_isolated: bool,
    input_aliases: tuple,
    timeout: float,
    block_network: bool,
    blocked_imports: set[str] | None,
) -> ProgramResult:
    """Import ``module_name`` from the project and call ``func_name``."""
    call = _call(args, kwargs, input_aliases, check_inputs_unchanged, check_result_isolated)
    # Everything that runs lives in one try-block; the whole file is then
    # indented (``_call`` is flat on its own, see run_function).
    body = (
        "# `importlib` is imported only here, after the pre-existing snapshot.\n"
        "import importlib  # noqa: F401 — used by _ego_import_function\n"
        f"_ego_func = _ego_import_function({str(tmp_dir)!r}, {module_name!r}, {func_name!r})\n"
        "if _ego_func is None:\n"
        "    sys.exit(1)\n"
        # From here on a blocked import belongs to the student's code.
        f"_ego_call_name = {func_name!r}\n"
        "_ego_called = [False]\n"
        "_ego_wrapper_files = {__file__}\n"
        "sys.settrace(_ego_trace)\n" + call + _TARGET_BLOCKED_REPORT
    )
    code = (
        _wrapper_prefix(blocked_imports)
        + "\n# === Import the project module and call its function ===\n"
        + "try:\n"
        + _indent(body, "    ")
        + '''except SystemExit:
    raise
except Exception:
    print("===EGO_EXCEPTION===", file=sys.stderr)
    # The traceback module pulls in `os`; importing it here (not above) keeps
    # the blocked-import check from mistaking it for a student import.
    import traceback
    traceback.print_exc()
    sys.exit(1)
'''
    )
    script_path = tmp_dir / "_ego_project_runner.py"
    script_path.write_text(code, encoding="utf-8")
    raw = _run_subprocess(
        [sys.executable, "-S", str(script_path)],
        cwd=tmp_dir,
        timeout=timeout,
        block_network=block_network,
    )
    # Drop the wrapper's own imports (see ``_WRAPPER_IMPORTS``) from both the
    # field and stderr; other warnings stay.
    blocked = raw.blocked_import
    stderr = "".join(
        line
        for line in raw.stderr.splitlines(keepends=True)
        if _blocked_warning_module(line) not in _WRAPPER_IMPORTS
    )
    if blocked is not None and blocked in _WRAPPER_IMPORTS:
        blocked = None
    # Without one, blocked modules the student's functions imported stay
    # silent — the tracer always prints something now.
    if blocked is None:
        stderr = "".join(
            line
            for line in stderr.splitlines(keepends=True)
            if _blocked_warning_module(line) is None
        )
    return ProgramResult(
        # Program output before the return value is what @program compares.
        stdout=_ego_normalize(_strip_sentinel(raw.stdout)),
        stderr=stderr,
        returncode=raw.returncode,
        timed_out=raw.timed_out,
        blocked_import=blocked,
        exception=raw.exception,
    )


def _run_entry(
    tmp_dir: Path,
    *,
    entry: str,
    stdin: str,
    expected_stdout: str,
    match: str,
    expected_exit: int | None,
    timeout: float,
    block_network: bool,
) -> ProgramResult:
    """Run ``python -S <entry>`` with ``stdin``; compare stdout / exit code."""
    problem = check_project_path(entry)
    entry_path = None if problem is not None else tmp_dir.joinpath(*entry.split("/"))
    if problem is not None or entry_path is None or not entry_path.is_file():
        return ProgramResult(
            stdout="",
            stderr=f"файл точки входа `{entry}` не найден в проекте",
            returncode=-1,
            exception="FileNotFoundError",
        )
    raw = _run_subprocess(
        [sys.executable, "-S", entry],
        cwd=tmp_dir,
        timeout=timeout,
        block_network=block_network,
        stdin=stdin,
    )
    stdout = _strip_sentinel(raw.stdout)
    result = ProgramResult(
        stdout=_cap_output(stdout),
        stderr=raw.stderr,
        returncode=raw.returncode,
        timed_out=raw.timed_out,
        blocked_import=raw.blocked_import,
        exception=raw.exception,
    )
    if raw.timed_out or raw.exception:
        return result
    # An empty ``expected_stdout`` means "no output checked", as for the
    # fixed lines a task prints (ADR-0018 D18.3).
    if expected_stdout.strip() and _ego_program_failure(stdout, expected_stdout, match) is not None:
        result.returncode = 1
        result.stderr = (
            f"stdout mismatch ({match}):\n"
            f"--- expected ---\n{expected_stdout.rstrip()}\n"
            f"--- actual ---\n{stdout.rstrip()}"
        )
    elif expected_exit is not None and raw.returncode != expected_exit:
        result.returncode = 1
        result.stderr = f"exit code {raw.returncode}, expected {expected_exit}"
    return result


def _cap_output(text: str) -> str:
    """Truncate runaway stdout so a tooltip stays readable."""
    if len(text) <= MAX_PROGRAM_OUTPUT:
        return text
    return text[:MAX_PROGRAM_OUTPUT] + "\n… (вывод обрезан)"


def _check_expected_files(result: ProgramResult, tmp_dir: Path, expected: dict) -> None:
    """Fill ``result.files``; a mismatch fails the run with a short reason.

    Only files the run left on disk are checked (a program that failed
    before writing them has already failed for its own reason). A reason
    names the first difference: «ожидалось X, получено Y» or a plain error.
    """
    for path, wanted in expected.items():
        problem = check_project_path(path)
        if problem is not None:
            result.files[path] = (None, problem)
        else:
            result.files[path] = _read_json(tmp_dir, path, wanted)
    mismatched = [path for path, (_actual, diff) in result.files.items() if diff]
    if mismatched and result.returncode == 0:
        result.returncode = 1
        result.stderr = "файлы после запуска не совпали: " + "; ".join(
            f"`{path}`: {result.files[path][1]}" for path in mismatched
        )


def _read_json(tmp_dir: Path, path: str, wanted: Any) -> tuple[Any, str]:
    """``(parsed JSON, "")`` for a matching file, else ``(None, difference)``."""
    try:
        actual = json.loads(tmp_dir.joinpath(*path.split("/")).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, "файл не создан"
    except (OSError, ValueError):
        return None, "это не JSON"
    if _json_equal(actual, wanted):
        return actual, ""
    return actual, f"ожидалось {_json_text(wanted)}, получено {_json_text(actual)}"


def _json_equal(left: Any, right: Any) -> bool:
    """JSON equality: ``True`` is not ``1``, number order and dict order ignored."""
    if isinstance(left, bool) or isinstance(right, bool):
        return type(left) is type(right) and left == right
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return left == right
    if isinstance(left, dict) and isinstance(right, dict):
        return left.keys() == right.keys() and all(
            _json_equal(left[key], right[key]) for key in left
        )
    if isinstance(left, list) and isinstance(right, list):
        return len(left) == len(right) and all(
            _json_equal(a, b) for a, b in zip(left, right)
        )
    return type(left) is type(right) and left == right


def _json_text(value: Any) -> str:
    """Compact, readable rendering of a JSON value for a diff message."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True)
