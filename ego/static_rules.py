"""Static rules — AST checks of the student's code (opt-in per task).

Behaviour tests only observe return values, so a statement like «не используй
``sorted``» cannot be enforced by ``@case`` alone: ``sorted(a + b)`` passes a
merge-sort task. ``@rules`` (``ego.testing``) declares extra AST rules in the
task's ``.tests.py`` and this module evaluates them.

Pure module (stdlib only). See ``docs/TESTS_DESIGN.md``.

Rule keys (each yields at most one violation — the first line number):

- ``forbid_names``      — bare ``Name`` used anywhere: ``sorted(...)``, ``x = max``
- ``forbid_methods``    — ``x.sort(...)`` (attribute of another value)
- ``forbid_imports``    — ``import math`` / ``from math import ...`` (and calls
  through an imported module, e.g. ``math.sqrt(4)``)
- ``forbid_nodes``      — any ``ast`` node of that class (``Global``, ``Lambda``, ...)
- ``require_functions`` — top-level ``def`` / ``async def`` with that name

Functions named ``given_*`` (GIVEN helpers from starters) are always exempt
from the ``forbid_*`` rules; ``allow_in`` names more exempt functions.
"""

from __future__ import annotations

import ast
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass, field
from typing import Any

GIVEN_PREFIX = "given_"
# Description prefix of every static-rule result; the CLI, server and the
# extension use it to render «Правило» rows separately from behaviour cases.
RULE_PREFIX = "Правило: "

# Human wording for common forbidden nodes; other classes fall back to the name.
_NODE_HINTS: dict[str, str] = {
    "ListComp": "list comprehension",
    "SetComp": "set comprehension",
    "DictComp": "dict comprehension",
    "GeneratorExp": "генераторное выражение",
    "Global": "global",
    "Nonlocal": "nonlocal",
    "Lambda": "lambda",
    "While": "while",
    "Try": "try/except",
}

_KNOWN_NODES: dict[str, type[ast.AST]] = {
    name: obj
    for name, obj in vars(ast).items()
    if isinstance(obj, type) and issubclass(obj, ast.AST) and obj is not ast.AST
}
# Covered by dedicated keys — mixing them into forbid_nodes would be ambiguous.
_DEDICATED_NODES = {"Name": "forbid_names", "Attribute": "forbid_methods"}


@dataclass(frozen=True)
class Rules:
    """Normalised ``@rules(...)`` declaration attached to a task function."""

    __test__ = False  # not a pytest test class

    forbid_names: tuple[str, ...] = ()
    forbid_methods: tuple[str, ...] = ()
    forbid_imports: tuple[str, ...] = ()
    forbid_nodes: tuple[str, ...] = ()  # ast node class names
    require_functions: tuple[str, ...] = ()
    allow_in: tuple[str, ...] = ()
    # Rule key -> custom message. Keys are the declared names ("sorted",
    # "sort", "math", "Global"); "method:sort" also works for methods.
    messages: dict[str, str] = field(default_factory=dict)

    def message_for(self, violation: Violation) -> str:
        """Custom message for ``violation``, else its default text (no prefix)."""
        return self.messages.get(violation.key) or self.messages.get(violation.trigger)

    @property
    def is_empty(self) -> bool:
        return not (
            self.forbid_names
            or self.forbid_methods
            or self.forbid_imports
            or self.forbid_nodes
            or self.require_functions
        )


@dataclass(frozen=True)
class Violation:
    """One static-rule violation (at most one per ``trigger``).

    ``trigger`` is the declared rule name: ``"sorted"`` (name), ``"sort"``
    (method), ``"math"`` (import), ``"Global"`` (node) or
    ``"parse_command"`` (required function). It is looked up in ``messages``
    and used as the result's ``expected_repr``.

    ``rule`` says which rule kind fired (``name``, ``method``, ``import``,
    ``node``, ``function``) and ``key`` combines both (``"name:sorted"``).
    """

    __test__ = False  # not a pytest test class

    trigger: str
    rule: str
    text: str  # reason, e.g. "нельзя использовать `sorted`"
    line: int | None = None  # 1-based; None for a missing function

    @property
    def key(self) -> str:
        return f"{self.rule}:{self.trigger}"

    @property
    def description(self) -> str:
        """Student-facing description: «Правило: <reason> (строка N)»."""
        return format_violation(self)


