"""Export the original XL-A source pack into a self-contained Cogito catalog.

Only metadata, statements, and student starters belong to this generator.
Reference solutions and tests are authored separately and are never overwritten.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import textwrap
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPO_ROOT / "docs" / "tasks" / "XL-A"
VERSION = "1.0.0"
TITLE_RE = re.compile(r"^XL-A(?P<number>\d{2})\. (?P<kind>.+?) — (?P<title>.+)$")
TASK_RE = re.compile(r"^task_xla(?P<number>\d{2})_")
KINDS = {"НАЙТИ БАГ": "bug", "ПРАВКИ": "modify", "НОВЫЙ КОД": "new"}


@dataclass(frozen=True)
class Group:
    folder: str
    name: str
    domain: str


GROUPS = (
    Group("01_chat_context", "История чатбота", "chat-context"),
    Group("02_quest_journal", "Квестовый журнал", "quest-journal"),
    Group("03_party_finder", "Поиск группы в MMO", "party-finder"),
    Group("04_answer_sources", "Источники ответа", "answer-sources"),
    Group("05_guild_assistant", "Помощник гильдии", "guild-assistant"),
    Group("06_crafting", "Производство", "crafting"),
    Group("07_market", "Рынок", "market"),
    Group("08_assistant_memory", "Память помощника", "assistant-memory"),
    Group("09_agent_plans", "Планы агента", "agent-plans"),
)

PARTY_CONTRACT = """Места и результат подбора:
    slots = {"tank": 1, "healer": 1, "damage": 2}
    result = {"members": [ID],
              "missing": {"tank": int, "healer": int, "damage": int},
              "ready": bool}

Количество мест — целое >= 0. Отсутствующая в slots роль требует 0 мест.
Роли обрабатываются в порядке tank, healer, damage. Внутри роли сначала
выбирается большее wait_seconds, при равенстве — меньший по алфавиту ID
игрока. members следует этому порядку. При нехватке сохраняется частичный
состав. В missing всегда все три роли и число незаполненных мест каждой.
ready=True ровно при отсутствии незаполненных мест. Для slots={}
members=[], все значения missing равны 0, ready=True."""

GUILD_CONTRACT = """Состояние и канонические команды:
    state = {"events": [{"id": "e1", "title": "Рейд", "capacity": 2,
                         "members": ["m1"]}], "next_id": 2}
    create = {"tool": "create_event", "args": {"title": "Рейд", "capacity": 2}}
    join = {"tool": "join_event", "args": {"event_id": "e1", "member_id": "m2"}}

next_id задаёт следующий свободный номер eN. create_event добавляет
событие с пустым members, увеличивает next_id и возвращает value={event_id}.
join_event добавляет участника и возвращает value={event_id, member_id}.
Порядок отказов вступления: unknown_event, already_joined, event_full.
Неизвестная команда отклоняется с unknown_tool. given_dispatch возвращает
{status, state, result, reason}: при успехе status="done", result=value,
reason=None; при отказе status="rejected", result=None, reason — код отказа,
state равно исходному состоянию. Входные объекты сохраняются."""

RECIPE_CONTRACT = """Данные одного рецепта:
    inventory = {"iron": 3, "hammer": 1}
    recipe = {"ingredients": {"iron": 2}, "tools": {"hammer": 1},
              "product": {"item": "sword", "qty": 1}}

Имена предметов — строки. В inventory количества целые >= 0.
ingredients обязательно и задаёт положительные количества расходуемых
материалов. tools необязательно, по умолчанию {}; инструменты нужны
для проверки наличия и не расходуются. product имеет поля item (строка)
и qty (положительное целое). Если один предмет нужен как материал и как
инструмент, до начала крафта требуется сумма количеств; списывается только
материал. Проверяются все требования по исходному запасу. Успех сохраняет
нулевые и посторонние ключи, добавляет продукт. При нехватке запас не меняется.
given_craft возвращает {status: "crafted" или "missing", inventory: новый
словарь, missing: словарь положительных нехваток}. Порядок ключей missing
не является критерием правильности: сравниваются названия и количества."""

ACTION_CONTRACT = """Команды GIVEN given_run_action:
- create_event: args={title, capacity}. title — непустая строка после strip,
  иначе invalid_title; capacity — именно int >= 1, bool не подходит,
  иначе invalid_capacity. Создаётся e<next_id> с пустыми members, счётчик
  увеличивается; result={event_id}.
