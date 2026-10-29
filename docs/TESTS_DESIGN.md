# Task file format: separate solution + tests

## Product exercise contracts (XL-A)

An optional `task_<slug>.student.py` sidecar supplies the actual learner
starter, including intentional bugs, modification baselines and GIVEN helpers.
The parser uses it verbatim after syntax validation. Without the sidecar,
signature-based stub generation remains unchanged. Starter changes affect
`content_hash`; bump the task version when changing a published starter.

New `@case` options are opt-in; existing tests keep their previous behavior:

- `comparison="value"`: compare literal data recursively. Dictionary key
  order is ignored; list order, container types and scalar types matter
  (`True` differs from `1`). The default remains `comparison="repr"`.
- `check_inputs_unchanged=True`: observe arguments in the student subprocess
  before and after the call; a change fails the case, even if the return value
  looks correct. This checks data values and types, not Python reference counts.
- `check_result_isolated=True`: reject returned mutable containers that are
  shared with the arguments. Use only when the task explicitly requires an
  independent result. Immutable strings/numbers/tuples may be shared.
- `input_aliases=(((0, "B", "preferences"), (0, "A", "preferences")),)`:
  recreate shared input objects inside the subprocess. Each pair is
  `(target_path, source_path)`; a path starts with a positional argument index.
  Pairs apply in declaration order, before the unchanged-input snapshot.

For example, two users sharing one preferences object can expose a shallow
copy bug. Plain literal argument serialization loses that relationship, so
such a case must declare the alias explicitly. Reference implementations must
pass the same observations as learner submissions.

These checks grade public behavior. Helper composition and refactoring quality
remain mentor review criteria; behavior tests cannot prove that a learner
decomposed a function well. XL-A25 therefore legitimately passes behavior tests
before refactoring.

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

## Static rules (`@rules`)

Тесты видят только возвращаемые значения, поэтому «не используй `sorted`» из
условия так не проверить: `sorted(a + b)` проходит задачу на слияние. Для этого
есть opt-in статические правила — AST-проверка кода студента. Они объявляются в
`.tests.py` рядом с `@case`:

```python
from ego.testing import case, rules

@rules(
    forbid_names=["sum", "sorted", "max"],       # bare names / builtins (Call или ссылка)
    forbid_methods=["sort", "replace"],          # вызовы x.sort(...), s.replace(...)
    forbid_imports=["math"],                     # import math / from math import ...
    forbid_nodes=["Global", "Lambda", "ListComp"],  # имена классов ast
    require_functions=["parse_command"],         # обязательные функции верхнего уровня
    allow_in=["given_helper"],                   # функции, где forbid_* не действует
    messages={"sorted": "Сортировку нужно написать самому"},  # сообщения по ключу правила
)
@case(args=([1, 3], [2]), expected=[1, 2, 3], description="merge")
@case(args=([], [1]), expected=[1], description="empty + one")
def task_li21_merge_sorted(a, b):
    ...
```

Правила:

- `@rules` можно ставить до или после `@case` в любом порядке; на функцию —
  максимум один `@rules` (второй даёт `ValueError` при загрузке модуля).
- Аргументы проверяются при декорации: неизвестное имя узла `ast`,
  несуществующий ключ в `messages` или строка вместо списка → `ValueError`.
- Функции с именем `given_*` (GIVEN-хелперы из стартера) всегда освобождены от
  `forbid_*`; `allow_in` добавляет к ним другие имена. Также не учитывается имя
  модуля, затенённое параметром (`def f(math)`).
- `messages` принимает имя правила (`"sorted"`, `"sort"`, `"math"`, `"Global"`)
  или квалифицированную форму (`"method:sort"`).

### Правила для ООП-задач

Курс по ООП проверяет не только ответ, но и устройство классов:

```python
from ego.testing import case, rules

@rules(
    require_classes=["Account", "Shape", "Circle"],          # классы верхнего уровня
    require_decorators={                                     # "Класс" или "Класс.метод"
        "Account": ["dataclass"],
        "Account.balance": ["property", "setter"],
        "Account.from_dict": ["classmethod"],
        "Shape.area": ["abstractmethod"],
    },
    require_methods={"Account": ["deposit", "withdraw", "__repr__"]},  # методы в теле класса
    require_methods_inherited={"Child": ["deposit"]},        # ... или унаследованные (для этого класса)
    require_bases={"Shape": ["ABC"], "Circle": ["Shape"]},  # прямые базовые классы
    forbid_bases={"Inventory": ["list", "dict"]},            # наследование нельзя
    forbid_attributes_outside_class=["_balance"],            # x._balance снаружи класса нельзя
)
@case(args=(50,), expected=150, description="deposit 50")
def task_oop_account(amount):
    ...
```

