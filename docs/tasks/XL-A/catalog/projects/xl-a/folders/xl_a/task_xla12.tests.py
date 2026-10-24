from ego.testing import case


@case(
    args=(
        {"text": "Ответ.", "used_chunk_ids": ["b", "a", "c", "b"]},
        [
            {"id": "a", "doc_id": "d1", "title": "Памятка", "text": "A"},
            {"id": "b", "doc_id": "d1", "title": "Памятка", "text": "B"},
            {"id": "c", "doc_id": "d2", "title": "Закон", "text": "C"},
        ],
    ),
    expected={
        "status": "ok",
        "answer": "Ответ.",
        "sources": [
            {"doc_id": "d1", "title": "Памятка", "chunk_ids": ["b", "a"]},
            {"doc_id": "d2", "title": "Закон", "chunk_ids": ["c"]},
        ],
        "errors": [],
    },
    description="Группировка по документу с удалением повторных ссылок",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {"text": "Ответ.", "used_chunk_ids": ["c", "x", "x"]},
        [{"id": "c", "doc_id": "d2", "title": "Закон", "text": "C"}],
    ),
    expected={
        "status": "invalid_sources",
        "answer": "",
        "sources": [],
        "errors": ["unknown_chunk:x"],
    },
    description="Одна неизвестная ссылка отклоняет весь ответ и не дублирует ошибку",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=({"text": "Нужны ссылки.", "used_chunk_ids": []}, []),
    expected={"status": "needs_sources", "answer": "", "sources": [], "errors": ["no_sources"]},
    description="Нет ни одной использованной ссылки",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=({"text": "Text", "used_chunk_ids": ["z", "a", "z", "b", "a"]}, []),
    expected={
        "status": "invalid_sources",
        "answer": "",
        "sources": [],
        "errors": ["unknown_chunk:z", "unknown_chunk:a", "unknown_chunk:b"],
    },
    description="Неизвестные ссылки перечисляются по первому использованию",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {"text": "Text", "used_chunk_ids": ["c", "b", "a", "d"]},
        [
            {"id": "a", "doc_id": "d1", "title": "One", "text": "A"},
            {"id": "b", "doc_id": "d1", "title": "One", "text": "B"},
            {"id": "c", "doc_id": "d2", "title": "Two", "text": "C"},
            {"id": "d", "doc_id": "d2", "title": "Two", "text": "D"},
        ],
    ),
    expected={
        "status": "ok",
        "answer": "Text",
        "sources": [
            {"doc_id": "d2", "title": "Two", "chunk_ids": ["c", "d"]},
            {"doc_id": "d1", "title": "One", "chunk_ids": ["b", "a"]},
        ],
        "errors": [],
    },
    description="Порядок документов задают ссылки, а не каталог",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {"text": "Text", "used_chunk_ids": ["a", "a", "a"]},
        [{"id": "a", "doc_id": "d", "title": "Only", "text": "A"}],
    ),
    expected={
        "status": "ok",
        "answer": "Text",
        "sources": [{"doc_id": "d", "title": "Only", "chunk_ids": ["a"]}],
        "errors": [],
    },
    description="Многократная ссылка остаётся единственной в документе",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {"text": "Text", "used_chunk_ids": ["b", "a"]},
        [
            {"id": "a", "doc_id": "d1", "title": "Same title", "text": "A"},
            {"id": "b", "doc_id": "d2", "title": "Same title", "text": "B"},
        ],
    ),
    expected={
        "status": "ok",
        "answer": "Text",
        "sources": [
            {"doc_id": "d2", "title": "Same title", "chunk_ids": ["b"]},
            {"doc_id": "d1", "title": "Same title", "chunk_ids": ["a"]},
        ],
        "errors": [],
    },
    description="Одинаковые названия не объединяют разные документы",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {"text": "Do not display", "used_chunk_ids": ["missing", "a", "later"]},
        [{"id": "a", "doc_id": "d", "title": "Known", "text": "A"}],
    ),
    expected={
        "status": "invalid_sources",
        "answer": "",
        "sources": [],
        "errors": ["unknown_chunk:missing", "unknown_chunk:later"],
    },
    description="При нескольких ошибках ни текст, ни известные источники не показываются",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {"text": "  Текст\nбез очистки  ", "used_chunk_ids": ["a"]},
        [{"id": "a", "doc_id": "d", "title": "Title", "text": "Source"}],
    ),
    expected={
        "status": "ok",
        "answer": "  Текст\nбез очистки  ",
        "sources": [{"doc_id": "d", "title": "Title", "chunk_ids": ["a"]}],
        "errors": [],
    },
    description="Текст ответа сохраняется дословно",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {"text": "Text", "used_chunk_ids": ["b"]},
        [
            {"id": "a", "doc_id": "d1", "title": "Unused", "text": "A"},
            {"id": "b", "doc_id": "d2", "title": "Used", "text": "B"},
            {"id": "c", "doc_id": "d2", "title": "Used", "text": "C"},
        ],
    ),
    expected={
        "status": "ok",
        "answer": "Text",
        "sources": [{"doc_id": "d2", "title": "Used", "chunk_ids": ["b"]}],
        "errors": [],
    },
    description="Неиспользованные документы и фрагменты не попадают в sources",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
def task_xla12_assemble_answer(model_output, context_chunks): ...
