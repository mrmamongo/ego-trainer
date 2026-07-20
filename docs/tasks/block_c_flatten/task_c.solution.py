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
