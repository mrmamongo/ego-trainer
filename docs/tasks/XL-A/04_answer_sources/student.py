"""XL-A / 04. Источники ответа — задачи XL-A10, XL-A11, XL-A12.

Работаем с поиском по документам: выдачей фрагментов, бюджетом контекста
и сборкой проверяемых ссылок. Входные списки и словари менять нельзя.
Каждая задача самостоятельна; GIVEN-помощники разрешено вызывать, но
менять их нельзя. Не нужны сеть, модель или сторонние библиотеки.
"""


def task_xla10_make_citations(chunks, min_score):
    """
    XL-A10. НАЙТИ БАГ — ссылки ведут не к тем фрагментам.

    Поиск уже вернул подходящие текстовые фрагменты, но интерфейс ответа
    показывает пользователю подписи источников. Найди и исправь дефект,
    из-за которого подпись или цитируемый текст может не соответствовать
    фрагменту, который действительно прошёл порог и занял это место.

    Аргументы:
        chunks — фрагменты с уникальным id и полями doc_id, title, text,
                 score; score — целое число релевантности.
        min_score — целый порог включения, равный ему score подходит.

    Договор:
        Оставь только фрагменты с score >= min_score. Упорядочь их по
        убыванию score, а при равенстве — по возрастанию id. Для каждого
        выбранного элемента верни словарь {label, chunk_id, doc_id,
        title, text}; label — последовательные строки '[1]', '[2]' и т.д.
        Все поля описывают один и тот же исходный фрагмент. Не меняй вход.
        Если ничего не прошло фильтр, верни [].

    Пример:
        chunks = [
            {"id": "z", "doc_id": "manual", "title": "Руководство", "text": "Срок 5 дней", "score": 8},
            {"id": "a", "doc_id": "law", "title": "Правило", "text": "Срок 3 дня", "score": 10},
            {"id": "b", "doc_id": "blog", "title": "Заметка", "text": "Срок 9 дней", "score": 2},
        ]
        task_xla10_make_citations(chunks, 5) == [
            {"label": "[1]", "chunk_id": "a", "doc_id": "law", "title": "Правило", "text": "Срок 3 дня"},
            {"label": "[2]", "chunk_id": "z", "doc_id": "manual", "title": "Руководство", "text": "Срок 5 дней"},
        ]
        task_xla10_make_citations(chunks, 11) == []
        При min_score=0 включатся все три, b идёт последним.
    Второй пример: chunks=[{"id":"q","doc_id":"d","title":"T",
    "text":"X","score":4}], min_score=4 даёт
    [{"label":"[1]","chunk_id":"q","doc_id":"d","title":"T","text":"X"}].

    Проверь также пустой список, равные оценки и порог ровно score.
    Сдай исправление, кратко опиши причину и пример, который ловит дефект.
    Не подменяй отсутствующие поля выдуманными значениями.
    """
    selected = [chunk for chunk in chunks if chunk["score"] >= min_score]
    selected.sort(key=lambda chunk: (-chunk["score"], chunk["id"]))
    return [
        {
            "label": f"[{i + 1}]",
            "chunk_id": chunk["id"],
            "doc_id": chunks[i]["doc_id"],
            "title": chunks[i]["title"],
            "text": chunks[i]["text"],
        }
        for i, chunk in enumerate(selected)
    ]


