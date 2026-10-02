"""Задача J1: Парсинг tool-call строки

Блок: XL-K — Агенты и тул-коллы
Сложность: easy
Тип: написать новый код
Темы: tool-call, парсинг, агенты, LLM

== УСЛОВИЕ ==

LLM-агент вызывает инструменты через специальные строки вида:
  CALL: get_weather {"city": "Moscow", "units": "celsius"}

Формат: префикс "CALL: ", имя тула (без пробелов), пробел, JSON-объект.
Твоя задача — распарсить строку и вернуть dict:
  {"name": "get_weather", "args": {"city": "Moscow", "units": "celsius"}}

== АРГУМЕНТЫ ==

- line — строка вида "CALL: <name> <json>" (может быть невалидной)

== ВОЗВРАЩАЕТ ==

Dict {"name": str, "args": dict} при успешном парсинге.
None, если строка не соответствует формату или JSON невалиден.

== ПРАВИЛА ==

- Имя тула — всё между "CALL: " и первым пробелом.
- args — результат json.loads на остатке строки (должен быть dict).
- Строка без префикса "CALL: " → None.
- Невалидный JSON → None.

== ПРИМЕР ==

  parse_tool_call('CALL: search {"q": "python"}')
  # -> {"name": "search", "args": {"q": "python"}}

  parse_tool_call("CALL: bad {not json}")
  # -> None
"""

def task_xlj1_parse_tool_call(line):
    # ТВОЙ КОД ЗДЕСЬ
    pass
