"""Helpers whose source is embedded into the sandbox wrapper by ``ego.runner``.

The sandbox runs ``python -S``, so the installed ``ego`` package is not
importable there. Runner copies these functions verbatim into the wrapper
script instead (``inspect.getsource``), and they must stay import-free.
"""


def _ego_same_value(left, right):
    """Compare literal data, ignoring dict order but retaining scalar types."""
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return len(left) == len(right) and all(
            any(
                _ego_same_value(key, other_key) and _ego_same_value(value, other_value)
                for other_key, other_value in right.items()
            )
            for key, value in left.items()
        )
    if isinstance(left, (list, tuple)):
        return len(left) == len(right) and all(
            _ego_same_value(a, b) for a, b in zip(left, right)
        )
    if isinstance(left, (set, frozenset)):
        return len(left) == len(right) and all(
            any(_ego_same_value(a, b) for b in right) for a in left
        )
    return left == right


def _ego_mutable_ids(value, seen=None):
    """Find mutable containers in literal data, including nested aliases."""
    if seen is None:
        seen = set()
    if id(value) in seen:
        return set()
    seen.add(id(value))
    found = {id(value)} if isinstance(value, (dict, list, set)) else set()
    if isinstance(value, dict):
        children = value.values()
    elif isinstance(value, (list, tuple, set, frozenset)):
        children = value
    else:
        children = ()
    for child in children:
        found.update(_ego_mutable_ids(child, seen))
    return found


def _ego_normalize_stdout(text):
    """Program output for ``@program``: no trailing spaces, no final newline."""
    return "\n".join(line.rstrip() for line in text.replace("\r\n", "\n").split("\n"))


def _ego_normalize(text):
    """Output without trailing spaces and without empty lines at the end."""
    return _ego_normalize_stdout(text).rstrip("\n")


def _ego_strip_indent(text):
    """Drop the common leading whitespace (so stdout comparisons ignore indents)."""
    lines = _ego_normalize_stdout(text).split("\n")
    indents = [
        len(line) - len(line.lstrip())
        for line in lines
        if line.strip()
    ]
    shift = min(indents) if indents else 0
    return "\n".join(line[shift:] if line.strip() else "" for line in lines)


def _ego_program_failure(actual, expected, match="lines"):
    """Reason an ``@program`` output differs from the expected one, or None.

    ``match``:

    - ``lines`` (default) — the same non-empty lines, leading indentation
      ignored;
    - ``exact`` — the same lines, trailing spaces and empty lines at the end
      not counted;
    - ``contains`` — the expected non-empty lines appear among the output's
      lines, in order (a run may also print more).
    """
    if match == "exact":
        return None if _ego_normalize(actual) == _ego_normalize(expected) else "exact"
    wanted = [line for line in _ego_strip_indent(expected).split("\n") if line.strip()]
    if match == "contains":
        text = _ego_strip_indent(actual)
        position = 0
        for line in wanted:
            found = text.find(line, position)
            if found < 0:
                return "contains"
            position = found + len(line)
        return None
    printed = [line for line in _ego_strip_indent(actual).split("\n") if line.strip()]
    return None if printed == wanted else "lines"


def _ego_import_function(tempdir, module_name, func_name):
    """Callable ``func_name`` of ``module_name`` in the project copy, or None.

    The project root goes first on ``sys.path``; a module runs under its own
    name, so its ``if __name__ == "__main__"`` block does not run here.
    ``sys`` and ``importlib`` (imported by the wrapper just before the call,
    so the blocked-import snapshot stays clean) and ``_print_traceback``
    come from the wrapper's globals.
    """
    if tempdir not in sys.path:
        sys.path.insert(0, tempdir)
    try:
        module = importlib.import_module(module_name)
    except Exception:
        print("===EGO_EXCEPTION===", file=sys.stderr)
        _print_traceback()
        return None
    func = getattr(module, func_name, None)
    if not callable(func):
        print("===EGO_NO_FUNCTION===", file=sys.stderr)
        return None
    return func