- join_event: args={event_id, member_id}. Проверки по порядку: unknown_event;
  непустая строка member_id без обрезки, иначе invalid_member;
  already_joined; event_full. Успех добавляет участника,
  result={event_id, member_id}.
- prepare_announcement: args={event_id, text}. Сначала unknown_event,
  затем непустая строка text после strip, иначе invalid_text. Успех
  добавляет объявление; result={announcement_index}, индекс начинается с 0.

Неизвестный tool даёт unknown_tool. Результат одной команды содержит
{status, state, result, reason}. Успех: done и reason=None. Отказ: rejected,
result=None, reason — код ошибки; состояние остаётся прежним. Предметная
логика уже дана в given_run_action, её не нужно повторять."""

PLAN_CONTRACT = """Данные плана и правила выполнения:
    step = {"id": "join", "tool": "join_event", "critical": True,
            "args": {"event_id": {"from_step": "create", "field": "event_id"},
                     "member_id": "Sam"}}
    report = {"id": "join", "status": "done", "result": {}, "reason": None}

steps — список шагов в порядке выполнения. id — уникальная строка;
critical — bool. Значения args — str, int, bool, None либо одноуровневая
ссылка {from_step: id, field: имя_поля} на более ранний шаг. Поле результата
может отсутствовать. Аргументы просматриваются в порядке вставки: первая
ошибка ссылки определяет отказ. given_resolve_args возвращает (args, error).
Неуспешная зависимость даёт dependency_failed:<id>; отсутствующее поле —
missing_result_field:<id>:<field>. Такой шаг получает rejected, result=None.
Разрешённые аргументы передаются в given_run_action. Успех имеет done,
result команды и reason=None; отказ — rejected, result=None и reason команды.
Отказ не меняет состояние. После некритичного отказа выполнение продолжается.
После critical-отказа все следующие шаги получают skipped, result=None,
reason=stopped_after:<упавший_id>. Отчёты сохраняют порядок исходных шагов.
Пустой план успешен. Правила reused и возвращаемого completed приведены
в условии возобновления ниже."""

EXTRA_CONTRACTS = {
    9: PARTY_CONTRACT,
    15: GUILD_CONTRACT,
    17: RECIPE_CONTRACT,
    26: ACTION_CONTRACT,
    27: ACTION_CONTRACT + "\n\n" + PLAN_CONTRACT,
}


def yaml_string(value: str) -> str:
    """JSON string quoting is also valid YAML and needs no extra dependency."""
    return json.dumps(value, ensure_ascii=False)


def shared_contract(module: ast.Module, number: int) -> str:
    lines = (ast.get_docstring(module) or "").splitlines()
    text = "\n".join(lines[1:]).strip()
    text = re.sub(r"^НАЙТИ БАГ:.*\n?", "", text, flags=re.MULTILINE)
    text = re.sub(r"^ПРАВКИ:.*\n?", "", text, flags=re.MULTILINE)
    text = re.sub(r"^НОВЫЙ КОД:.*\n?", "", text, flags=re.MULTILINE)
    text = text.replace(
        "Готового checker.py в этой пачке нет. Примеры можно вызывать самостоятельно.", ""
    )
    text = text.replace("Здесь нет solution.py или checker.py.", "")
    text = text.replace(
        "В XL-A19/20 покупатель и продавец различны; XL-A21 пропускает\nсобственные лоты.",
        "Покупатель и продавец различны."
        if number in (19, 20)
        else "Собственные лоты пропускаются.",
    )
    text = text.replace("id лотов в XL-A21 уникальны", "id лотов уникальны")
    text = text.replace(
        "В XL-A26/27 также разрешены словари-ссылки.",
        "В аргументах шагов также разрешены словари-ссылки." if number in (26, 27) else "",
    )
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def task_documentation(node: ast.FunctionDef, number: int) -> str:
    text = ast.get_docstring(node) or ""
    replacements = {
        9: [
            (
                "slots и результат имеют договор XL-A08.",
                "Форматы slots и результата приведены в договоре данных этой задачи.",
            )
        ],
        15: [
            (
                "state и command имеют формат XL-A14: события, next_id и каноническая\n"
                "    команда create_event или join_event.",
                "state содержит события и next_id; command — каноническая\n"
                "    команда create_event или join_event. Форматы приведены в договоре данных.",
            ),
            (
                "given_dispatch; эта задача от XL-A14 не зависит.",
                "given_dispatch, приведённый в этом файле.",
            ),
        ],
        17: [("рецептам формата XL-A16.", "рецептам из договора данных этой задачи.")],
        20: [
            (
                "given_buy_whole как опору для старого полного сценария; не вызывай код\n"
                "задачи XL-A19 и не полагайся на него.",
                "given_buy_whole как опору для старого полного сценария.",
            )
        ],
        24: [("с правилами XL-A22", "с правилами из договора данных этой задачи")],
        27: [
            (
                "Используй правила\nXL-A26 для ссылок, error при отсутствующем поле, dependency_failed,",
                "Используй правила из договора данных этой задачи для ссылок,\n"
                "error при отсутствующем поле, dependency_failed,",
            )
        ],
    }
    for old, new in replacements.get(number, []):
        if old not in text:
            raise ValueError(f"Documentation reference changed in XL-A{number:02d}: {old!r}")
        text = text.replace(old, new)
    return text


def render_markdown(text: str) -> str:
    """Keep prose as prose and preserve indented examples in fenced blocks."""
    lines = text.splitlines()
    rendered: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        if line.startswith("    "):
            block: list[str] = []
            while index < len(lines) and (
                lines[index].startswith("    ") or not lines[index].strip()
            ):
                block.append(lines[index])
                index += 1
            code = textwrap.dedent("\n".join(block)).strip("\n")
            try:
                ast.parse(code)
                language = "python"
            except SyntaxError:
                language = "text"
            rendered.extend(["", f"```{language}", code, "```", ""])
            continue
        if line and line.endswith(":") and not line.startswith(("-", "#")):
            rendered.append(f"**{line}**")
        else:
            rendered.append(line)
        index += 1
    return re.sub(r"\n{3,}", "\n\n", "\n".join(rendered)).strip()


def bound_names(node: ast.AST) -> set[str]:
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return {node.name}
    if isinstance(node, (ast.Import, ast.ImportFrom)):
        return {alias.asname or alias.name.split(".")[0] for alias in node.names}
    if isinstance(node, (ast.Assign, ast.AnnAssign)):
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        return {
            part.id for target in targets for part in ast.walk(target) if isinstance(part, ast.Name)
        }
    return set()


def dependencies(node: ast.AST) -> set[str]:
    names = {
        part.id
        for part in ast.walk(node)
        if isinstance(part, ast.Name) and isinstance(part.ctx, ast.Load)
    }
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        # A pass starter can name required GIVEN helpers only in its contract.
        names.update(re.findall(r"\bgiven_\w+\b", ast.get_docstring(node) or ""))
    return names


def starter_nodes(module: ast.Module, target: ast.FunctionDef) -> list[ast.AST]:
    symbols = {name: node for node in module.body for name in bound_names(node)}
    selected = {target}
    pending: list[ast.AST] = [target]
    while pending:
        node = pending.pop()
        for name in sorted(dependencies(node)):
            dependency = symbols.get(name)
            if dependency is None or dependency in selected:
                continue
            if name.startswith("task_") and dependency is not target:
                raise ValueError(f"Starter {target.name} depends on another task: {name}")
            selected.add(dependency)
            pending.append(dependency)
    return sorted(selected, key=lambda node: node.lineno)


def render_docstring(text: str, indent: str = "") -> str:
    escaped = text.replace("\\", "\\\\").replace('"""', '\\"\\"\\"')
    lines = ['"""', *escaped.splitlines(), '"""']
    return "\n".join(indent + line if line else "" for line in lines)


