"""Tests for the OOP keys of @rules — classes, decorators, methods, bases, attributes."""

from __future__ import annotations

import ast
import textwrap
from pathlib import Path

import pytest

from ego.checker import RULE_PREFIX, run_check
from ego.models import Task
from ego.static_rules import Rules, build_rules, check_tree, evaluate, format_violation
from ego.testing import rules

# === Helpers ===


def _src(source: str) -> str:
    """Dedent a test snippet (nested blocks may carry extra leading blanks).

    Works like ``textwrap.dedent`` except that the common indent ignores blank
    lines: an indented empty line after the opening quotes would otherwise
    confuse it. ``str.format`` placeholders must be filled in before dedenting
    (see the ``.replace`` pattern used by the parametrized tests).
    """
    lines = source.splitlines()
    cut = min((len(text) - len(text.lstrip()) for text in lines if text.strip()), default=0)
    return "\n".join(text[cut:] if text.strip() else "" for text in lines)


def _spec(**kwargs) -> Rules:
    return build_rules(**kwargs)


def _keys(source: str, **kwargs) -> list[str]:
    return [v.key for v in evaluate(_src(source), _spec(**kwargs))]


def _descriptions(source: str, **kwargs) -> list[str]:
    return [v.description for v in evaluate(_src(source), _spec(**kwargs))]


def _write_task(tmp_path: Path, tests_src: str, **task_kwargs) -> Task:
    tests_file = tmp_path / "task_x.tests.py"
    tests_file.write_text(textwrap.dedent(tests_src), encoding="utf-8")
    defaults = dict(
        id="OOPX",
        block="OOP",
        slug="block_oop",
        task_id="OOP1",
        title="OOP rules",
        level="easy",
        md_path=tmp_path / "task_x.md",
        statement_md="# OOP1",
        stub_py="def task_x():\n    pass\n",
        solution_py="def task_x():\n    return 1\n",
        tests_file=tests_file,
    )
    defaults.update(task_kwargs)
    return Task(**defaults)


# === require_classes ===


def test_require_class_present_and_missing():
    src = """
        class Account:
            pass
    """
    assert _keys(src, require_classes=["Account"]) == []
    assert _keys("def task_x():\n    return 1\n", require_classes=["Account"]) == [
        "class:Account"
    ]


def test_require_class_message():
    (violation,) = evaluate("def task_x():\n    return 1\n", _spec(require_classes=["Account"]))
    assert violation.description == "Правило: нужен класс `Account`"
    assert violation.trigger == "Account"
    assert violation.rule == "class"


def test_require_class_present_without_giving_up_other_gaps():
    """With a class in the module, every declared gap is reported separately."""
    src = """
        class Wallet:
            pass
    """
    keys = _keys(
        src,
        require_classes=["Account"],
        require_methods={"Wallet": ["add"]},
        require_bases={"Wallet": ["ABC"]},
    )
    assert keys == ["class:Account", "method:Wallet.add", "base:Wallet -> ABC"]


def test_require_class_ignores_nested_and_locally_defined_classes():
    src = """
        class Outer:
            class Account:
                pass

        def task_x():
            class Account:
                pass
            return Account
    """
    assert _keys(src, require_classes=["Account"]) == ["class:Account"]


def test_missing_class_is_reported_once():
    """One message per missing class, not one per rule that mentions it."""
    src = "def task_x():\n    return 1\n"
    keys = _keys(
        src,
        require_classes=["Account"],
        require_decorators={"Account": ["dataclass"]},
        require_methods={"Account": ["deposit"]},
        require_bases={"Account": ["ABC"]},
        forbid_bases={"Account": ["list"]},
    )
    assert keys == ["class:Account"]


def test_missing_class_without_require_classes():
    """Without require_classes the first rule needing the class reports it."""
    src = "def task_x():\n    return 1\n"
    assert _keys(src, require_decorators={"Account": ["dataclass"]}) == ["decorator:Account"]
    assert _descriptions(src, require_decorators={"Account": ["dataclass"]}) == [
        "Правило: нужен класс `Account` с @dataclass"
    ]
    assert _keys(src, require_methods={"Account": ["deposit"]}) == ["method:Account.deposit"]
    assert _keys(src, require_bases={"Account": ["ABC"]}) == ["base:Account -> ABC"]
    assert _descriptions(src, require_bases={"Account": ["ABC"]}) == [
        "Правило: нужен класс `Account`, наследующий от `ABC`"
    ]


