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

OOP rules (class bodies are about the structure, not the spelling):

- ``require_classes``        — top-level ``class`` with that name
- ``require_decorators``     — ``{"Account": ["dataclass"], "Account.balance":
  ["property"]}``: the class / method carries a matching decorator
  (``@dataclass``, ``@dataclasses.dataclass``, ``@dataclass(...)``,
  ``@x.setter`` → ``setter``, ``@abc.abstractmethod`` → ``abstractmethod``)
- ``require_methods``        — ``{"Account": ["deposit"]}``: methods defined in
  the class body (``require_methods_inherited`` also accepts inherited ones)
- ``require_bases`` / ``forbid_bases`` — direct base names (``abc.ABC`` →
  ``ABC``)
- ``forbid_attributes_outside_class`` — ``x._balance`` read/set outside the
  class body

Triggers of the OOP rules are the subject with its suffix:
``"_balance"`` for the attribute, ``"Account.deposit"`` for a method,
``"Circle -> Shape"`` for a base, the plain subject otherwise.

Functions and classes named ``given_*`` / ``Given*`` (GIVEN helpers and
dataclasses from starters) are exempt from the OOP rules; ``allow_in`` names
more functions the ``forbid_*`` rules ignore.

Each OOP violation states one thing. A class missing from the module is named
once — by ``require_classes`` if it is listed there, otherwise by the first
rule that needs it; a method that does not exist is named once (by
``require_methods``, or by ``require_decorators`` if only that mentions it).
"""

from __future__ import annotations

import ast
from collections.abc import Callable, Iterable, Iterator, Sequence
from dataclasses import dataclass, field
from typing import Any

GIVEN_PREFIX = "given_"
# Class counterpart of GIVEN_PREFIX: ``class GivenPoint:`` from a starter.
GIVEN_CLASS_PREFIX = "Given"
# Decorator spellings accepted in ``require_decorators`` -> what they mean.
_DECORATOR_ALIASES: dict[str, str] = {
    "setter": "setter",
    "getter": "getter",
    "deleter": "deleter",
    "abstractmethod": "abstractmethod",
    "abc.abstractmethod": "abstractmethod",
    "abstractproperty": "abstractproperty",
    "abc.abstractproperty": "abstractproperty",
    "classmethod": "classmethod",
    "staticmethod": "staticmethod",
    "property": "property",
    "functools.cached_property": "cached_property",
    "cached_property": "cached_property",
    "functools.total_ordering": "total_ordering",
    "total_ordering": "total_ordering",
    "dataclass": "dataclass",
    "dataclasses.dataclass": "dataclass",
    "enum.unique": "unique",
    "unique": "unique",
}

# Line suffix of the OOP rule reasons: «… (строка 12)».
LINE_SUFFIX = "(строка "

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
    # OOP rules (see the module docstring).
    require_classes: tuple[str, ...] = ()
    require_decorators: dict[str, tuple[str, ...]] = field(default_factory=dict)
    require_methods: dict[str, tuple[str, ...]] = field(default_factory=dict)
    require_methods_inherited: dict[str, tuple[str, ...]] = field(default_factory=dict)
    require_bases: dict[str, tuple[str, ...]] = field(default_factory=dict)
    forbid_bases: dict[str, tuple[str, ...]] = field(default_factory=dict)
    forbid_attributes_outside_class: tuple[str, ...] = ()
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
            or self.require_classes
            or self.require_decorators
            or self.require_methods
            or self.require_methods_inherited
            or self.require_bases
            or self.forbid_bases
            or self.forbid_attributes_outside_class
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
    message_key: str | None = None  # declared message key when it differs

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
    # The line of an OOP member sits where it belongs: «метод … (строка 12)».
    if violation.line is None or LINE_SUFFIX in reason:
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
    require_classes: Iterable[str] = (),
    require_decorators: dict[str, Iterable[str]] | None = None,
    require_methods: dict[str, Iterable[str]] | None = None,
    require_methods_inherited: dict[str, Iterable[str]] | None = None,
    require_bases: dict[str, Iterable[str]] | None = None,
    forbid_bases: dict[str, Iterable[str]] | None = None,
    forbid_attributes_outside_class: Iterable[str] = (),
    messages: dict[str, str] | None = None,
) -> Rules:
    """Validate ``@rules`` arguments and normalise them into ``Rules``.

    Raises ``ValueError`` for an unknown ast node name, a bare string instead
    of a list, a malformed name, an unknown decorator, a malformed ``"Class"``
    / ``"Class.method"`` key, or a message key that matches no rule.
    """
    names = _name_list("forbid_names", forbid_names)
    methods = _name_list("forbid_methods", forbid_methods)
    required = _name_list("require_functions", require_functions)
    allowed = _name_list("allow_in", allow_in)
    imports = _name_list("forbid_imports", forbid_imports, dotted=True)
    nodes = _node_list(forbid_nodes)
    classes = _name_list("require_classes", require_classes)
    decorators = _map_list("require_decorators", require_decorators, member="decorator")
    required_methods = _map_list("require_methods", require_methods, member="method")
    inherited = _map_list("require_methods_inherited", require_methods_inherited, member="method")
    bases = _map_list("require_bases", require_bases, member="class")
    forbidden_bases = _map_list("forbid_bases", forbid_bases, member="class")
    attributes = _name_list("forbid_attributes_outside_class", forbid_attributes_outside_class)
    oop_keys: set[str] = set(classes) | set(required) | set(attributes)
    for mapping in (required_methods, inherited):
        oop_keys.update(f"{cls}.{member}" for cls in mapping for member in mapping[cls])
    oop_keys.update(decorators)
    oop_keys.update(f"{cls}.{member}" for cls in decorators for member in decorators[cls])
    for base_map in (bases, forbidden_bases):
        oop_keys.update(f"{cls} -> {base}" for cls in base_map for base in base_map[cls])
    msgs = _messages(
        messages,
        names=names,
        methods=methods,
        imports=imports,
        nodes=nodes,
        extra=oop_keys,
    )
    return Rules(
        forbid_names=names,
        forbid_methods=methods,
        forbid_imports=imports,
        forbid_nodes=nodes,
        require_functions=required,
        allow_in=allowed,
        require_classes=classes,
        require_decorators=decorators,
        require_methods=required_methods,
        require_methods_inherited=inherited,
        require_bases=bases,
        forbid_bases=forbidden_bases,
        forbid_attributes_outside_class=attributes,
        messages=msgs,
    )


def _map_list(
    argname: str, value: dict[str, Iterable[str]] | None, *, member: str
) -> dict[str, tuple[str, ...]]:
    """Validate ``{"Class": [names]}`` / ``{"Class.method": [names]}`` arguments."""
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"@rules {argname} must be a dict {{'Class': [names]}}")
    out: dict[str, tuple[str, ...]] = {}
    for raw_key, members in value.items():
        if not isinstance(raw_key, str) or not raw_key.strip():
            raise ValueError(f"@rules {argname}: class name must be a string, got {raw_key!r}")
        key = raw_key.strip()
        # Class name, optionally qualified by one ".member" (e.g. "Account.balance").
        if key.count(".") > 1 or not all(part.isidentifier() for part in key.split(".")):
            raise ValueError(
                f"@rules {argname}: {key!r} must be 'ClassName' or 'ClassName.member'"
            )
        if isinstance(members, (str, bytes)):
            raise ValueError(
                f"@rules {argname}[{key!r}] must be a list of names, not a string"
            )
        checked: list[str] = []
        for raw in members:
            if not isinstance(raw, str) or not raw.strip():
                raise ValueError(
                    f"@rules {argname}[{key!r}]: entries must be non-empty strings, got {raw!r}"
                )
            item = raw.strip()
            if argname == "require_decorators":
                if item not in _DECORATOR_ALIASES:
                    raise ValueError(
                        f"@rules require_decorators[{key!r}]: unknown decorator {item!r} "
                        f"(known: {sorted(_DECORATOR_ALIASES)})"
                    )
                item = _DECORATOR_ALIASES[item]
            elif argname in ("require_methods", "require_methods_inherited"):
                if not item.isidentifier():
                    raise ValueError(
                        f"@rules {argname}[{key!r}]: {item!r} is not a valid method name"
                    )
            elif not item.isidentifier():
                raise ValueError(f"@rules {argname}[{key!r}]: {item!r} is not a valid class name")
            if item not in checked:
                checked.append(item)
        if not checked:
            raise ValueError(
                f"@rules {argname}[{key!r}]: at least one {member} name is required"
            )
        merged = (*out.get(key, ()), *(item for item in checked if item not in out.get(key, ())))
        out[key] = merged
    return out


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
    extra: Iterable[str] = (),
) -> dict[str, str]:
    if messages is None:
        return {}
    if not isinstance(messages, dict):
        raise ValueError("@rules messages must be a dict {rule key: text}")
    known = {*names, *methods, *imports, *nodes, *extra}
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
    exempt_classes = {cls for cls in _class_index(tree) if cls.startswith(GIVEN_CLASS_PREFIX)}
    skip = {*skip_functions}
    names = set(rules.forbid_names)
    methods = set(rules.forbid_methods)
    imports = set(rules.forbid_imports)
    nodes = set(rules.forbid_nodes)

    # trigger -> [rule kind, reason, first line, message key]. Nodes are visited
    # in source order, so the first hit of a trigger is its earliest occurrence.
    hits: dict[str, list[Any]] = {}

    def hit(
        trigger: str, rule: str, reason: str, line: int | None, key: str | None = None
    ) -> None:
        if trigger not in hits:
            hits[trigger] = [rule, reason, line, key]

    def hit_import(name: str, line: int | None, *, statement: bool) -> None:
        if name in hits:
            if statement:  # prefer describing the import statement itself
                hits[name][1] = f"нельзя импортировать `{name}`"
            return
        action = "импортировать" if statement else "использовать"
        hits[name] = ["import", f"нельзя {action} `{name}`", line, None]

    # Visit nodes in source order. Module scope and every top-level function are
    # walked separately so parameters can shadow names/modules (`def f(math)`
    # does not use the module); `_walk_scope` descends into nested defs and
    # skips exempt ones. The module walker does not descend into functions.
    ordered: list[tuple[int, int, ast.AST, frozenset[str]]] = []
    for scope in _function_scopes(tree):
        if _exempt(scope, exempt):
            continue
        if isinstance(scope, ast.ClassDef) and scope.name in exempt_classes:
            continue
        shadowed = frozenset(_param_names(scope))
        for node in _walk_scope(scope, exempt, exempt_classes):
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
        *_check_classes(tree, rules, exempt_classes, hit),
    ]
    return [
        Violation(
            trigger=trigger,
            rule=str(hits[trigger][0]),
            text=str(hits[trigger][1]),
            line=hits[trigger][2],
            message_key=hits[trigger][3],
        )
        for trigger in dict.fromkeys(order)
        if trigger in hits
    ]


def _check_classes(
    tree: ast.AST,
    rules: Rules,
    exempt_classes: set[str],
    hit: Callable[[str, str, str, int | None, str | None], None],
) -> list[str]:
    """OOP rules (``require_classes`` … ``forbid_attributes_outside_class``).

    Records violations through ``hit`` and returns their triggers in
    declaration order. A missing method / base has no line; everything that is
    found in the code reports the line of the method, the base or the access.
    """
    classes = _class_index(tree)
    order: list[str] = []

    for name in rules.require_classes:
        if not _is_given_class(name) and name not in classes:
            hit(name, "class", f"нужен класс `{name}`", None)
            order.append(name)

    for subject, members in rules.require_decorators.items():
        cls_name, _, method_name = subject.partition(".")
        if _is_given_class(cls_name):
            continue
        cls = classes.get(cls_name)
        if cls is None:
            if subject not in rules.require_classes:  # otherwise already reported
                hit(subject, "decorator", _missing_class_text(subject, members[0]), None, subject)
                order.append(subject)
            continue
        if not method_name:
            missing = _missing_decorators(cls.decorator_list, members)
            if missing:
                hit(
                    subject,
                    "decorator",
                    f"`{cls_name}` должен быть помечен @{members[0]}",
                    cls.lineno,
                    subject,
                )
                order.append(subject)
            continue
        methods = _own_methods(cls)
        if method_name not in methods:
            # Absent: require_methods* already names it if both rules ask for
            # it, so avoid a second message. Inherited: that is inheritance's
            # business (require_methods_inherited), not a decorator issue.
            required = method_name in rules.require_methods.get(
                cls_name, ()
            ) or method_name in rules.require_methods_inherited.get(cls_name, ())
            if not required:
                text = _missing_class_text(subject, members[0])
                hit(subject, "decorator", text, None, subject)
                order.append(subject)
            continue
        missing = _missing_decorators(_all_decorators(cls, method_name), members)
        if missing:
            hit(
                subject,
                "decorator",
                f"метод `{method_name}` в классе `{cls_name}` должен быть помечен "
                f"@{members[0]} (строка {methods[method_name].lineno})",
                methods[method_name].lineno,
                subject,
            )
            order.append(subject)

    required = {**rules.require_methods, **rules.require_methods_inherited}
    for cls_name, members in required.items():
        if _is_given_class(cls_name):
            continue
        cls = classes.get(cls_name)
        if cls is None:
            if cls_name not in rules.require_classes:  # otherwise already reported
                trigger = f"{cls_name}.{members[0]}"
                hit(trigger, "method", _missing_method_text(cls_name, members[0]), None, trigger)
                order.append(trigger)
            continue
        pool = _own_methods(cls)
        if cls_name in rules.require_methods_inherited:  # per class opt-in
            pool = {**pool, **_inherited_methods(cls, classes)}
        for method_name in members:
            trigger = f"{cls_name}.{method_name}"
            if method_name in pool:
                continue
            # The message key of "Account.deposit" is the trigger itself.
            hit(trigger, "method", _missing_method_text(cls_name, method_name), None, trigger)
            order.append(trigger)

    for subject, base_list in rules.require_bases.items():
        if _is_given_class(subject):
            continue
        cls = classes.get(subject)
        if cls is None:
            if subject not in rules.require_classes:  # otherwise already reported
                trigger = f"{subject} -> {base_list[0]}"
                text = f"нужен класс `{subject}`, наследующий от `{base_list[0]}`"
                hit(trigger, "base", text, None, trigger)
                order.append(trigger)
            continue
        bases = _direct_bases(cls)
        for base in base_list:
            trigger = f"{subject} -> {base}"
            if _find_base(bases, base) is not None:
                continue
            near = f" (сейчас: от `{bases[0][0]}`)" if bases else ""
            hit(trigger, "base", f"`{subject}` наследуется от `{base}`{near}", cls.lineno, trigger)
            order.append(trigger)

    for subject, base_list in rules.forbid_bases.items():
        if _is_given_class(subject):
            continue
        cls = classes.get(subject)
        if cls is None:
            continue
        bases = _direct_bases(cls)
        for base in base_list:
            trigger = f"{subject} -> {base}"
            match = _find_base(bases, base)
            if match is None:
                continue
            hit(
                trigger,
                "base_forbidden",
                f"`{subject}` не должен наследоваться от `{match[0]}`",
                match[1],
                trigger,
            )
            order.append(trigger)

    if rules.forbid_attributes_outside_class:
        for name in rules.forbid_attributes_outside_class:
            line = _first_outside_access(tree, name, exempt_classes)
            if line is None:
                continue
            hit(
                name,
                "attribute",
                f"к `{_escape_attr(name)}` нельзя обращаться снаружи класса (строка {line})",
                line,
                name,
            )
            order.append(name)

    return order


def _iter_functions(node: ast.AST) -> Iterator[ast.FunctionDef | ast.AsyncFunctionDef]:
    for child in ast.walk(node):
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
            yield child


def _function_scopes(tree: ast.AST) -> Iterator[ast.AST]:
    """Module scope + top-level functions and classes.

    The walker covers their bodies, including nested functions.
    """
    yield tree
    for stmt in getattr(tree, "body", []):
        if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
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


def _walk_scope(
    scope: ast.AST,
    exempt: set[str] = frozenset(),
    exempt_classes: frozenset[str] | set[str] = frozenset(),
) -> Iterator[ast.AST]:
    """Nodes of one scope; nested ``def`` bodies are walked with their own scope.

    The ``def`` node itself is yielded (so ``forbid_nodes=["FunctionDef"]``
    works), then its decorators/defaults and body. Exempt functions (``given_*``
    / ``allow_in``) are not descended into; their nested functions are skipped.
    The body of an exempt class (``Given*``) is skipped the same way, while its
    def and decorators are still visited like any other class.
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
        if isinstance(node, ast.ClassDef):
            nested_exempt = is_exempt or node.name in exempt_classes
            stack.extend((child, nested_exempt) for child in node.decorator_list)
            stack.extend((child, nested_exempt) for child in node.bases)
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