Что считается:

| Аргумент | Проверяет |
|----------|-----------|
| `require_classes=["Account"]` | есть `class Account` на верхнем уровне (вложенные и локальные в функциях — нет) |
| `require_decorators={"Account": ["dataclass"]}` | у класса есть декоратор: `@dataclass`, `@dataclasses.dataclass`, `@dataclass(frozen=True)` |
| `require_decorators={"Account.balance": ["property"]}` | у метода в теле класса есть декоратор |
| `require_methods={"Account": ["deposit"]}` | метод определён в теле класса (унаследованный не считается) |
| `require_methods_inherited={"Child": ["deposit"]}` | для этого класса унаследованные методы тоже считаются |
| `require_bases={"Circle": ["Shape"]}` / `forbid_bases` | прямой базовый класс (`abc.ABC` = `ABC`, `collections.OrderedDict` = `OrderedDict`) |
| `forbid_attributes_outside_class=["_balance"]` | чтение/запись `x._balance` вне тела класса; внутри класса и его методов — можно |

Декораторы понимаются так: `@property` → `"property"`, `@x.setter` / `@x.getter`
/ `@x.deleter` → `"setter"` / `"getter"` / `"deleter"`, `@classmethod`,
`@staticmethod`, `@abstractmethod` / `@abc.abstractmethod` → `"abstractmethod"`,
`@cached_property`, `@total_ordering`, `@unique`, `@dataclass`. Неизвестное имя
декоратора — `ValueError` при декорации. Если у класса несколько требований,
в сообщении называется первое недостающее (`@Account.balance: ["property",
"setter"]` с одним только сеттером скажет про `@property`).

Классы с именем `Given*` и функции `given_*` (GIVEN-заготовки из стартера)
освобождены от этих правил.

Сообщения (по одному результату на нарушение):

```
Правило: нужен класс `Account`
Правило: `Account` должен быть помечен @dataclass (строка 4)
Правило: метод `balance` в классе `Account` должен быть помечен @property (строка 7)
Правило: нужен метод `deposit` в классе `Account`
Правило: `Circle` наследуется от `Shape` (строка 12)
Правило: `Inventory` не должен наследоваться от `list` (строка 16)
Правило: к `\\_balance` нельзя обращаться снаружи класса (строка 12)
```

Пропавший класс называется **один раз**: если он перечислен в
`require_classes`, то `require_decorators` / `require_methods` / `require_bases`
про него молчат (иначе одна ошибка давала бы три результата). Без
`require_classes` про него скажет первое правило, которому он нужен
(«нужен класс `Account` с @dataclass»). Метод, которого нет в классе, тоже
сообщается один раз — в `require_methods` (или в `require_decorators`, если в
`require_methods` его нет).

Ключи для `messages`: имя класса (`"Account"`), метод (`"Account.deposit"`),
база (`"Circle -> Shape"`), атрибут (`"_balance"`).

Проверка (`ego/checker.py` + `ego/static_rules.py`):

- перед запуском кейсов код студента парсится через `ast`; при `SyntaxError`
  поведение прежнее (ошибку сообщает runner для каждого кейса).
- каждое нарушение — один неуспешный `TestResult` **первым** в `results`:
  `description="Правило: нельзя использовать \`sorted\` (строка 7)"`,
  `level="smoke"`, `expected_repr="sorted"` (ключ правила), `actual_repr=None`,
  `error=None`. Нет обязательной функции → `«Правило: нужна функция \`parse_command\`»`.
- На каждое правило — один результат (первая строка), а не на каждое вхождение.
- Кейсы всё равно запускаются; `status` не может стать `passed`, пока правило
  нарушено; `passed_tests` считает только кейсы, `total_tests` включает
  результаты правил. Формы `CheckResult` / `TestResult` не меняются.
- Верификаторы (`scripts/verify_*_catalog.py`) проверяют эталонное решение
  теми же правилами: эталон, нарушающий свои же `@rules`, роняет проверку.

`@rules` не входит в `content_hash` (`statement_md + stub_py + solution_py`) и
не версионируется сам по себе: меняя правила опубликованной задачи, подними
`version` в frontmatter, иначе sync не применит изменение.

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

