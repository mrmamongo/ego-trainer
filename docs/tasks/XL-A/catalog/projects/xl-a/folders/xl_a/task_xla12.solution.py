def given_index_chunks(chunks):
    """GIVEN: индекс фрагментов по уникальному идентификатору."""
    return {chunk["id"]: chunk for chunk in chunks}


def given_unique_in_order(values):
    """GIVEN: сохранить первое появление каждого значения."""
    seen = set()
    result = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def task_xla12_assemble_answer(model_output, context_chunks):
    indexed = given_index_chunks(context_chunks)
    used_ids = given_unique_in_order(model_output["used_chunk_ids"])
    errors = [f"unknown_chunk:{chunk_id}" for chunk_id in used_ids if chunk_id not in indexed]
    if errors:
        return {"status": "invalid_sources", "answer": "", "sources": [], "errors": errors}
    if not used_ids:
        return {"status": "needs_sources", "answer": "", "sources": [], "errors": ["no_sources"]}
    sources = []
    by_document = {}
    for chunk_id in used_ids:
        chunk = indexed[chunk_id]
        doc_id = chunk["doc_id"]
        if doc_id not in by_document:
            source = {"doc_id": doc_id, "title": chunk["title"], "chunk_ids": []}
            by_document[doc_id] = source
            sources.append(source)
        by_document[doc_id]["chunk_ids"].append(chunk_id)
    return {"status": "ok", "answer": model_output["text"], "sources": sources, "errors": []}