# === OOP helpers ===


def _missing_method_text(cls_name: str, method_name: str) -> str:
    return f"нужен метод `{method_name}` в классе `{cls_name}`"


def _missing_class_text(subject: str, decorator: str) -> str:
    cls_name, _, method_name = subject.partition(".")
    if not method_name:
        return f"нужен класс `{cls_name}` с @{decorator}"
    return f"нужен класс `{cls_name}` с методом `{method_name}`, помеченным @{decorator}"


def _is_given_class(name: str | None) -> bool:
    return name is not None and name.startswith(GIVEN_CLASS_PREFIX)


def _given_scope(name: str | None) -> bool:
    """``given_*`` function or a ``Given*`` class from the starter."""
    if name is None:
        return False
    return name.startswith(GIVEN_PREFIX) or name.startswith(GIVEN_CLASS_PREFIX)


def _escape_attr(name: str) -> str:
    """Attribute name in backticks; underscores are escaped outside code spans."""
    return name.replace("_", "\\_")


def _class_index(tree: ast.AST) -> dict[str, ast.ClassDef]:
    """Top-level classes by name; nested (inner) classes are ignored."""
    out: dict[str, ast.ClassDef] = {}
    for stmt in getattr(tree, "body", []):
        if isinstance(stmt, ast.ClassDef) and stmt.name not in out:
            out[stmt.name] = stmt
    return out