## Челленджи (многофайловые)

ADR-0018: программа из нескольких модулей, которая растёт по этапам. Челлендж — папка каталога с
`kind: challenge`, этап — обычная задача каталога (`stage_NN_<slug>.md`), код живёт в папке проекта,
которую собирает расширение.

### Папка челленджа

```
folders/kv_store/
├── folder.yaml                  # kind: challenge + workspace
├── lesson_*.md                  # теория, как в обычных папках
├── starter/                     # стартовый проект (main.py, commands.py, …)
├── solution/                    # эталон после последнего этапа
├── stage_01_parse.md            # условие этапа (frontmatter id/title/version/level/tags)
├── stage_01_parse.tests.py      # тесты этапа
├── stage_02_save.md
├── stage_02_save.tests.py
└── stage_02_save.solution/      # необязательно: эталон ровно после этапа 2
```

```yaml
# folder.yaml
id: kv_store
code: KV
name: "Своё хранилище ключ-значение"
kind: challenge
workspace:
  entry: main.py               # что запускает «чёрный ящик» (@program)
  include: ["*.py", "data/*.json"]   # какие файлы собираются из папки студента
  max_files: 20
  max_bytes: 200000
```

- Номера этапов — с 01 без пропусков; иначе каталог не загрузится. У этапа нет `.solution.py` и
  `.student.py`: хеш версии считается по условию (`.md`) и, если есть, по эталону этапа
  `stage_NN_<slug>.solution/` — как у обычной задачи.
- `workspace` есть только у челленджей. `entry` и `include` проверяются `scripts/verify_challenges.py`.

### `@case(target="module.func")` — импорт

Вызывает функцию модуля из папки студента. Остальные аргументы `@case` работают как раньше
(`level`, `comparison`, `hide_expected`, `check_inputs_unchanged`, `input_aliases`, …). Модуль
импортируется под своим именем, поэтому блок `if __name__ == "__main__"` не выполняется.

```python
from ego.testing import case, rules

@rules(require_functions=["parse_command"])
@case(
    target="commands.parse_command",
    args=("set a 1",),
    expected=("SET", ["a", "1"]),
    description="SET с аргументами",
)
def task_kv01_parse():
    ...
```

### `@program(...)` — чёрный ящик

Запускает `python -S <entry>` (по умолчанию `main.py` из `workspace`) в копии папки, `cwd` — эта
копия; на stdin подаётся `stdin`, stdout сравнивается построчно (хвостовые пробелы и последний
перевод строки не считаются).

```python
from ego.testing import program

@program(
    stdin="SET a 1\nGET a\nEXIT\n",
    expected_stdout="OK\n1\n",
    description="SET, потом GET",
    files={"data/store.json": '{"x": "5"}'},                 # файлы до запуска
    expect_files={"data/store.json": {"x": "5", "a": "1"}},  # JSON в файлах после
)
def task_kv02_repl():
    ...
```

| Аргумент | Смысл |
|----------|-------|
| `match` | `lines` (по умолчанию: те же непустые строки без учёта отступа), `exact` (тот же текст, без хвостовых пробелов и последнего перевода строки), `contains` (ожидаемые строки встречаются по порядку, вывод может быть длиннее) |
| `expected_exit` | ожидаемый код завершения (`None` — `0`) |
| `files` | `{путь: содержимое}` — раскладывается поверх проекта до запуска |
| `expect_files` | `{путь: JSON}` — файл после запуска читается как JSON и сравнивается (`True` ≠ `1`) |
| `timeout` | таймаут запуска в секундах (по умолчанию — таймаут проверки) |
| `hide_expected` | не показывать ожидаемый вывод |
| `entry` | другой файл вместо `workspace.entry` |

Аргументы проверяются при декорации (`ValueError`), как у `@case`.

### `@rules` по проекту

Статические правила в челлендже проверяют весь проект: `require_functions`, `require_classes`,
`require_methods`, `forbid_imports` и остальные ключи вычисляются по всем `.py` файлам папки
студента. `@rules(file="storage.py", ...)` сужает правило до одного файла проекта. На одной
функции объявляется **одно** правило — либо по проекту, либо с `file=`; два `@rules` на одной
функции (`ValueError` при загрузке тестов) не складываются.

### Песочница и пути

