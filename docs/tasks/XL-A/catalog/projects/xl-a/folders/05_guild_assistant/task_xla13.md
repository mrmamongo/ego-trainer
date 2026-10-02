---
id: XL-A13
title: "проверить намерение и подготовить команду"
version: "1.0.0"
level: medium
tags: ["guild-assistant", "new"]
folder: 05_guild_assistant
---

# Задача XL-A13: проверить намерение и подготовить команду

**Блок:** XLA05 — Помощник гильдии

**Сложность:** medium

**Темы:** guild-assistant, new

## Условие

**Формат работы:** НОВЫЙ КОД

### Общий договор данных

Работаем с безопасной подготовкой и симуляцией игровых действий.
Все данные локальны: функция не обращается к сети, модели или игре.
Аргументы не меняются. Задачи независимы, а GIVEN-помощники можно
вызывать, но нельзя изменять.

### Задание

**Модельный вывод уже разобран в словарь, но его нельзя сразу выполнять:**
игрок мог назвать отсутствующего участника или событие. Проверь данные
и преобразуй названия в канонические ID. Здесь нет реального вызова игры.

**Аргументы:**

```text
raw={tool: строка, args: словарь}.
Допустимы create_event с title и capacity; join_event с member_name
и event_title. members=[{id,name}], events=[{id,title,capacity,
members:[member ID]}]. ID уникальны, имена — нет. Сравнение точное.
Названия из raw сначала strip(); регистр не меняй. Для имени или
названия события отсутствующее поле, None, значение не-строка или
пустая после strip() строка считаются *_empty. Записи каталога
гарантированно имеют строковые name/title и ID; у событий capacity
— целое >= 1, members — список ID.
```

Всегда верни {status:'ready' или 'rejected', command:..., errors:[...]}.
Для create_event сначала проверь title: пустая после strip() строка
даёт title_empty. Затем capacity: нужен int >= 1, bool не считается
целым; иначе invalid_capacity. Готовая команда содержит tool и args
с очищенным title и прежним capacity.
Если неверны оба поля, верни обе ошибки в указанном порядке.
Отсутствующий или нестроковый title тоже даёт title_empty.
Лишние поля args игнорируй: в готовую команду входят только описанные поля.
Для join_event сначала проверь участника, затем событие и собери обе
независимые ошибки поиска, если они есть. Пустые поля дают
member_name_empty / event_title_empty. Ноль совпадений —
unknown_member / unknown_event; больше одного — ambiguous_member /
ambiguous_event. При уникальных совпадениях проверь уже вступил ли
участник (already_joined), затем заполненность (event_full).
Готовые args — только member_id и event_id. Ошибки возвращай в этом
порядке; при отказе command=None. Неизвестный tool даёт ['unknown_tool'].

**Примеры:**

```python
members=[{"id":"m1","name":"Ира"}]; events=[]
raw={"tool":"create_event","args":{"title":"  Рейд  ","capacity":4}}
task_xla13_prepare_action(raw, members, events) == {
    "status":"ready","command":{"tool":"create_event",
    "args":{"title":"Рейд","capacity":4}},"errors":[]}
```

Второй пример: members=[{"id":"m1","name":"Ира"},
{"id":"m2","name":"Ира"}], events=[] и raw=
{"tool":"join_event","args":{"member_name":"Ира","event_title":"Луна"}}
дают {"status":"rejected","command":None,
"errors":["ambiguous_member","unknown_event"]}.
Третий пример: members=[{"id":"m1","name":"Ира"}], events=[
{"id":"e1","title":"Рейд","capacity":1,"members":["m2"]}];
join Ира в Рейд даёт rejected, command=None, errors=['event_full'].
Если участник уже в заполненном событии, ошибка только already_joined.
Используй given_find_matches для поиска. Входные данные не меняй.
