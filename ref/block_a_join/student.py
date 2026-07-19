#!/usr/bin/env python3
"""
student.py — ТВОЙ файл. Пиши решения здесь.

Как работать:
    1. Удали `pass` и напиши код
    2. Запускай проверку:  python checker.py
    3. Смотри результат: ✅ (зачёт) или ❌ (не зачёт)

Правила:
    - Не меняй НАЗВАНИЯ функций
    - Не меняй АРГУМЕНТЫ функций
    - return результат, не print
"""


def task_a_merge_runs(runs, chunks, metrics):
    """
    Задача A: Сборка из разных источников (join / merge)

    У тебя три списка словарей — это ответы от трёх разных API.
    Нужно собрать их в один словарь по ключу run_id.

    Аргументы:
        runs    — список словарей: [{"run_id": "r1", "model": "gpt-4o", "prompt": "..."}, ...]
        chunks  — список словарей: [{"run_id": "r1", "chunk_id": "c1", "text": "..."}, ...]
        metrics — список словарей: [{"run_id": "r1", "tokens_in": 100, "tokens_out": 50}, ...]

    Верни:
        Словарь:
        {
            "r1": {
                "model": "gpt-4o",
                "prompt": "...",
                "chunks": [
                    {"chunk_id": "c1", "text": "..."},
                    {"chunk_id": "c2", "text": "..."},
                ],
                "metrics": {"tokens_in": 100, "tokens_out": 50}
            },
            "r2": { ... }
        }

    Правила:
        - chunks кладутся в список внутри агента, БЕЗ поля run_id
        - metrics кладутся как словарь, БЕЗ поля run_id
        - runs дают model и prompt
        - Если у run_id нет chunks — список пустой []
        - Если у run_id нет metrics — словарь пустой {}
        - Порядок run_id — как в списке runs
    """
    pass
