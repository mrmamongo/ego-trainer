"""Задача J8: Memory compaction — сжать историю в summary

Блок: XL-K — Агенты и тул-коллы
Сложность: hard
Тип: написать новый код
Темы: memory, compaction, summarization, агенты

== УСЛОВИЕ ==

У агента длинная история сообщений. Нужно сжать её в один summary,
сохраняя ключевые факты.

Алгоритм:
  1) Разбить history на группы по group_size сообщений.
  2) Каждую группу сжать в одну строку: "<role>: <first 30 chars of content>..."
     (если content длиннее 30 символов — обрезать и добавить "...").
  3) Соединить все строки через " | ".

== АРГУМЕНТЫ ==

- history — список dict: [{"role": "user"|"assistant", "content": str}, ...]
- group_size — целое, сколько сообщений в одной группе

== ВОЗВРАЩАЕТ ==

Строку — summary всей истории.

== ПРАВИЛА ==

- Группы идут подряд, последняя может быть короче group_size.
- Формат сжатия: "user: Hello, how are you?..." (роль + первые 30 символов).
- Если content <= 30 символов — без "...".
- Пустой history → пустая строка.

== ПРИМЕР ==

  compact_memory([
      {"role": "user", "content": "What is the capital of France?"},
      {"role": "assistant", "content": "The capital of France is Paris."},
      {"role": "user", "content": "And Germany?"},
  ], 2)
  # -> "user: What is the capital of France?... | assistant: The capital of France is Paris... | user: And Germany?"
"""


def task_xlj8_compact_memory(history, group_size):
    # ТВОЙ КОД ЗДЕСЬ
    pass
