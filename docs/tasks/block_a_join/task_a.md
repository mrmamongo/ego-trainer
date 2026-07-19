# Задача A: Сборка из разных источников

**Блок:** A — Join/merge
**Сложность:** hard
**Темы:** join, index_by_key, merge_sources

## Условие

У тебя три списка словарей — это ответы от трёх разных API. Нужно собрать их в один словарь по ключу `run_id`, объединив для каждого прогона его модель и промпт (из `runs`), список чанков (из `chunks`) и метрики (из `metrics`).

## Аргументы

- `runs` — список словарей: `[{"run_id": "r1", "model": "gpt-4o", "prompt": "..."}, ...]`
- `chunks` — список словарей: `[{"run_id": "r1", "chunk_id": "c1", "text": "..."}, ...]`
- `metrics` — список словарей: `[{"run_id": "r1", "tokens_in": 100, "tokens_out": 50}, ...]`

## Возвращает

Словарь, сгруппированный по `run_id`:

```python
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
```

## Правила

- chunks кладутся в список внутри агента, БЕЗ поля `run_id`
- metrics кладутся как словарь, БЕЗ поля `run_id`
- runs дают `model` и `prompt`
- Если у `run_id` нет chunks — список пустой `[]`
- Если у `run_id` нет metrics — словарь пустой `{}`
- Порядок `run_id` — как в списке `runs`

## Пример

```python
runs = [
    {"run_id": "r1", "model": "gpt-4o", "prompt": "Parse invoice #123"},
    {"run_id": "r2", "model": "claude-3", "prompt": "Summarize article"},
]
chunks = [
    {"run_id": "r1", "chunk_id": "c1", "text": "Found 3 line items"},
    {"run_id": "r1", "chunk_id": "c2", "text": "Total amount: $450"},
    {"run_id": "r2", "chunk_id": "c3", "text": "The article discusses..."},
]
metrics = [
    {"run_id": "r1", "tokens_in": 120, "tokens_out": 85},
]

task_a_merge_runs(runs, chunks, metrics)
# {
#     "r1": {
#         "model": "gpt-4o",
#         "prompt": "Parse invoice #123",
#         "chunks": [
#             {"chunk_id": "c1", "text": "Found 3 line items"},
#             {"chunk_id": "c2", "text": "Total amount: $450"},
#         ],
#         "metrics": {"tokens_in": 120, "tokens_out": 85}
#     },
#     "r2": {
#         "model": "claude-3",
#         "prompt": "Summarize article",
#         "chunks": [
#             {"chunk_id": "c3", "text": "The article discusses..."},
#         ],
#         "metrics": {}
#     }
# }
```

<details>
<summary>Эталонное решение</summary>

```python
def task_a_merge_runs(runs, chunks, metrics):
    """Правильный ответ."""
    # Шаг 1: Индексируем чанки по run_id
    chunks_by_run = {}
    for c in chunks:
        rid = c["run_id"]
        if rid not in chunks_by_run:
            chunks_by_run[rid] = []
        # Кладём без run_id
        chunks_by_run[rid].append({
            "chunk_id": c["chunk_id"],
            "text": c["text"],
        })

    # Шаг 2: Индексируем метрики по run_id
    metrics_by_run = {}
    for m in metrics:
        rid = m["run_id"]
        metrics_by_run[rid] = {
            "tokens_in": m["tokens_in"],
            "tokens_out": m["tokens_out"],
        }

    # Шаг 3: Собираем итоговый словарь
    result = {}
    for r in runs:
        rid = r["run_id"]
        result[rid] = {
            "model": r["model"],
            "prompt": r["prompt"],
            "chunks": chunks_by_run.get(rid, []),
            "metrics": metrics_by_run.get(rid, {}),
        }

    return result
```

</details>
