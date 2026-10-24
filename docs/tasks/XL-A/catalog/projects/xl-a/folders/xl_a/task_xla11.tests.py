from ego.testing import case


@case(
    args=(
        [
            {"id": "a", "doc_id": "x", "text": "A", "score": 9, "tokens": 3},
            {"id": "b", "doc_id": "x", "text": "B", "score": 8, "tokens": 2},
            {"id": "c", "doc_id": "y", "text": "C", "score": 7, "tokens": 4},
        ],
        7,
        1,
    ),
    expected={"chunk_ids": ["a", "c"], "used_tokens": 7},
    description="Квота оставляет место другому документу",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        [
            {"id": "a", "doc_id": "x", "text": "A", "score": 9, "tokens": 3},
            {"id": "b", "doc_id": "x", "text": "B", "score": 8, "tokens": 2},
            {"id": "c", "doc_id": "y", "text": "C", "score": 7, "tokens": 4},
        ],
        2,
        1,
    ),
    expected={"chunk_ids": ["b"], "used_tokens": 2},
    description="Слишком большой фрагмент не расходует квоту документа",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        [
            {"id": "z", "doc_id": "x", "text": "Z", "score": 5, "tokens": 1},
            {"id": "b", "doc_id": "y", "text": "B", "score": 5, "tokens": 2},
            {"id": "a", "doc_id": "x", "text": "A", "score": 5, "tokens": 2},
        ],
        5,
        1,
    ),
    expected={"chunk_ids": ["a", "b"], "used_tokens": 4},
    description="При равенстве score выбор определяется id и квотой",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=([{"id": "a", "doc_id": "x", "text": "A", "score": 9, "tokens": 1}], 10, 0),
    expected={"chunk_ids": [], "used_tokens": 0},
    description="Нулевая квота запрещает любой выбор",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=([{"id": "a", "doc_id": "x", "text": "A", "score": 9, "tokens": 1}], 0, 2),
    expected={"chunk_ids": [], "used_tokens": 0},
    description="Нулевой бюджет",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=([], 9),
    expected={"chunk_ids": [], "used_tokens": 0},
    description="Пустой ввод и квота по умолчанию",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        [
            {"id": "a", "doc_id": "x", "text": "A", "score": 9, "tokens": 1},
            {"id": "b", "doc_id": "x", "text": "B", "score": 8, "tokens": 1},
            {"id": "c", "doc_id": "x", "text": "C", "score": 7, "tokens": 1},
            {"id": "d", "doc_id": "y", "text": "D", "score": 6, "tokens": 1},
        ],
        10,
    ),
    expected={"chunk_ids": ["a", "b", "d"], "used_tokens": 3},
    description="Квота по умолчанию равна двум",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        [
            {"id": "a", "doc_id": "x", "text": "A", "score": 4, "tokens": 4},
            {"id": "b", "doc_id": "y", "text": "B", "score": 3, "tokens": 3},
            {"id": "c", "doc_id": "z", "text": "C", "score": 2, "tokens": 1},
        ],
        5,
        8,
    ),
    expected={"chunk_ids": ["a", "c"], "used_tokens": 5},
    description="После заполнения части бюджета просмотр продолжается",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        [
            {"id": "b", "doc_id": "y", "text": "B", "score": -5, "tokens": 1},
            {"id": "a", "doc_id": "x", "text": "A", "score": -1, "tokens": 2},
        ],
        3,
        5,
    ),
    expected={"chunk_ids": ["a", "b"], "used_tokens": 3},
    description="Отрицательные оценки не являются фильтром",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        [
            {"id": "a", "doc_id": "x", "text": "A", "score": 5, "tokens": 8},
            {"id": "b", "doc_id": "x", "text": "B", "score": 4, "tokens": 7},
            {"id": "c", "doc_id": "x", "text": "C", "score": 3, "tokens": 2},
            {"id": "d", "doc_id": "y", "text": "D", "score": 2, "tokens": 3},
        ],
        5,
        1,
    ),
    expected={"chunk_ids": ["c", "d"], "used_tokens": 5},
    description="Несколько пропусков не мешают поздним фрагментам поместиться точно",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
def task_xla11_select_context(chunks, budget, max_per_doc=2): ...
