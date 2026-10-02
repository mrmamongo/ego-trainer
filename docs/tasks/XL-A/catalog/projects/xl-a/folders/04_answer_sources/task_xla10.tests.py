from ego.testing import case


@case(
    args=(
        [
            {"id": "z", "doc_id": "manual", "title": "Guide", "text": "Five days", "score": 8},
            {"id": "a", "doc_id": "law", "title": "Rule", "text": "Three days", "score": 10},
            {"id": "b", "doc_id": "blog", "title": "Note", "text": "Nine days", "score": 2},
        ],
        5,
    ),
    expected=[
        {"label": "[1]", "chunk_id": "a", "doc_id": "law", "title": "Rule", "text": "Three days"},
        {
            "label": "[2]",
            "chunk_id": "z",
            "doc_id": "manual",
            "title": "Guide",
            "text": "Five days",
        },
    ],
    description="После сортировки и фильтра все поля ссылки принадлежат выбранному фрагменту",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        [
            {"id": "b", "doc_id": "d2", "title": "Second", "text": "B", "score": 4},
            {"id": "a", "doc_id": "d1", "title": "First", "text": "A", "score": 4},
        ],
        4,
    ),
    expected=[
        {"label": "[1]", "chunk_id": "a", "doc_id": "d1", "title": "First", "text": "A"},
        {"label": "[2]", "chunk_id": "b", "doc_id": "d2", "title": "Second", "text": "B"},
    ],
    description="Равные оценки разрешаются по id с сохранением текста и документа",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=([{"id": "q", "doc_id": "d", "title": "T", "text": "X", "score": 4}], 4),
    expected=[{"label": "[1]", "chunk_id": "q", "doc_id": "d", "title": "T", "text": "X"}],
    description="Оценка на пороге включается",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=([], 0),
    expected=[],
    description="Пустая выдача поиска",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=([{"id": "a", "doc_id": "d", "title": "T", "text": "A", "score": 3}], 4),
    expected=[],
    description="Все фрагменты ниже порога",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        [
            {"id": "b", "doc_id": "d2", "title": "B", "text": "minus two", "score": -2},
            {"id": "a", "doc_id": "d1", "title": "A", "text": "zero", "score": 0},
            {"id": "c", "doc_id": "d3", "title": "C", "text": "minus three", "score": -3},
        ],
        -2,
    ),
    expected=[
        {"label": "[1]", "chunk_id": "a", "doc_id": "d1", "title": "A", "text": "zero"},
        {"label": "[2]", "chunk_id": "b", "doc_id": "d2", "title": "B", "text": "minus two"},
    ],
    description="Отрицательные оценки и отрицательный порог",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        [
            {"id": "drop", "doc_id": "old", "title": "Old", "text": "Skip", "score": 1},
            {"id": "keep", "doc_id": "new", "title": "New", "text": "Keep", "score": 7},
        ],
        5,
    ),
    expected=[
        {"label": "[1]", "chunk_id": "keep", "doc_id": "new", "title": "New", "text": "Keep"}
    ],
    description="Удаление первого элемента не подменяет метаданные оставшегося",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        [
            {"id": "a", "doc_id": "same", "title": "Book", "text": "Chapter one", "score": 1},
            {"id": "b", "doc_id": "same", "title": "Book", "text": "Chapter two", "score": 9},
        ],
        0,
    ),
    expected=[
        {"label": "[1]", "chunk_id": "b", "doc_id": "same", "title": "Book", "text": "Chapter two"},
        {"label": "[2]", "chunk_id": "a", "doc_id": "same", "title": "Book", "text": "Chapter one"},
    ],
    description="У одного документа могут быть разные тексты фрагментов",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        [
            {"id": "a", "doc_id": "d1", "title": "A", "text": "1", "score": 3},
            {"id": "b", "doc_id": "d2", "title": "B", "text": "2", "score": 2},
            {"id": "c", "doc_id": "d3", "title": "C", "text": "3", "score": 1},
        ],
        0,
    ),
    expected=[
        {"label": "[1]", "chunk_id": "a", "doc_id": "d1", "title": "A", "text": "1"},
        {"label": "[2]", "chunk_id": "b", "doc_id": "d2", "title": "B", "text": "2"},
        {"label": "[3]", "chunk_id": "c", "doc_id": "d3", "title": "C", "text": "3"},
    ],
    description="Нумерация всех прошедших фрагментов непрерывна",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        [
            {
                "id": "я",
                "doc_id": "док",
                "title": " Памятка ",
                "text": " Первая строка\nВторая ",
                "score": 1,
            }
        ],
        1,
    ),
    expected=[
        {
            "label": "[1]",
            "chunk_id": "я",
            "doc_id": "док",
            "title": " Памятка ",
            "text": " Первая строка\nВторая ",
        }
    ],
    description="Название и текст возвращаются без очистки пробелов",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
def task_xla10_make_citations(chunks, min_score): ...