`ego.runner.run_project(files, ...)` раскладывает файлы во временную папку и запускает
`python -S` (без site-packages; `sys.path` проекта нужен для импортов между модулями студента).
`validate_project_files(files, workspace)` проверяет до запуска (сообщения по-русски): только
относительные POSIX-пути, без `..`, абсолютных путей и `\`; `.cogito/`, `__pycache__/`,
`.venv/` писать нельзя; каждый файл подходит под `include`; лимиты `max_files` и `max_bytes`.
Мягкие предупреждения `BLOCKED_IMPORTS` работают как раньше; импорты самого раннера
(`importlib`, `os`, `traceback`) импортом студента не считаются.

### Проверка по этапам (`run_stage_check`)

Проверка этапа N гоняет тесты этапов 1..N: сломал этап 2, доделывая этап 5 — этап 5 не
засчитан. У каждого результата есть `stage` и `stage_title`, лог (`format_stage_check_result`)
группирует результаты по этапам. В прогресс пишется только этап N.

### API: `POST /check` с `files` и `GET /challenges/<id>`

Этапы — обычные строки `tasks` (колонка `challenge_stage`: 1..N), папка — `folders.kind =
'challenge'` с `folders.workspace_json`. Прогресс, кабинет и рекомендации видят этапы как задачи;
аддитивные миграции только добавляют колонки (`tasks.challenge_stage`, `folders.kind`,
`folders.workspace_json`, `runs.files_json`).

```http
POST /check
Authorization: Bearer <token>
{"task_id": "KV01", "files": {"main.py": "...", "commands.py": "..."}}
```

| Что отправлено | Обычная задача | Этап челленджа |
|----------------|----------------|----------------|
| `student_code` | проверка как раньше (`run_check`) | 422 «этот этап проверяется только новой версией Cogito — обнови расширение» |
| `files` | 422: `files` только для этапа челленджа | `run_stage_check` по этапам 1..N |
| оба / ни одного | 422 с понятным текстом | 422 с понятным текстом |
| `files: {}` | — | 422 «files пустой…»: проект без файлов не «проходит» этап впустую |

- Лимиты: `workspace` (`include`, `max_files`, `max_bytes`) и `max_code_chars` из настроек
  сервера — по всему проекту в склейке `# === path ===\n<content>`; нарушение `workspace` —
  422 с русским текстом (`validate_project_files`), превышение `max_code_chars` — 413.
- В ответе у каждого результата есть `stage` и `stage_title`; у обычной задачи этих полей нет
  (форма ответа не меняется). `log` — `format_stage_check_result` (результаты по этапам).
- Прогресс и строка `runs` пишутся только для этапа N; проект целиком сохраняется в
  `runs.files_json` (`{путь: код}`), а в AI и историю уходит склейка `project_view`.
- `solution_hash` этапа — sha256 склейки проекта, а не одной функции.

`GET /challenges/<folder_id>` (та же авторизация, что у `/tasks`): метаданные папки,
`workspace`, `stages` (`id`, `title`, `number`, `order`, `level`, `version`, `status`,
`passed_tests`, `total_tests`, `current`) и стартовые файлы `starter/` как `{путь: содержимое}`.
`status` — прогресс вызывающего студента на текущей версии этапа (`new`, если не проверял);
`current` — первый непройденный этап, с него начинают. Неизвестная папка или папка не
`kind: challenge` — 404. `solution/` через API не отдаётся никогда.

### Верификатор

```bash
python -m scripts.verify_challenges --catalog tests/fixtures/challenges_catalog --timeout 30
```

Проверяет, что `solution/` проходит все этапы, `starter/` не проходит этап 1, `stage_K.solution/`
проходит этапы 1..K и не проходит K+1, у этапа не меньше трёх smoke-проверок и есть `full`,
пути и `include` корректны. Тот же формат — на будущих челленджах в репозитории контента.

## How checker works (updated)

1. Parser находит `task_f1.solution.py` и `task_f1.tests.py` рядом с `.md`
2. Parser: `solution_py` из `.solution.py` (не из `<details>` в .md)
3. Parser: `tests_file` — путь к `.tests.py` (поле `Task.tests_file`)
4. Checker:
   a. Импортирует `.tests.py` (через `importlib`)
   b. Находит `task_*` функцию, собирает `_ego_cases` и опциональные `@rules`
   c. Фильтрует по `level` аргумента `run_check` (`smoke` | `full` | `all`, default `smoke`)
   d. Находит `_ego_before` / `_ego_after` функции
   d1. Если у задачи есть `@rules` — парсит код студента (`ast`) и ставит
      результаты нарушений первыми в `results` (см. «Static rules»)
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