def test_class_required_as_given_is_exempt():
    src = "def task_x():\n    return 1\n"
    assert _keys(src, require_classes=["GivenPoint"]) == []


# === require_decorators ===


@pytest.mark.parametrize(
    "decorator",
    [
        "@dataclass",
        "@dataclasses.dataclass",
        "@dataclass(frozen=True)",
        "@dataclasses.dataclass(frozen=True, eq=False)",
    ],
)
def test_class_decorator_variants(decorator):
    src = f"""
        import dataclasses

        {decorator}
        class Account:
            pass
    """.replace("{decorator}", decorator)
    assert _keys(src, require_decorators={"Account": ["dataclass"]}) == []


def test_class_decorator_missing_and_message():
    src = """
        class Account:
            pass
    """
    (violation,) = evaluate(
        _src(src), _spec(require_decorators={"Account": ["dataclass"]})
    )
    assert violation.key == "decorator:Account"
    assert violation.description == "Правило: `Account` должен быть помечен @dataclass (строка 2)"


def test_class_decorator_on_wrong_class():
    """A decorated Wallet does not stand in for the required Account."""
    src = """
        @dataclass
        class Wallet:
            pass
    """
    assert _keys(src, require_decorators={"Account": ["dataclass"]}) == ["decorator:Account"]
    assert _descriptions(src, require_decorators={"Account": ["dataclass"]}) == [
        "Правило: нужен класс `Account` с @dataclass"
    ]


@pytest.mark.parametrize(
    ("decorator", "wanted"),
    [
        ("@property", "property"),
        ("@classmethod", "classmethod"),
        ("@staticmethod", "staticmethod"),
        ("@x.setter", "setter"),
        ("@x.getter", "getter"),
        ("@x.deleter", "deleter"),
        ("@abc.abstractmethod", "abstractmethod"),
        ("@abstractmethod", "abstractmethod"),
        ("@functools.cached_property", "cached_property"),
        ("@cached_property", "cached_property"),
        ("@functools.total_ordering", "total_ordering"),
    ],
)
def test_method_decorator_variants(decorator, wanted):
    src = """
        import abc
        import functools

        class Account:
            {decorator}
            def balance(self):
                return 0
    """
    src = src.replace("@x.", "@balance.").replace("{decorator}", decorator)
    assert _keys(src, require_decorators={"Account.balance": [wanted]}) == []


def test_method_decorator_missing_message_with_method_line():
    src = """
        class Account:
            def from_dict(cls, data):
                return cls()
    """
    (violation,) = evaluate(
        _src(src), _spec(require_decorators={"Account.from_dict": ["classmethod"]})
    )
    assert violation.key == "decorator:Account.from_dict"
    assert violation.description == (
        "Правило: метод `from_dict` в классе `Account` должен быть помечен @classmethod (строка 3)"
    )


def test_class_decorator_does_not_satisfy_method_rule():
    src = """
        @dataclass
        class Account:
            @dataclass
            class Inner:
                pass

            def balance(self):
                return 0
    """
    assert _keys(
        src,
        require_decorators={"Account": ["dataclass"], "Account.balance": ["property"]},
    ) == ["decorator:Account.balance"]


def test_setter_needs_the_property_too():
    src = """
        class Account:
            @x.setter
            def balance(self, value):
                pass
    """
    src = src.replace("@x.", "@balance.")
    assert _keys(
        src,
        require_decorators={"Account.balance": ["property", "setter"]},
    ) == ["decorator:Account.balance"]


def test_property_with_setter_satisfies_both_decorators():
    src = """
        class Account:
            @property
            def balance(self):
                return self._balance

            @balance.setter
            def balance(self, value):
                self._balance = value
    """
    assert _keys(src, require_decorators={"Account.balance": ["property", "setter"]}) == []
    getter_only = src.split("            @balance.setter")[0]
    assert _keys(
        getter_only, require_decorators={"Account.balance": ["property", "setter"]}
    ) == ["decorator:Account.balance"]