def node_source(source: str, node: ast.AST, documentation: str | None = None) -> str:
    segment = ast.get_source_segment(source, node)
    if segment is None:
        raise ValueError("Cannot locate source segment")
    if isinstance(node, ast.FunctionDef) and ast.get_docstring(node) is not None:
        original_doc = ast.get_docstring(node) or ""
        cleaned_doc = (
            documentation
            if documentation is not None
            else original_doc.replace("; независима от XL-A14", "")
        )
        if cleaned_doc != original_doc:
            expression = node.body[0]
            lines = segment.splitlines()
            before = lines[: expression.lineno - node.lineno]
            after = lines[expression.end_lineno - node.lineno + 1 :]
            segment = "\n".join([*before, render_docstring(cleaned_doc, "    "), *after])
    return segment


def starter_source(
    source: str,
    module: ast.Module,
    node: ast.FunctionDef,
    number: int,
    shared: str,
    documentation: str,
) -> str:
    title = documentation.splitlines()[0]
    header_parts = [title, shared]
    if number in EXTRA_CONTRACTS:
        header_parts.extend(["Дополнительный договор данных", EXTRA_CONTRACTS[number]])
    header_parts.append(
        "Работай с этой функцией. GIVEN-помощники можно вызывать, но нельзя изменять."
    )
    pieces = [render_docstring("\n\n".join(header_parts))]
    for dependency in starter_nodes(module, node):
        if isinstance(dependency, ast.FunctionDef) and dependency is not node:
            pieces.append("# GIVEN: готовый помощник для этой задачи.")
        pieces.append(
            node_source(source, dependency, documentation if dependency is node else None)
        )
    starter = "\n\n\n".join(pieces).rstrip() + "\n"
    parsed = ast.parse(starter)
    main_names = [
        item.name
        for item in parsed.body
        if isinstance(item, ast.FunctionDef) and item.name.startswith("task_")
    ]
    if main_names != [node.name]:
        raise ValueError(f"Unexpected entry points for XL-A{number:02d}: {main_names}")
    other_refs = {int(value) for value in re.findall(r"XL-A(\d{2})", starter)} - {number}
    if other_refs:
        raise ValueError(f"Unresolved task references in XL-A{number:02d}: {sorted(other_refs)}")
    return starter


