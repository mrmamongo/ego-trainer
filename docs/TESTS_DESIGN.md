# Task file format: separate solution + tests

## File layout

```
docs/tasks/block_f_simple/
├── task_f1.md           # только условие (Условие, Аргументы, Возвращает, Правила, Пример)
├── task_f1.solution.py  # эталонное решение
└── task_f1.tests.py     # тесты (@case) + before/after hooks
```

## task_f1.md

Только условие. Больше НЕТ `<details>Эталонное решение</summary>` — решение в отдельном файле.

```markdown
# Задача F1: Найди первый критический баг

**Блок:** F — Базовые паттерны
**Сложность:** easy
**Темы:** find, linear search, first match

## Условие

В баг-трекере нужно найти первый критический баг...

## Аргументы

- `bugs` — список словарей

## Возвращает

Строку — title первого critical бага, или "".

## Правила

- Верни title первого critical бага
- Если нет — верни ""

## Пример

```python
task_f1_find_critical(bugs)
# -> "Crash on login"
```
```

## task_f1.solution.py

Эталонное решение — обычный Python файл.

```python
def task_f1_find_critical(bugs):
    for b in bugs:
        if b["severity"] == "critical":
            return b["title"]
    return ""
```

## Test levels (smoke vs full)

Два уровня прогона — быстрая проверка работоспособности и полный функционал.

| Level | Назначение | Что внутри | Когда |
|-------|------------|------------|-------|
| `smoke` | быстрые тесты работоспособности | 2–5 явных `@case` (happy path + 1–2 edge) | default: `ego check`, UI Check |
| `full` | полный функционал | дополнительные edge `@case` + (post-MVP) Hypothesis `@scenario` | `ego check --full`, CI, ментор |

**Правила:**
- У каждого `@case` / `@scenario` есть `level: "smoke" | "full"` (default для `@case` — `"smoke"`).
- `ego check` → только `smoke`.
- `ego check --full` (или `--level all`) → `smoke` + `full`.
- `--level smoke|full|all` — явный выбор; `full` = только full-кейсы (без smoke), `all` = оба.
- Hypothesis / property (эпик `9u7`) всегда `level="full"` — в default-check не тормозят студента.
- Старые `## Тесты` / `literal_eval` считаются `smoke`.

## task_f1.tests.py

Тесты с `@case` декоратором + `@before` / `@after` хуками + уровнем.

```python
from ego.testing import case, before, after

@before
def setup(task_func):
    """Вызывается перед каждым тестом. Возвращает dict с доп. данными."""
    return {"start_time": time.time()}

@after
def teardown(task_func, case_result, ctx):
    """Вызывается после каждого теста. Для логирования/очистки."""
    elapsed = time.time() - ctx["start_time"]
    if elapsed > 1.0:
        print(f"Slow test: {case_result.description} ({elapsed:.2f}s)")

# --- smoke (default ego check) ---
@case(
    args=([{"id": "B1", "severity": "critical", "title": "Crash"}],),
    expected="Crash",
    description="basic: one critical bug",
    level="smoke",
)
@case(
    args=([],),
    expected="",
    description="empty list",
    level="smoke",
)

# --- full (ego check --full) ---
@case(
    args=([{"id": "B1", "severity": "minor", "title": "Typo"}],),
    expected="",
    description="no critical bugs",
    level="full",
)
@case(
    args=(
        [
            {"id": "B1", "severity": "minor", "title": "A"},
            {"id": "B2", "severity": "critical", "title": "B"},
            {"id": "B3", "severity": "critical", "title": "C"},
        ],
    ),
    expected="B",
    description="first critical wins",
    level="full",
)
def task_f1_find_critical(bugs):
    ...
```

## Hooks

### `@before`

```python
@before
def setup(task_func) -> dict:
    """Вызывается перед каждым @case. Возвращает context dict."""
    return {"mock_db": create_mock_db()}
```

- Вызывается перед каждым тестом
- Возвращает dict — передаётся в `@after` и доступен в тестах (опционально)
- Использование: mock внешних ресурсов, подготовка данных, таймеры

### `@after`