def test_nested_class_decorator_ignored():
    src = """
        class Account:
            @dataclass
            class Settings:
                pass
    """
    # The @dataclass on the inner Settings does not decorate Account; once a
    # class exists in the module, a nested Settings does not satisfy the rule.
    assert _keys(src, require_decorators={"Account": ["dataclass"]}) == ["decorator:Account"]
    assert _keys(
        src, require_decorators={"Account": ["dataclass"], "Settings": ["dataclass"]}
    ) == ["decorator:Account", "decorator:Settings"]


def test_method_decorator_for_inherited_method_is_ignored():
    """Inheritance is require_methods_inherited's job, not require_decorators'."""
    src = """
        class Base:
            def helper(self):
                return 0

        class Child(Base):
            pass
    """
    # Inherited: the decorator rule leaves it to require_methods_inherited.
    assert _keys(
        src,
        require_classes=["Base", "Child"],
        require_methods_inherited={"Child": ["helper"]},
        require_decorators={"Child.helper": ["property"]},
    ) == []
    # Not required anywhere: the missing method is named directly.
    assert _descriptions(
        src, require_classes=["Base", "Child"], require_decorators={"Child.helper": ["property"]}
    ) == ["Правило: нужен класс `Child` с методом `helper`, помеченным @property"]


def test_given_class_decorator_exempt():
    src = """
        class GivenPoint:
            def x(self):
                return 0
    """
    assert _keys(
        src,
        require_decorators={"GivenPoint": ["dataclass"], "GivenPoint.x": ["property"]},
    ) == []


# === require_methods ===


def test_require_methods_present_and_missing():
    src = """
        class Account:
            def deposit(self, amount):
                pass

            def withdraw(self, amount):
                pass

            def __repr__(self):
                return "Account()"
    """
    wanted = {"Account": ["deposit", "withdraw", "__repr__"]}
    assert _keys(src, require_methods=wanted) == []
    assert _keys(
        "class Account:\n    def deposit(self):\n        pass\n", require_methods=wanted
    ) == ["method:Account.withdraw", "method:Account.__repr__"]


def test_require_method_message():
    src = """
        class Account:
            pass
    """
    (violation,) = evaluate(
        _src(src), _spec(require_methods={"Account": ["deposit"]})
    )
    assert violation.description == "Правило: нужен метод `deposit` в классе `Account`"
    assert violation.trigger == "Account.deposit"


def test_require_methods_do_not_count_inherited_ones():
    src = """
        class BaseAccount:
            def deposit(self):
                pass

        class Account(BaseAccount):
            pass
    """
    assert _keys(src, require_methods={"Account": ["deposit"]}) == ["method:Account.deposit"]


def test_require_methods_inherited_accepts_parent_methods():
    src = """
        class BaseAccount:
            def deposit(self):
                pass
            def owner(self):
                pass

        class Child(BaseAccount):
            def announce(self):
                pass
    """
    # For "Child" inherited methods count (require_methods_inherited);
    # the body definition of announce is required by require_methods.
    assert _keys(
        src,
        require_methods={"Child": ["announce"]},
        require_methods_inherited={"Child": ["deposit", "owner"]},
    ) == []
    assert _keys(
        src,
        require_methods={"Child": ["announce"]},
        require_methods_inherited={"Child": ["deposit", "owner", "announce"]},
    ) == []
    assert _keys(
        src,
        require_methods={"Child": ["deposit"]},
        require_methods_inherited={"Child": ["deposit"]},
    ) == []
    assert _keys(src, require_methods={"Child": ["deposit"]}) == ["method:Child.deposit"]


def test_require_methods_inherited_is_per_class():
    src = """
        class BaseAccount:
            def deposit(self):
                pass

        class Child(BaseAccount):
            pass

        class PlainAccount:
            pass
    """
    kwargs = {
        "require_methods": {"Child": ["deposit"]},
        "require_methods_inherited": {"Child": ["deposit"], "PlainAccount": ["deposit"]},
    }
    assert _keys(src, **kwargs) == ["method:PlainAccount.deposit"]


def test_require_methods_only_class_body_definitions():
    src = """
        class Account:
            if True:
                pass

        def task_x():
            def deposit():
                pass
            return deposit
    """
    assert _keys(src, require_methods={"Account": ["deposit"]}) == ["method:Account.deposit"]