def statement_source(
    number: int,
    group_number: int,
    group: Group,
    title: str,
    kind: str,
    shared: str,
    documentation: str,
) -> str:
    task_id = f"XL-A{number:02d}"
    level = "medium" if number <= 18 else "hard"
    tags = [group.domain, KINDS[kind]]
    frontmatter = [
        "---",
        f"id: {task_id}",
        f"title: {yaml_string(title)}",
        f"version: {yaml_string(VERSION)}",
        f"level: {level}",
        "tags: " + json.dumps(tags),
        f"folder: {group.folder}",
        "---",
    ]
    body = [
        f"# Задача {task_id}: {title}",
        f"**Блок:** XLA{group_number:02d} — {group.name}",
        f"**Сложность:** {level}",
        f"**Темы:** {', '.join(tags)}",
        "## Условие",
        f"**Формат работы:** {kind}",
        "### Общий договор данных",
        render_markdown(shared),
    ]
    if number in EXTRA_CONTRACTS:
        body.extend(["### Дополнительный договор данных", render_markdown(EXTRA_CONTRACTS[number])])
    body.extend(["### Задание", render_markdown("\n".join(documentation.splitlines()[1:]).strip())])
    return "\n".join(frontmatter) + "\n\n" + "\n\n".join(body) + "\n"


