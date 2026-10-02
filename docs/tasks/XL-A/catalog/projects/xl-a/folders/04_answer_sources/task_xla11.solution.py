def task_xla11_select_context(chunks, budget, max_per_doc=2):
    selected = []
    used = 0
    per_document = {}
    ordered = sorted(chunks, key=lambda chunk: (-chunk["score"], chunk["id"]))
    for chunk in ordered:
        doc_id = chunk["doc_id"]
        if per_document.get(doc_id, 0) >= max_per_doc:
            continue
        if used + chunk["tokens"] > budget:
            continue
        selected.append(chunk["id"])
        used += chunk["tokens"]
        per_document[doc_id] = per_document.get(doc_id, 0) + 1
    return {"chunk_ids": selected, "used_tokens": used}