def test_require_methods_staticmethod_and_property_count():
    src = """
        class Account:
            @staticmethod
            def from_dict(data):
                return data

            @property
            def balance(self):
                return 0
    """
    assert _keys(src, require_methods={"Account": ["from_dict", "balance"]}) == []


def test_nested_class_methods_ignored():
    src = """
        class Outer:
            class Account:
                def deposit(self):
                    pass
    """
    # The method lives in the inner class of Outer, not in a top-level Account.
    assert _keys(
        src, require_classes=["Outer"], require_methods={"Account": ["deposit"]}
    ) == ["method:Account.deposit"]


def test_nested_class_body_methods_do_not_satisfy_outer_class():
    src = """
        class Account:
            class Inner:
                def deposit(self):
                    pass
    """
    assert _keys(src, require_methods={"Account": ["deposit"]}) == ["method:Account.deposit"]


def test_given_class_methods_exempt():
    src = """
        class GivenRepo:
            pass
    """
    assert _keys(src, require_methods={"GivenRepo": ["save"]}) == []


# === require_bases / forbid_bases ===


@pytest.mark.parametrize("base", ["ABC", "abc.ABC"])
def test_require_bases_accepts_dotted_base(base):
    src = """
        import abc

        class Shape(BASE):
            pass

        class Circle(Shape):
            pass
    """.replace("BASE", base)
    assert _keys(src, require_bases={"Shape": ["ABC"], "Circle": ["Shape"]}) == []


def test_require_bases_missing_and_message():
    src = """
        class Circle(object):
            pass
    """
    (violation,) = evaluate(
        _src(src), _spec(require_bases={"Circle": ["Shape"]})
    )
    assert violation.key == "base:Circle -> Shape"
    assert violation.description == (
        "Правило: `Circle` наследуется от `Shape` (сейчас: от `object`) (строка 2)"
    )


def test_require_bases_of_missing_class_is_not_reported():
    """A missing class is require_classes' message, not a base message."""
    assert _keys("def task_x():\n    return 1\n", require_classes=["Circle"], require_bases={
        "Circle": ["Shape"]
    }) == ["class:Circle"]


def test_require_bases_direct_only():
    """A grandparent base does not satisfy a direct-base rule."""
    src = """
        class Shape:
            pass

        class Named(Shape):
            pass

        class Circle(Named):
            pass
    """
    assert _keys(src, require_bases={"Circle": ["Shape"]}) == ["base:Circle -> Shape"]


def test_require_bases_plain_base_class():
    src = """
        class Registry(UserDict):
            pass
    """
    assert _keys(src, require_bases={"Registry": ["UserDict"]}) == []


@pytest.mark.parametrize("base", ["list", "dict", "collections.OrderedDict"])
def test_forbid_bases_detects_wrong_base(base):
    src = """
        import collections

        class Inventory(BASE):
            pass
    """.replace("BASE", base)
    expected = base.split(".")[-1]
    assert _keys(src, forbid_bases={"Inventory": ["list", "dict", "OrderedDict"]}) == [
        f"base_forbidden:Inventory -> {expected}"
    ]


def test_forbid_bases_message():
    src = """
        class Inventory(list):
            pass
    """
    (violation,) = evaluate(
        _src(src), _spec(forbid_bases={"Inventory": ["list", "dict"]})
    )
    assert violation.description == (
        "Правило: `Inventory` не должен наследоваться от `list` (строка 2)"
    )


def test_forbid_bases_accepts_composition():
    src = """
        class Inventory:
            def __init__(self):
                self.items = []
    """
    assert _keys(src, forbid_bases={"Inventory": ["list", "dict"]}) == []


def test_require_and_forbid_bases_together():
    src = """
        class Inventory(list, Sized):
            pass
    """
    keys = _keys(
        src,
        require_bases={"Inventory": ["Sized"]},
        forbid_bases={"Inventory": ["list"]},
    )
    assert keys == ["base_forbidden:Inventory -> list"]


# === forbid_attributes_outside_class ===