def catalog_outputs(source_root: Path = SOURCE_ROOT) -> dict[Path, str]:
    outputs: dict[Path, str] = {
        Path(
            "catalog.yaml"
        ): "schema_version: 1\nprojects:\n  - id: xl-a\n    path: projects/xl-a\n    enabled: true\n",
        Path("projects/xl-a/project.yaml"): (
            "id: xl-a\nname: XL-A product practice\n"
            f"description: {yaml_string('27 задач на продуктовую логику чатботов, агентов, игр и MMO')}\n"
            f"version: {yaml_string(VERSION)}\norder: 1\ndefault_locale: ru\n"
            "tags: [python, llm, agents, games, mmo]\nversion_policy: declare\n"
        ),
    }
    task_numbers: list[int] = []
    for group_number, group in enumerate(GROUPS, 1):
        source_path = source_root / group.folder / "student.py"
        source = source_path.read_text(encoding="utf-8-sig")
        module = ast.parse(source, filename=str(source_path))
        folder = Path("projects/xl-a/folders") / group.folder
        outputs[folder / "folder.yaml"] = (
            f"id: {group.folder}\ncode: XLA{group_number:02d}\nname: {yaml_string(group.name)}\n"
            f"description: {yaml_string('Продуктовая практика: ' + group.name.lower())}\n"
            f"order: {group_number}\nlevel: {'medium' if group_number <= 6 else 'hard'}\n"
        )
        for node in module.body:
            if not isinstance(node, ast.FunctionDef) or not TASK_RE.match(node.name):
                continue
            number = int(TASK_RE.match(node.name).group("number"))
            if not (group_number - 1) * 3 < number <= group_number * 3:
                raise ValueError(f"Unexpected task {node.name} in {group.folder}")
            documentation = task_documentation(node, number)
            title_match = TITLE_RE.match(documentation.splitlines()[0])
            if title_match is None or int(title_match.group("number")) != number:
                raise ValueError(f"Invalid task title for {node.name}")
            title = title_match.group("title").rstrip(".")
            kind = title_match.group("kind")
            shared = shared_contract(module, number)
            prefix = folder / f"task_xla{number:02d}"
            outputs[prefix.with_suffix(".md")] = statement_source(
                number, group_number, group, title, kind, shared, documentation
            )
            outputs[prefix.with_suffix(".student.py")] = starter_source(
                source, module, node, number, shared, documentation
            )
            task_numbers.append(number)
    if task_numbers != list(range(1, 28)):
        raise ValueError(f"Expected XL-A01 through XL-A27, got {task_numbers}")
    outputs[Path("README.txt")] = """XL-A — каталог задач Cogito

27 задач XL-A01…XL-A27, 9 тематических папок, версия 1.0.0.
Исходный учебный пакет сохранён в соседних 01_chat_context…09_agent_plans/student.py.

Из корня ego-trainer:
  python scripts/build_xl_a_catalog.py
  python scripts/build_xl_a_catalog.py --check
  uv run ego-server admin sync-tasks --from docs/tasks/XL-A/catalog

Команда sync-tasks импортирует этот каталог в настроенную БД сервера.
Для публикации в отдельном content-repo переносится весь каталог с catalog.yaml.

Нужна версия Cogito с явными стартерами <task>.student.py и дополнительными
полями @case: comparison="value", check_inputs_unchanged и check_result_isolated.
Без поддержки .student.py задачи на поиск бага и правки потеряют исходный код;
без новых полей тестов их загрузка или необходимые проверки недоступны.

Файлы .md, .student.py и YAML генерируются из оригинальных student.py.
Эталонные .solution.py и тестовые .tests.py создаются отдельно. Генератор их
не читает, не переписывает и ничего не удаляет. Изменения условий и стартеров
вносятся в исходный пакет, затем каталог строится заново. Общие договоры и
контекст прежних перекрёстных ссылок включены в каждую отдельную задачу.

Первые 18 задач — medium, последние 9 — hard. В каждой группе есть задачи
на поиск бага, расширение и новый код. Ошибки и pass в стартерах намеренные.
Рефакторинг XL-A25 дополнительно оценивается наставником: тесты проверяют
поведение и не определяют качество выделения помощников.
"""
    return outputs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="check generated files without writing"
    )
    args = parser.parse_args(argv)
    outputs = catalog_outputs()
    destination = SOURCE_ROOT / "catalog"
    changed: list[Path] = []
    for relative, text in outputs.items():
        path = destination / relative
        if path.is_file() and path.read_text(encoding="utf-8") == text:
            continue
        changed.append(relative)
        if not args.check:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8", newline="\n")
    if args.check and changed:
        print("Generated XL-A catalog is out of date:")
        for path in changed:
            print(f"  {path.as_posix()}")
        return 1
    action = "checked" if args.check else "generated"
    print(f"XL-A: {action} {len(outputs)} owned files for 27 tasks; {len(changed)} changed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