def task_xla11_select_context(chunks, budget, max_per_doc=2):
    """
    XL-A11. ПРАВКИ — ограничить число фрагментов одного документа.

    Текущая версия укладывает найденные фрагменты в лимит токенов. Теперь
    один длинный документ не должен вытеснять остальные источники.

    Аргументы:
        chunks — словари с уникальным id, doc_id, text, score и tokens.
        score — целое число; tokens — положительное целое число.
        budget и max_per_doc — целые числа не меньше нуля.

    Новое правило:
        Рассматривай фрагменты по score от большего к меньшему, затем по
        id от меньшего к большему. Если у документа уже выбрано
        max_per_doc фрагментов, пропусти следующий фрагмент этого
        документа. Иначе добавь его целиком, только если он помещается в
        оставшийся бюджет. Непоместившийся фрагмент пропусти и продолжай
        просмотр. Счётчик документа увеличивается только при выборе.
        При max_per_doc=0 верни пустой выбор.

    Верни прежний формат: {"chunk_ids": [...], "used_tokens": N}.
    chunk_ids идут в порядке выбора, used_tokens — сумма их tokens.
    Пример:
        chunks = [
            {"id":"a", "doc_id":"x", "text":"A", "score":9, "tokens":3},
            {"id":"b", "doc_id":"x", "text":"B", "score":8, "tokens":2},
            {"id":"c", "doc_id":"y", "text":"C", "score":7, "tokens":4},
        ]
        task_xla11_select_context(chunks, 7, max_per_doc=1) == {
            "chunk_ids": ["a", "c"], "used_tokens": 7}
        task_xla11_select_context(chunks, 2, max_per_doc=1) == {
            "chunk_ids": ["b"], "used_tokens": 2}
    Здесь a не помещается и пропускается; b затем помещается. При
    max_per_doc=0 результат {"chunk_ids": [], "used_tokens": 0}.
    Второй пример: один фрагмент id='r', doc_id='x', score=5, tokens=2;
    при budget=2 и max_per_doc=2 ответ
    {"chunk_ids": ["r"], "used_tokens": 2}. При пустом вводе ответ пустой.

    Когда квота не ограничивает выбор, сохрани прежнюю жадную логику:
    сортировку, неделимость фрагментов и продолжение после пропуска
    слишком большого элемента. Вход не меняй.
    Проверь пустой ввод, равные score и несколько документов.
    """
    ordered = sorted(chunks, key=lambda chunk: (-chunk["score"], chunk["id"]))
    selected = []
    used = 0
    for chunk in ordered:
        if used + chunk["tokens"] <= budget:
            selected.append(chunk["id"])
            used += chunk["tokens"]
    return {"chunk_ids": selected, "used_tokens": used}


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
    """
    XL-A12. НОВЫЙ КОД — собрать ответ с целостными источниками.

    Модель вернула текст и идентификаторы использованных фрагментов.
    Прежде чем показывать ответ, проверь, что все ссылки существуют,
    затем сгруппируй цитаты по документам. Эта функция проверяет только
    целостность ссылок; истинность текста она определить не может.

    Аргументы:
        model_output={text: непустая строка, used_chunk_ids: список строк}.
        context_chunks — фрагменты с уникальными id, doc_id, title, text.
        У всех фрагментов одного документа title одинаков.

    Обязательно используй given_index_chunks и given_unique_in_order.
    Повторный ID в used_chunk_ids учитывай один раз, при первом появлении.
    Если хотя бы один уникальный ID неизвестен, верни status='invalid_sources',
    answer='', sources=[], errors со строками unknown_chunk:<id> в порядке
    первого появления неизвестных ID. В прочем случае, если ссылок нет,
    верни status='needs_sources', пустые answer/sources и errors=['no_sources'].
    Иначе верни status='ok', answer из model_output, errors=[], а sources —
    список {doc_id,title,chunk_ids}. Документы и ID внутри каждого документа
    расположи по первому появлению ссылки. Во всех случаях ключи результата
    ровно status, answer, sources, errors.

    Пример:
        context = [
            {"id":"a", "doc_id":"d1", "title":"Памятка", "text":"..."},
            {"id":"b", "doc_id":"d1", "title":"Памятка", "text":"..."},
            {"id":"c", "doc_id":"d2", "title":"Закон", "text":"..."},
        ]
        output = {"text":"Ответ.", "used_chunk_ids":["b","a","c","b"]}
        task_xla12_assemble_answer(output, context) == {
            "status":"ok", "answer":"Ответ.",
            "sources":[{"doc_id":"d1","title":"Памятка","chunk_ids":["b","a"]},
                       {"doc_id":"d2","title":"Закон","chunk_ids":["c"]}],
            "errors":[]}
    Второй пример: output={"text":"Ответ.","used_chunk_ids":["c","x","x"]}
    даёт {"status":"invalid_sources","answer":"","sources":[],
    "errors":["unknown_chunk:x"]}; пустые ссылки дают needs_sources,
    answer='', sources=[], errors=['no_sources'].
    text гарантированно непустой; отдельная проверка этого условия не нужна.
    Не меняй вход.
    """
    pass