def test_outside_access_is_flagged_with_line():
    src = """
        class Account:
            def __init__(self):
                self._balance = 0

            def add(self, amount):
                self._balance += amount

        def task_x(account):
            return account._balance
    """
    (violation,) = evaluate(
        _src(src), _spec(forbid_attributes_outside_class=["_balance"])
    )
    assert violation.key == "attribute:_balance"
    assert violation.description == (
        "Правило: к `\\_balance` нельзя обращаться снаружи класса (строка 10)"
    )


def test_first_outside_access_only():
    src = """
        def a(x):
            return x._balance

        def b(x):
            return x._balance
    """
    found = evaluate(_src(src), _spec(forbid_attributes_outside_class=["_balance"]))
    assert len(found) == 1, (found, _src(src))
    assert found[0].line == 3


def test_inside_access_allowed_including_nested_functions():
    src = """
        class Account:
            def __init__(self):
                self._balance = 0

            def __repr__(self):
                def show():
                    return self._balance
                return str(show())
    """
    assert _keys(src, forbid_attributes_outside_class=["_balance"]) == []


def test_setter_and_storage_inside_class_allowed():
    src = """
        class Account:
            _balance = 0

            @balance.setter
            def balance(self, value):
                self._balance = value

            def inc(self):
                Account._balance += 1
    """
    assert _keys(src, forbid_attributes_outside_class=["_balance"]) == []


def test_attribute_only_flagged_when_listed():
    src = """
        def task_x(account):
            return account._balance
    """
    assert _keys(src, forbid_attributes_outside_class=["_secret"]) == []
    assert _keys(src, forbid_attributes_outside_class=["_balance"]) == ["attribute:_balance"]


def test_given_classes_and_functions_exempt():
    src = """
        class GivenWallet:
            def show(self):
                return self._balance

        def given_read(w):
            return w._balance

        class Account:
            def __init__(self):
                self._balance = 0
    """
    assert _keys(src, forbid_attributes_outside_class=["_balance"]) == []


def test_given_class_body_does_not_hide_other_rules():
    """A Given* class is exempt; the rest of the module is still checked."""
    src = """
        class GivenPoint:
            def show(self):
                return self._balance

        def task_x(p):
            return p._balance
    """
    (violation,) = evaluate(
        _src(src), _spec(forbid_attributes_outside_class=["_balance"])
    )
    assert "строка 7" in violation.description


# === combined / declaration order / nested classes ===


def test_violations_in_declaration_order():
    src = """
        class Account:
            pass

        class Circle:
            pass
    """
    keys = _keys(
        src,
        require_methods={"Account": ["deposit"]},
        require_bases={"Circle": ["Shape"], "Account": ["ABC"]},
        require_decorators={"Account": ["dataclass"]},
    )
    assert keys == [
        "decorator:Account",
        "method:Account.deposit",
        "base:Circle -> Shape",
        "base:Account -> ABC",
    ]


def test_valid_oop_module_has_no_violations():
    src = """
        import abc
        from dataclasses import dataclass

        class Shape(abc.ABC):
            @abc.abstractmethod
            def area(self):
                pass

        @dataclass(frozen=True)
        class Account:
            _balance: float = 0.0

            @property
            def balance(self):
                return self._balance

            @classmethod
            def from_dict(cls, data):
                return cls()

            def deposit(self, amount):
                self._balance += amount

            def withdraw(self, amount):
                self._balance -= amount

            def __repr__(self):
                return f"Account({self._balance})"

        class Circle(Shape):
            def area(self):
                return 0

        class Inventory:
            def __init__(self):
                self.items = []

        def task_x(account):
            return account.balance
    """
    spec = _spec(
        require_classes=["Account", "Shape", "Circle", "Inventory"],
        require_decorators={
            "Account": ["dataclass"],
            "Account.balance": ["property"],
            "Account.from_dict": ["classmethod"],
            "Shape.area": ["abstractmethod"],
        },
        require_methods={
            "Account": ["deposit", "withdraw", "__repr__"],
            "Shape": ["area"],
        },
        require_bases={"Shape": ["ABC"], "Circle": ["Shape"]},
        forbid_bases={"Inventory": ["list", "dict"]},
        forbid_attributes_outside_class=["_balance"],
    )
    assert evaluate(_src(src), spec) == []


