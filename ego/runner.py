"""Runner — executes Python code in a subprocess sandbox.

Используется ego.checker для запуска решения студента и эталона
в одинаковых условиях (timeout, no network, temp dir, blocked imports).

See ADR-0001 D12 (sandbox для ego check) and D9 (сервер не выполняет
студенческий код — check всегда локален).
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


# Зависимости, которые студенту запрещено использовать
# (защита от exfil, file system access).
BLOCKED_IMPORTS: set[str] = {
    "os", "subprocess", "socket", "urllib", "http", "ctypes",
    "multiprocessing", "threading", "signal", "asyncio",
    "shutil", "pathlib", "pickle", "marshal",
}


@dataclass
class RunResult:
    """Результат выполнения кода в sandbox."""

    stdout: str
    stderr: str
    returncode: int
    timed_out: bool = False
    blocked_import: str | None = None
    exception: str | None = None


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
        - temp dir as cwd (created via tempfile.mkdtemp, NOT cleaned — caller cleans)
        - ``-S`` flag: skip the ``site`` module so venv site-packages / editable
          installs (e.g. ``import ego``) are NOT on ``sys.path``. Stdlib is still
          available (added by the interpreter core, not by ``site``).
        - PYTHONPATH set to empty (no project imports)
        - PROXY/HTTP_PROXY cleared
        - student code wrapped in a runner script that catches exceptions and prints
          them as a special marker that we parse
    """
    blocked = blocked_imports if blocked_imports is not None else BLOCKED_IMPORTS

    # Build wrapper script
    wrapper = _build_wrapper(code, blocked_imports=blocked)

    # Create temp dir
    tmp_dir = Path(tempfile.mkdtemp(prefix="ego-runner-"))
    script_path = tmp_dir / "_ego_runner.py"
    script_path.write_text(wrapper, encoding="utf-8")

    # Build env
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
            [sys.executable, "-S", str(script_path)],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(tmp_dir),
            env={**os.environ, **env},  # inherit + override
            encoding="utf-8",
            errors="replace",
        )
        result = _parse_output(
            proc.stdout, proc.stderr, proc.returncode, timed_out=False
        )
        return result
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


def _build_wrapper(code: str, *, blocked_imports: set[str]) -> str:
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
    blocked_str = ", ".join(repr(m) for m in sorted(blocked_imports))
    return f'''import sys


# === Blocked-import detection ===
_BLOCKED = {{ {blocked_str} }}

# Snapshot which blocked modules were in sys.modules BEFORE student code.
# With only `import sys` above, this should be empty for typical blocks.
_pre_existing = {{m for m in _BLOCKED if m in sys.modules}}


def _check_blocked_after():
    """Print WARNING for any blocked module that is in sys.modules now
    but was NOT there before exec (i.e. student imported it)."""
    for m in _BLOCKED:
        if m in sys.modules and m not in _pre_existing:
            print(f"WARNING: blocked import: {{m}}", file=sys.stderr)
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


# === Execute student code ===
_code = {code!r}
_namespace = {{ "__name__": "__main__", "__file__": "<ego-runner>" }}

try:
    exec(_code, _namespace)
    _check_blocked_after()
except SystemExit as e:
    if e.code not in (None, 0):
        print(f"SystemExit({{e.code}})", file=sys.stderr)
        sys.exit(int(e.code) if isinstance(e.code, int) else 1)
except Exception:
    print("===EGO_EXCEPTION===", file=sys.stderr)
    _print_traceback()
    sys.exit(1)
'''


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
    # NOTE: the caller is appended to `code` and exec'd inside `_namespace`.
    # Inside the exec'd code, `globals()` returns `_namespace`, so we use that
    # to look up the function. `traceback` is imported locally because it lives
    # in the wrapper's module globals, not in `_namespace`.
    caller = f'''

# === Call function and print return value ===
import sys as _sys
import traceback as _tb
try:
    _func = globals().get({function_name!r})
    if _func is None:
        print("===EGO_NO_FUNCTION===", file=_sys.stderr)
        _sys.exit(1)
    _result = _func(*{args!r}, **{kwargs!r})
    print("===EGO_RETURN===")
    print(repr(_result))
except Exception:
    print("===EGO_EXCEPTION===", file=_sys.stderr)
    _tb.print_exc()
    _sys.exit(1)
'''
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