def format_violation(violation: Violation, text: str | None = None) -> str:
    """«Правило: <text|reason> (строка N)»; no line for missing functions."""
    reason = violation.text if text is None else text
    if violation.line is None:
        return f"{RULE_PREFIX}{reason}"
    return f"{RULE_PREFIX}{reason} (строка {violation.line})"


# === Declaration validation ===


def build_rules(
    *,
    forbid_names: Iterable[str] = (),
    forbid_methods: Iterable[str] = (),
    forbid_imports: Iterable[str] = (),
    forbid_nodes: Iterable[str] = (),
    require_functions: Iterable[str] = (),
    allow_in: Iterable[str] = (),
    messages: dict[str, str] | None = None,
) -> Rules:
    """Validate ``@rules`` arguments and normalise them into ``Rules``.

    Raises ``ValueError`` for an unknown ast node name, a bare string instead
    of a list, a malformed name, or a message key that matches no rule.
    """
    names = _name_list("forbid_names", forbid_names)
    methods = _name_list("forbid_methods", forbid_methods)
    required = _name_list("require_functions", require_functions)
    allowed = _name_list("allow_in", allow_in)
    imports = _name_list("forbid_imports", forbid_imports, dotted=True)
    nodes = _node_list(forbid_nodes)
    msgs = _messages(messages, names=names, methods=methods, imports=imports, nodes=nodes)
    return Rules(
        forbid_names=names,
        forbid_methods=methods,
        forbid_imports=imports,
        forbid_nodes=nodes,
        require_functions=required,
        allow_in=allowed,
        messages=msgs,
    )


def _name_list(argname: str, value: Iterable[str], *, dotted: bool = False) -> tuple[str, ...]:
    if isinstance(value, (str, bytes)):
        raise ValueError(f"@rules {argname} must be a list of names, not a string")
    out: list[str] = []
    for raw in value:
        if not isinstance(raw, str) or not raw.strip():
            raise ValueError(f"@rules {argname} entries must be non-empty strings, got {raw!r}")
        item = raw.strip()
        parts = item.split(".") if dotted else [item]
        if not all(part.isidentifier() for part in parts):
            raise ValueError(f"@rules {argname}: {item!r} is not a valid name")
        if item not in out:
            out.append(item)
    return tuple(out)


def _node_list(value: Iterable[str]) -> tuple[str, ...]:
    if isinstance(value, (str, bytes)):
        raise ValueError("@rules forbid_nodes must be a list of names, not a string")
    out: list[str] = []
    for raw in value:
        if not isinstance(raw, str) or not raw.strip():
            raise ValueError(f"@rules forbid_nodes entries must be strings, got {raw!r}")
        item = raw.strip()
        if item not in _KNOWN_NODES:
            raise ValueError(
                f"@rules forbid_nodes: unknown ast node {item!r} "
                "(use an ast class name such as 'Lambda' or 'ListComp')"
            )
        if item in _DEDICATED_NODES:
            raise ValueError(
                f"@rules forbid_nodes: {item!r} has a dedicated key "
                f"({_DEDICATED_NODES[item]!r}); use it instead"
            )
        if item not in out:
            out.append(item)
    return tuple(out)


def _messages(
    messages: dict[str, str] | None,
    *,
    names: Sequence[str],
    methods: Sequence[str],
    imports: Sequence[str],
    nodes: Sequence[str],
) -> dict[str, str]:
    if messages is None:
        return {}
    if not isinstance(messages, dict):
        raise ValueError("@rules messages must be a dict {rule key: text}")
    known = {*names, *methods, *imports, *nodes}
    out: dict[str, str] = {}
    for key, text in messages.items():
        if not isinstance(text, str) or not text.strip():
            raise ValueError(f"@rules messages[{key!r}] must be a non-empty string")
        # Accept both "sort" and its qualified form "method:sort".
        bare = key.split(":", 1)[-1] if isinstance(key, str) else key
        if bare not in known:
            raise ValueError(
                f"@rules messages: {key!r} matches no rule key (known: {sorted(known)})"
            )
        out[str(bare)] = " ".join(text.split())
    return out