def test_nested_classes_ignored_by_structural_rules():
    src = """
        class Outer:
            class Account:
                @property
                def balance(self):
                    pass
    """
    spec = _spec(
        require_classes=["Account"],
        require_methods={"Account": ["deposit"]},
        require_bases={"Account": ["ABC"]},
    )
    # The inner class does not count as a top-level Account: one clear message.
    assert [v.key for v in evaluate(_src(src), spec)] == ["class:Account"]


def test_existing_rules_still_work_inside_classes():
    src = """
        class Account:
            def show(self):
                return sorted([3, 1])
    """
    assert _keys(src, forbid_names=["sorted"], require_classes=["Account"]) == ["name:sorted"]


# === decorator: validation ===


def test_decorator_rejects_string_instead_of_class_list():
    with pytest.raises(ValueError):
        rules(require_classes="Account")


@pytest.mark.parametrize("argname", ["require_methods", "require_bases", "forbid_bases"])
def test_map_arguments_must_be_dict(argname):
    with pytest.raises(ValueError, match="must be a dict"):
        rules(**{argname: ["Account"]})


def test_map_arguments_reject_string_values():
    with pytest.raises(ValueError, match="not a string"):
        rules(require_methods={"Account": "deposit"})


def test_map_arguments_reject_empty_value():
    with pytest.raises(ValueError, match="at least one"):
        rules(require_bases={"Shape": []})


def test_require_decorators_unknown_name():
    with pytest.raises(ValueError, match="unknown decorator"):
        rules(require_decorators={"Account": ["datclass"]})


def test_require_decorators_normalises_aliases():
    spec = _spec(require_decorators={"Shape": ["abc.abstractmethod"]})
    assert spec.require_decorators == {"Shape": ("abstractmethod",)}
    assert _keys("import abc\n\nclass Shape:\n    pass\n", require_decorators={
        "Shape": ["abc.abstractmethod"]
    }) == ["decorator:Shape"]


def test_map_arguments_reject_qualified_subject():
    with pytest.raises(ValueError, match="ClassName"):
        rules(require_decorators={"Account.balance.x": ["property"]})


def test_map_arguments_reject_invalid_names():
    with pytest.raises(ValueError):
        rules(require_methods={"Account": ["1deposit"]})
    with pytest.raises(ValueError):
        rules(require_methods={"Account": ["with drawer"]})


def test_method_message_key_accepted():
    spec = _spec(
        require_methods={"Account": ["deposit", "withdraw"]},
        messages={"Account.deposit": "Метод deposit обязателен"},
    )
    assert _keys("class Account:\n    pass\n", **{
        "require_methods": {"Account": ["deposit", "withdraw"]},
        "messages": {"Account.deposit": "Метод deposit обязателен"},
    }) == ["method:Account.deposit", "method:Account.withdraw"]
    (violation,) = [
        v for v in evaluate("class Account:\n    pass\n", spec) if v.trigger == "Account.deposit"
    ]
    assert format_violation(violation, spec.message_for(violation)) == (
        "Правило: Метод deposit обязателен"
    )
    assert _keys("def task_x():\n    return 1\n", **{
        "require_methods": {"Account": ["deposit"]},
        "messages": {"Account.deposit": "Метод deposit обязателен"},
    }) == ["method:Account.deposit"]


def test_base_message_key_accepted():
    spec = _spec(
        forbid_bases={"Inventory": ["list"]},
        messages={"Inventory -> list": "Без наследования от list"},
    )
    (violation,) = evaluate("class Inventory(list):\n    pass\n", spec)
    assert violation.message_key == "Inventory -> list"
    assert spec.message_for(violation) == "Без наследования от list"


def test_oop_rules_do_not_change_empty_check():
    assert _spec().is_empty
    assert not _spec(require_classes=["Account"]).is_empty


def test_check_tree_handles_nested_classes():
    """The parsed-AST entry point sees the same top-level-only classes."""
    spec = _spec(require_classes=["Account"], forbid_attributes_outside_class=["_x"])
    tree = ast.parse("class Outer:\n    class Account:\n        pass\n")
    assert [v.key for v in check_tree(tree, spec)] == ["class:Account"]


# === end-to-end through run_check ===


