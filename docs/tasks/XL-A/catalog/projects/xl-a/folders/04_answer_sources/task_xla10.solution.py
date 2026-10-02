def task_xla10_make_citations(chunks, min_score):
    selected = sorted(
        (chunk for chunk in chunks if chunk["score"] >= min_score),
        key=lambda chunk: (-chunk["score"], chunk["id"]),
    )
    return [
        {
            "label": f"[{index + 1}]",
            "chunk_id": chunk["id"],
            "doc_id": chunk["doc_id"],
            "title": chunk["title"],
            "text": chunk["text"],
        }
        for index, chunk in enumerate(selected)
    ]
