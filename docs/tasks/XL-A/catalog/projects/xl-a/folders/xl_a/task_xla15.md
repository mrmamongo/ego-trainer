---
id: XL-A15
title: "показать последствие до применения"
version: "1.1.0"
level: medium
tags: ["guild-assistant", "modify"]
folder: xl_a
---

# Задача XL-A15: показать последствие до применения

**История:** XLA05 — Помощник гильдии

**Сложность:** medium

**Темы:** guild-assistant, modify

## Условие

**Формат работы:** ПРАВКИ

### Общий договор данных

Здесь мы безопасно готовим и проигрываем игровые действия: сначала
проверяем, что игрок имел в виду, а потом показываем (или применяем)
результат — без риска что-то сломать в игре.
Все данные локальные: функция не обращается к сети, модели или самой игре.
Аргументы не меняются. Задачи независимы друг от друга, а готовые
функции (GIVEN) можно вызывать, но нельзя изменять.

### Дополнительный договор данных

```text
Состояние гильдии и формат команд:
    state = {"events": [{"id": "e1", "title": "Рейд", "capacity": 2,
                         "members": ["m1"]}], "next_id": 2}
    create = {"tool": "create_event", "args": {"title": "Рейд", "capacity": 2}}
    join = {"tool": "join_event", "args": {"event_id": "e1", "member_id": "m2"}}

next_id задаёт следующий свободный номер eN. Команда create_event добавляет
событие с пустым members, увеличивает next_id и возвращает value={event_id}.
Команда join_event добавляет участника и возвращает value={event_id, member_id}.
Порядок отказов при вступлении: unknown_event, already_joined, event_full.
Неизвестная команда отклоняется с unknown_tool. given_dispatch возвращает
{status, state, result, reason}: при успехе status="done", result=value,
reason=None; при отказе status="rejected", result=None, reason — код отказа,
state равно исходному состоянию. Входные объекты сохраняются.
```

### Задание

До подтверждения игрок хочет увидеть, что произойдёт с локальным
состоянием гильдии, если применить команду. Добавь режим preview и
**сохрани старый режим apply. Реальных игровых вызовов здесь нет:**
это чистая симуляция.

**Аргументы:**

```text
state содержит события и next_id; command — обычная команда
create_event или join_event. Форматы приведены в правилах данных
этой задачи. mode гарантированно равен 'apply' либо 'preview'.
Для корректного обычного выполнения вызывай given_dispatch,
приведённый в этом файле.
```

Верни ключи status, state, result, reason, preview_state.
В apply поведение совпадает с given_dispatch, включая отказ: поле
preview_state всегда None. В preview при успехе status='preview',
state равен исходному состоянию, result содержит предсказанный value,
reason=None, а preview_state содержит предсказанное новое состояние.
При отказе preview верни status='rejected', исходный state, result=None,
reason из диспетчера и preview_state=None. Сам исходный state никогда
не меняется. Предпросмотр создания показывает увеличенный next_id в
preview_state, но не расходует его в возвращаемом state.

**Пример:**

```python
state={"events":[],"next_id":1}
command={"tool":"create_event","args":{"title":"Рейд","capacity":4}}
task_xla15_preview_action(state, command, "preview") == {
    "status":"preview","state":{"events":[],"next_id":1},
    "result":{"event_id":"e1"},"reason":None,
    "preview_state":{"events":[{"id":"e1","title":"Рейд",
    "capacity":4,"members":[]}],"next_id":2}}
```

Второй пример: та же команда в apply возвращает
{"status":"done","state":{"events":[{"id":"e1","title":"Рейд",
"capacity":4,"members":[]}],"next_id":2},"result":{"event_id":"e1"},
"reason":None,"preview_state":None}.
Третий пример: state как выше и join_event с event_id='missing',
member_id='m1' в preview даёт rejected, исходный state, result=None,
reason='unknown_event', preview_state=None.

Старое поведение apply должно сохраниться для всех корректных и
отказных команд. Проверь, что повторный вызов preview с тем же входом
даёт тот же прогноз и не меняет входные словари или списки.