OOP_TESTS = """
    from ego.testing import case, rules

    @rules(
        require_classes=["Account"],
        require_decorators={"Account": ["dataclass"], "Account.balance": ["property"]},
        require_methods={"Account": ["deposit", "__repr__"]},
        forbid_attributes_outside_class=["_balance"],
    )
    @case(args=(50,), expected=150, description="deposit 50", level="smoke")
    def task_x(amount):
        ...
"""

OOP_SOLUTION = """
    from dataclasses import dataclass

    @dataclass
    class Account:
        _balance: int = 100

        @property
        def balance(self):
            return self._balance

        def deposit(self, amount):
            self._balance += amount

        def __repr__(self):
            return f"Account({self._balance})"

    def task_x(amount):
        account = Account()
        account.deposit(amount)
        return account.balance
"""


def test_run_check_reference_passes(tmp_path):
    task = _write_task(tmp_path, OOP_TESTS, solution_py=textwrap.dedent(OOP_SOLUTION))
    result = run_check(task, task.solution_py, level="all")
    assert result.status == "passed", [tr.description for tr in result.results]
    assert result.total_tests == 1


def test_run_check_reference_violating_its_own_rules_fails(tmp_path):
    """The catalog verifier gate: a reference that breaks the OOP rules fails."""
    broken = textwrap.dedent(
        """
        @dataclass
        class Account:
            _balance: int = 100

            def deposit(self, amount):
                self._balance += amount

            def __repr__(self):
                return "Account()"

        def task_x(amount):
            return Account()._balance + 0 * amount
        """
    )
    task = _write_task(tmp_path, OOP_TESTS, solution_py=broken)
    result = run_check(task, broken, level="all")
    assert result.status != "passed"
    assert result.results[0].description.startswith(RULE_PREFIX)


def test_run_check_surfaces_each_oop_violation(tmp_path):
    """One student mistake → one «Правило» row before the cases."""
    task = _write_task(tmp_path, OOP_TESTS, solution_py=textwrap.dedent(OOP_SOLUTION))
    student = textwrap.dedent(
        """
        from dataclasses import dataclass

        @dataclass
        class Account:
            _balance: int = 100

            def deposit(self, amount):
                self._balance += amount

            def __repr__(self):
                return "Account()"

        def task_x(amount):
            account = Account()
            account.deposit(amount)
            return account._balance
        """
    )
    result = run_check(task, student)
    assert result.status == "partial"  # the case still passes
    assert result.passed_tests == 1
    rule_rows = [tr for tr in result.results if tr.description.startswith(RULE_PREFIX)]
    assert result.total_tests == 1 + len(rule_rows)
    assert [tr.description for tr in rule_rows] == [
        "Правило: нужен класс `Account` с методом `balance`, помеченным @property",
        "Правило: к `\\_balance` нельзя обращаться снаружи класса (строка 17)",
    ]
    assert [tr.expected_repr for tr in rule_rows] == ["Account.balance", "_balance"]
    assert all(not tr.passed and tr.actual_repr is None and tr.error is None for tr in rule_rows)
    assert rule_rows[0].level == "smoke"


def test_run_check_missing_property_message(tmp_path):
    task = _write_task(tmp_path, OOP_TESTS, solution_py=textwrap.dedent(OOP_SOLUTION))
    student = textwrap.dedent(
        """
        from dataclasses import dataclass

        @dataclass
        class Account:
            balance: int = 100

            def deposit(self, amount):
                self.balance += amount

            def __repr__(self):
                return "Account()"

        def task_x(amount):
            account = Account()
            account.deposit(amount)
            return account.balance
        """
    )
    result = run_check(task, student)
    assert result.status == "partial"
    assert result.results[0].description == (
        "Правило: нужен класс `Account` с методом `balance`, помеченным @property"
    )
    assert result.results[0].expected_repr == "Account.balance"


def test_run_check_missing_class(tmp_path):
    task = _write_task(tmp_path, OOP_TESTS, solution_py=textwrap.dedent(OOP_SOLUTION))
    result = run_check(task, "def task_x(amount):\n    return 100 + amount\n")
    assert result.status == "partial"
    assert result.results[0].description == "Правило: нужен класс `Account`"
    assert result.results[0].level == "smoke"