# === Evaluation ===


def evaluate(
    source: str,
    rules: Rules,
    *,
    skip_functions: Iterable[str] = (),
) -> list[Violation]:
    """Evaluate ``rules`` on Python ``source``; violations in declaration order.

    ``skip_functions`` (the solution's ``task_*`` entry point, whose existence
    the cases already verify) are ignored by ``require_functions``.
    ``given_*`` and ``rules.allow_in`` functions are exempt from ``forbid_*``.

    Raises ``SyntaxError`` if ``source`` does not parse (callers keep their
    previous behaviour for syntax errors).
    """
    if rules.is_empty:
        return []
    return check_tree(ast.parse(source), rules, skip_functions=skip_functions)


def check_tree(
    tree: ast.AST,
    rules: Rules,
    *,
    skip_functions: Iterable[str] = (),
) -> list[Violation]:
    """Evaluate ``rules`` on a parsed module AST (see ``evaluate``)."""
    if rules.is_empty:
        return []
    # `skip_functions` (the task_* entry point) is still checked by forbid_*;
    # only require_functions ignores it (the cases already prove it works).
    exempt = {*rules.allow_in}
    skip = {*skip_functions}
    names = set(rules.forbid_names)
    methods = set(rules.forbid_methods)
    imports = set(rules.forbid_imports)
    nodes = set(rules.forbid_nodes)

    # trigger -> [rule kind, reason, first line]. Nodes are visited in source
    # order, so the first hit of a trigger is its earliest occurrence.
    hits: dict[str, list[Any]] = {}

    def hit(trigger: str, rule: str, reason: str, line: int | None) -> None:
        if trigger not in hits:
            hits[trigger] = [rule, reason, line]

    def hit_import(name: str, line: int | None, *, statement: bool) -> None:
        if name in hits:
            if statement:  # prefer describing the import statement itself
                hits[name][1] = f"нельзя импортировать `{name}`"
            return
        action = "импортировать" if statement else "использовать"
        hits[name] = ["import", f"нельзя {action} `{name}`", line]

    # Visit nodes in source order. Module scope and every top-level function are
    # walked separately so parameters can shadow names/modules (`def f(math)`
    # does not use the module); `_walk_scope` descends into nested defs and
    # skips exempt ones. The module walker does not descend into functions.
    ordered: list[tuple[int, int, ast.AST, frozenset[str]]] = []
    for scope in _function_scopes(tree):
        if _exempt(scope, exempt):
            continue
        shadowed = frozenset(_param_names(scope))
        for node in _walk_scope(scope, exempt):
            pos = getattr(node, "lineno", 0), getattr(node, "col_offset", 0)
            ordered.append((pos[0], pos[1], node, shadowed))
    ordered.sort(key=lambda item: (item[0], item[1]))

    for _, _, node, shadowed in ordered:
        line = getattr(node, "lineno", None)
        if isinstance(node, ast.Name):
            if node.id in names:
                hit(node.id, "name", f"нельзя использовать `{node.id}`", line)
        elif isinstance(node, ast.Attribute):
            if node.attr in methods and isinstance(node.ctx, ast.Load):
                hit(node.attr, "method", f"нельзя вызывать `.{node.attr}()`", line)
        elif isinstance(node, ast.Call):
            base = _qualified_root(node.func)
            if base in imports and base not in shadowed:
                hit_import(base, line, statement=False)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for module in _import_modules(node):
                name = _forbidden_module(module, imports)
                if name is not None and name not in shadowed:
                    hit_import(name, line, statement=True)
        elif type(node).__name__ in nodes:
            cls = type(node).__name__
            hit(cls, "node", f"нельзя использовать `{_NODE_HINTS.get(cls, cls)}`", line)

    for name in rules.require_functions:
        if name not in skip and name not in exempt and not _has_top_level_function(tree, name):
            hit(name, "function", f"нужна функция `{name}`", None)

    order = [
        *rules.forbid_names,
        *rules.forbid_methods,
        *rules.forbid_imports,
        *rules.forbid_nodes,
        *rules.require_functions,
    ]
    return [
        Violation(
            trigger=trigger,
            rule=str(hits[trigger][0]),
            text=str(hits[trigger][1]),
            line=hits[trigger][2],
        )
        for trigger in dict.fromkeys(order)
        if trigger in hits
    ]


