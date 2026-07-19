# Задача C: Денормализация «для фронта» (flatten)

**Блок:** C — Flatten
**Сложность:** hard
**Темы:** flatten, denormalize, nested_to_table

## Условие

У тебя есть словарь run'ов, где каждый run содержит список `chunks`. Фронт хочет плоскую таблицу — по одной строке на каждый chunk, причём каждая строка должна включать поля из родительского run. Верни денормализованный список строк.

## Аргументы

- `runs` — словарь вида `{"r1": {"model": "gpt-4o", "prompt": "Parse invoice", "chunks": [...]}, "r2": {...}}`, где каждый run содержит поля `model`, `prompt` и список словарей `chunks` с ключами `chunk_id`, `text`, `timestamp` и др.

## Возвращает

Список словарей (плоская таблица) — по одной строке на каждый chunk. Каждая строка содержит `run_id`, `model` из родительского run, `chunk_id`, `chunk_text` (переименованный `text`) и остальные ключи chunk'а как есть.

## Правила

- Каждая строка содержит `run_id`, `model` из родительского run
- Ключ `text` из chunk переименовывается в `chunk_text`
- Остальные ключи из chunk копируются как есть (`timestamp` и т.д.)
- Порядок: как в словаре `runs`, внутри run — как в списке `chunks`
- Ключ `prompt` из run НЕ попадает в результат
- Если у run нет `chunks` — он не даёт строк вообще
- Если `chunks` пустой список `[]` — нет строк

## Пример

```python
runs = {
    "r1": {
        "model": "gpt-4o",
        "prompt": "Parse invoice",
        "chunks": [
            {"chunk_id": "c1", "text": "Found items", "timestamp": "10:00:01"},
            {"chunk_id": "c2", "text": "Total $450", "timestamp": "10:00:02"},
        ]
    },
    "r2": {
        "model": "claude-3-opus",
        "prompt": "Summarize report",
        "chunks": [
            {"chunk_id": "c3", "text": "Q2 revenue +15%", "timestamp": "10:01:01"},
        ]
    }
}

task_c_flatten(runs)
# [
#     {
#         "run_id": "r1",
#         "model": "gpt-4o",
#         "chunk_id": "c1",
#         "chunk_text": "Found items",
#         "timestamp": "10:00:01"
#     },
#     {
#         "run_id": "r1",
#         "model": "gpt-4o",
#         "chunk_id": "c2",
#         "chunk_text": "Total $450",
#         "timestamp": "10:00:02"
#     },
#     {
#         "run_id": "r2",
#         "model": "claude-3-opus",
#         "chunk_id": "c3",
#         "chunk_text": "Q2 revenue +15%",
#         "timestamp": "10:01:01"
#     }
# ]
```

<details>
<summary>Эталонное решение</summary>

```python
def task_c_flatten(runs):
    """Правильный ответ."""
    result = []
    for run_id, run_data in runs.items():
        model = run_data["model"]
        for chunk in run_data.get("chunks", []):
            row = {
                "run_id": run_id,
                "model": model,
                "chunk_id": chunk["chunk_id"],
                "chunk_text": chunk["text"],
            }
            # Копируем остальные ключи из chunk (кроме text и chunk_id)
            for key, value in chunk.items():
                if key not in ("text", "chunk_id"):
                    row[key] = value
            result.append(row)
    return result
```

</details>
