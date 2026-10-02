---
id: XL-A12
title: "собрать ответ с целостными источниками"
version: "1.0.0"
level: medium
tags: ["answer-sources", "new"]
folder: 04_answer_sources
---

# Задача XL-A12: собрать ответ с целостными источниками

**Блок:** XLA04 — Источники ответа

**Сложность:** medium

**Темы:** answer-sources, new

## Условие

**Формат работы:** НОВЫЙ КОД

### Общий договор данных

Работаем с поиском по документам: выдачей фрагментов, бюджетом контекста
и сборкой проверяемых ссылок. Входные списки и словари менять нельзя.
Каждая задача самостоятельна; GIVEN-помощники разрешено вызывать, но
менять их нельзя. Не нужны сеть, модель или сторонние библиотеки.

### Задание

Модель вернула текст и идентификаторы использованных фрагментов.
Прежде чем показывать ответ, проверь, что все ссылки существуют,
затем сгруппируй цитаты по документам. Эта функция проверяет только
целостность ссылок; истинность текста она определить не может.

**Аргументы:**

```text
model_output={text: непустая строка, used_chunk_ids: список строк}.
context_chunks — фрагменты с уникальными id, doc_id, title, text.
У всех фрагментов одного документа title одинаков.
```

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

**Пример:**

```python
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
```

Второй пример: output={"text":"Ответ.","used_chunk_ids":["c","x","x"]}
даёт {"status":"invalid_sources","answer":"","sources":[],
"errors":["unknown_chunk:x"]}; пустые ссылки дают needs_sources,
answer='', sources=[], errors=['no_sources'].
text гарантированно непустой; отдельная проверка этого условия не нужна.
Не меняй вход.