def _iter_functions(node: ast.AST) -> Iterator[ast.FunctionDef | ast.AsyncFunctionDef]:
    for child in ast.walk(node):
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
            yield child


def _function_scopes(tree: ast.AST) -> Iterator[ast.AST]:
    """Module scope + top-level functions; the walker covers nested ones."""
    yield tree
    for stmt in getattr(tree, "body", []):
        if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
            yield stmt


def _exempt(scope: ast.AST, exempt: set[str]) -> bool:
    if isinstance(scope, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return scope.name.startswith(GIVEN_PREFIX) or scope.name in exempt
    return False


def _param_names(scope: ast.AST) -> set[str]:
    if not isinstance(scope, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return set()
    args = scope.args
    names = {arg.arg for arg in (*args.posonlyargs, *args.args, *args.kwonlyargs)}
    names.update(arg.arg for arg in (args.vararg, args.kwarg) if arg is not None)
    return names


def _walk_scope(scope: ast.AST, exempt: set[str] = frozenset()) -> Iterator[ast.AST]:
    """Nodes of one scope; nested ``def`` bodies are walked with their own scope.

    The ``def`` node itself is yielded (so ``forbid_nodes=["FunctionDef"]``
    works), then its decorators/defaults and body. Exempt functions (``given_*``
    / ``allow_in``) are not descended into; their nested functions are skipped.
    """
    stack: list[tuple[ast.AST, bool]] = [
        (node, False) for node in (scope.body if isinstance(scope, ast.Module) else [scope])
    ]
    while stack:
        node, is_exempt = stack.pop()
        if not is_exempt:
            yield node
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            nested_exempt = is_exempt or _exempt(node, exempt)
            stack.extend((child, nested_exempt) for child in node.decorator_list)
            stack.extend((child, nested_exempt) for child in node.args.defaults)
            stack.extend(
                (child, nested_exempt) for child in node.args.kw_defaults if child is not None
            )
            stack.extend((child, nested_exempt) for child in node.body)
            continue
        if not is_exempt:
            stack.extend((child, False) for child in ast.iter_child_nodes(node))


def _forbidden_module(module: str, imports: dict[str, str]) -> str | None:
    """Forbidden entry matching ``module`` (``os`` matches ``os.path``)."""
    for name in imports:
        if module == name or module.startswith(name + "."):
            return name
    return None


def _qualified_root(node: ast.AST) -> str | None:
    while isinstance(node, ast.Attribute):
        node = node.value
    return node.id if isinstance(node, ast.Name) else None


def _import_modules(node: ast.Import | ast.ImportFrom) -> Iterator[str]:
    """Imported module names: ``math`` for ``import math`` and ``from math import x``.

    ``import os.path`` also yields ``os.path``; a forbidden ``"os"`` matches
    any dotted form of it (``module == name or module.startswith(name + ".")``).
    """
    if isinstance(node, ast.Import):
        for alias in node.names:
            yield alias.name
            root = alias.name.split(".")[0]
            if root != alias.name:
                yield root
        return
    if node.module:  # relative imports (level > 0, no module) are not compared
        yield node.module


def _has_top_level_function(tree: ast.AST, name: str) -> bool:
    body = getattr(tree, "body", None)
    if not isinstance(body, list):
        return False
    return any(
        isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)) and stmt.name == name
        for stmt in body
    )