```python
@after
def teardown(task_func, case_result, ctx: dict) -> None:
    """Вызывается после каждого @case. Для логирования/очистки."""
    if not case_result.passed:
        log_failure(case_result)
```

- Вызывается после каждого теста
- Получает `case_result` (passed, expected, actual, error) и `ctx` из `@before`
- Использование: cleanup, логирование, сбор метрик

### Порядок вызова

```
for each @case:
    ctx = before(task_func)          # если есть @before
    result = run_student(args)       # запуск student code
    compare(result, expected)
    after(task_func, result, ctx)    # если есть @after
```

## `ego/testing.py`

```python
from dataclasses import dataclass
from typing import Any, Callable, Literal

TestLevel = Literal["smoke", "full"]

@dataclass
class TestCase:
    args: tuple
    expected: Any
    description: str = ""
    level: TestLevel = "smoke"

@dataclass
class CaseResult:
    description: str
    passed: bool
    expected_repr: str
    actual_repr: str | None
    error: str | None = None
    level: TestLevel = "smoke"

def case(
    *,
    args: tuple,
    expected: Any,
    description: str = "",
    level: TestLevel = "smoke",
):
    """Decorator: register a test case for a task function."""
    def decorator(func):
        if not hasattr(func, "_ego_cases"):
            func._ego_cases = []
        func._ego_cases.append(
            TestCase(args=args, expected=expected, description=description, level=level)
        )
        return func
    return decorator

def before(func: Callable):
    """Decorator: register a before-hook (setup). Must return dict."""
    func._ego_before = True
    return func

def after(func: Callable):
    """Decorator: register an after-hook (teardown)."""
    func._ego_after = True
    return func
```

## How checker works (updated)

1. Parser находит `task_f1.solution.py` и `task_f1.tests.py` рядом с `.md`
2. Parser: `solution_py` из `.solution.py` (не из `<details>` в .md)
3. Parser: `tests_file` — путь к `.tests.py` (поле `Task.tests_file`)
4. Checker:
   a. Импортирует `.tests.py` (через `importlib`)
   b. Находит `task_*` функцию, собирает `_ego_cases`
   c. Фильтрует по `level` аргумента `run_check` (`smoke` | `full` | `all`, default `smoke`)
   d. Находит `_ego_before` / `_ego_after` функции
   e. Для каждого выбранного `@case`:
      - `ctx = before(task_func)` если есть
      - Запускает student code с `case.args`
      - Сравнивает `repr(result)` с `repr(expected)`
      - `after(task_func, result, ctx)` если есть
   f. Агрегирует в `CheckResult` (включая какой level был запрошен)
5. Post-MVP (`9u7`): при `level in (full, all)` дополнительно гоняет `@scenario` / Hypothesis (ref = oracle)

## Migration

1. Создать `ego/testing.py` (`@case` + `level`, `@before`, `@after`, `TestCase`, `CaseResult`)
2. Обновить parser:
   - `solution_py` — читать из `<task>.solution.py` (fallback: `<details>` в .md для совместимости)
   - `tests_file` — путь к `<task>.tests.py` (новое поле в Task)
3. Обновить checker:
   - `_extract_test_cases` — импортировать `.tests.py` через `importlib`
   - Фильтр по level (`smoke` / `full` / `all`)
   - Добавить before/after вызовы в `run_check`
4. CLI/API: `ego check --full` / `--level`, опционально в `POST /check` и vscode Check
5. Написать `.solution.py` + `.tests.py` для всех существующих задач (smoke + часть full)
6. Убрать `<details>Эталонное решение</summary>` из .md (или оставить как fallback)
7. Тесты на parser (новый формат) + checker (hooks + levels) + testing module
8. Post-MVP: Hypothesis `@scenario` только на `level=full` (эпик `9u7`)

## Совместимость

- Старые .md с `<details>` — parser fallback на старый формат (deprecated)
- Старые .md с `## Тесты` — parser fallback на `ast.literal_eval` (deprecated), level=`smoke`
- Новые задачи — только отдельные файлы
- Default check без флагов = `smoke` (быстро для студента)