def _own_methods(cls: ast.ClassDef) -> dict[str, ast.FunctionDef | ast.AsyncFunctionDef]:
    """Methods / ``property`` accessors defined in the class body (not nested ones)."""
    out: dict[str, ast.FunctionDef | ast.AsyncFunctionDef] = {}
    for stmt in cls.body:
        if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out.setdefault(stmt.name, stmt)
            continue
        # ``def __init__`` lives inside ``if TYPE_CHECKING:`` etc. — rare, but
        # a method behind a single ``if`` block still belongs to the body.
        if isinstance(stmt, ast.If):
            for inner in stmt.body:
                if isinstance(inner, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    out.setdefault(inner.name, inner)
    return out


def _all_decorators(cls: ast.ClassDef, name: str) -> list[ast.expr]:
    """Decorators of every ``def name`` in the class body.

    A property is several defs with one name: ``@property`` on the getter,
    ``@name.setter`` on the setter — ``require_decorators`` sees them all.
    """
    out: list[ast.expr] = []
    for stmt in cls.body:
        defs = stmt.body if isinstance(stmt, ast.If) else [stmt]
        for node in defs:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
                out.extend(node.decorator_list)
    return out


def _inherited_methods(
    cls: ast.ClassDef, classes: dict[str, ast.ClassDef]
) -> dict[str, ast.FunctionDef | ast.AsyncFunctionDef]:
    """Methods reachable through top-level base classes (own hierarchy only)."""
    out: dict[str, ast.FunctionDef | ast.AsyncFunctionDef] = {}
    seen: set[str] = set()
    pending = [base.id for base in cls.bases if isinstance(base, ast.Name)]
    while pending:
        name = pending.pop(0)
        if name in seen or name not in classes:
            continue
        seen.add(name)
        parent = classes[name]
        for method_name, node in _own_methods(parent).items():
            out.setdefault(method_name, node)
        pending.extend(base.id for base in parent.bases if isinstance(base, ast.Name))
    return out


def _decorator_name(node: ast.AST) -> str:
    """Bare name of a decorator: ``@dataclass(frozen=True)`` → ``dataclass``."""
    target = node.func if isinstance(node, ast.Call) else node
    if isinstance(target, ast.Attribute):
        return target.attr
    return target.id if isinstance(target, ast.Name) else ""


def _decorator_names(decorators: Sequence[ast.expr]) -> set[str]:
    """Canonical decorator kinds: ``@x.setter`` → ``setter``; calls unwrapped."""
    out: set[str] = set()
    for node in decorators:
        if isinstance(node, ast.Attribute):
            # @dataclasses.dataclass and the property accessors @x.setter,
            # @x.getter, @x.deleter all count by their last part.
            out.add(node.attr)
            continue
        if isinstance(node, ast.Call):
            name = _decorator_name(node.args[0] if node.args else node.func)
            if name:  # @property(getter) / @staticmethod(fn)
                out.add(name)
        name = _decorator_name(node)
        if name:
            out.add(name)
    return out


def _missing_decorators(decorators: Sequence[ast.expr], wanted: Sequence[str]) -> list[str]:
    present = _decorator_names(decorators)
    return [name for name in wanted if name not in present]


def _base_name(node: ast.expr) -> str | None:
    """``abc.ABC`` → ``ABC``; subscriptions (``list[int]``) unwrapped."""
    if isinstance(node, ast.Subscript):
        node = node.value
    if isinstance(node, ast.Attribute):
        return node.attr
    return node.id if isinstance(node, ast.Name) else None


def _direct_bases(cls: ast.ClassDef) -> list[tuple[str, int, str]]:
    """Direct base names: ``(last part, line, full dotted source name)``.

    ``class C(abc.ABC)`` → ``("ABC", line, "abc.ABC")``; rules match by the
    last part, so ``ABC`` and ``abc.ABC`` are the same base.
    """
    out: list[tuple[str, int, str]] = []
    for base in cls.bases:
        name = _base_name(base)
        if name is not None:
            out.append((name, getattr(base, "lineno", cls.lineno), ast.unparse(base)))
    return out


def _base_matches(candidate: tuple[str, int, str], wanted: str) -> bool:
    """``"ABC"`` matches ``abc.ABC``; ``"collections.OrderedDict"`` matches itself."""
    last, _, dotted = candidate
    if dotted == wanted or last == wanted:
        return True
    return wanted.startswith(dotted + ".") or dotted.startswith(wanted + ".")


def _find_base(bases: list[tuple[str, int, str]], wanted: str) -> tuple[str, int] | None:
    """The base matching ``wanted`` as ``(last part, line)``; nearest name wins."""
    for name, line, dotted in bases:
        if dotted == wanted or name == wanted:
            return name, line
    for name, line, _ in bases:  # allow a module prefix in either direction
        if dotted.startswith(wanted + ".") or wanted.startswith(dotted + "."):
            return name, line
    return None


def _first_outside_access(tree: ast.AST, attr: str, exempt_classes: set[str]) -> int | None:
    """Line of the first ``x.<attr>`` read/write outside every class body.

    A single class scope (no class inside a class on purpose): the module,
    one top-level class, and the functions / methods an access actually lives
    in. Class-level code (``_balance = 3``, ``@dataclass``) is therefore never
    mistaken for an attribute access, and the class' own methods — nested
    ones included — may use the private attribute. ``Given*`` classes and
    ``given_*`` functions are exempt.
    """
    found: list[int] = []

    def statement(node: ast.AST, *, owner: str | None, cls: str | None, func: str | None) -> None:
        """``owner`` is the class a method belongs to; ``cls`` its body scope."""
        if node is None:  # none of the walked statement lists
            return
        if isinstance(node, ast.ClassDef):
            if node.name in exempt_classes:
                return
            for body_node in node.body:
                statement(body_node, owner=node.name, cls=node.name, func=None)
            return
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            func = node.name
        # The def itself yields only its decorators / defaults: no class.
        # A method is "inside" the class it was defined in (nested methods too).
        inside = (func is not None and (owner is not None or cls is not None))
        if not inside and not _is_given_class(cls) and not _is_given_class(owner):
            if not _given_scope(func):
                found.extend(_access_lines(node, attr))
        # Class-level code (``_balance = 3``, ``if True: def m``) may run
        # outside the class: follow it with ``cls`` cleared.
        for branch in _nested_statements(node):
            statement(branch, owner=owner, cls=cls, func=func)

    for node in getattr(tree, "body", []):
        statement(node, owner=None, cls=None, func=None)

    return min(found) if found else None


def _nested_statements(node: ast.AST) -> list[ast.AST]:
    """Statements / handlers / defs nested in ``node`` (any scope kind)."""
    out: list[ast.AST] = []
    # Every compound statement has ``body``; a few also have the others.
    nested_lists = [getattr(node, "body", None), getattr(node, "orelse", None)]
    nested_lists.append(getattr(node, "finalbody", None))
    for value in nested_lists:
        if isinstance(value, list):
            out.extend(item for item in value if isinstance(item, ast.AST))
    for handler in getattr(node, "handlers", None) or []:
        out.extend(handler.body)
    return out


def _access_lines(node: ast.AST, attr: str) -> list[int]:
    """Lines of ``Attribute`` loads/stores/deletes named ``attr`` in ``node``.

    Nested classes are not descended into (their bodies belong to them).
    """
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        # The def itself may carry accesses in decorators / defaults only.
        parts: list[ast.AST] = list(node.decorator_list)
        if isinstance(node, ast.ClassDef):
            parts.extend(node.bases)
        else:
            parts.extend(node.args.defaults)
            parts.extend(d for d in node.args.kw_defaults if d is not None)
        return [line for part in parts for line in _access_lines(part, attr)]

    lines: list[int] = []

    def visit(current: ast.AST) -> None:
        if isinstance(current, ast.ClassDef):
            return
        if (
            isinstance(current, ast.Attribute)
            and current.attr == attr
            and isinstance(current.ctx, (ast.Load, ast.Store, ast.Del))
        ):
            lines.append(current.lineno)
        for child in ast.iter_child_nodes(current):
            visit(child)

    visit(node)
    return lines
