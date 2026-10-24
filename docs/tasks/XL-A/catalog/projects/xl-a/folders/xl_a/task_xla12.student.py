"""
XL-A12. НОВЫЙ КОД — собрать ответ с целостными источниками.

Здесь мы делаем поиск по документам и ответ с ссылками на источники:
отбираем найденные текстовые фрагменты, укладываем их в бюджет контекста
и собираем проверяемые ссылки для пользователя.
Входные списки и словари менять нельзя.
Задачи независимы друг от друга; готовые функции (GIVEN) можно вызывать,
но менять их нельзя. Сеть, модель и сторонние библиотеки не нужны.

Работай с этой функцией. GIVEN-помощники можно вызывать, но нельзя изменять.
"""


# GIVEN: готовый помощник для этой задачи.


def given_index_chunks(chunks):
    """GIVEN: индекс фрагментов по уникальному идентификатору."""
    return {chunk["id"]: chunk for chunk in chunks}


# GIVEN: готовый помощник для этой задачи.


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

        Модель вернула текст ответа и идентификаторы фрагментов, на которые
        она ссылается. Прежде чем показать ответ пользователю, убедись, что все
        ссылки существуют, и сгруппируй цитаты по документам. Эта функция
        проверяет только целостность ссылок; истинность текста она определить
        не может.

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
        text гарантированно непустой; отдельно проверять это условие не нужно.
        Не меняй вход.
        """
    pass
