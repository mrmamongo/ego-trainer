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
