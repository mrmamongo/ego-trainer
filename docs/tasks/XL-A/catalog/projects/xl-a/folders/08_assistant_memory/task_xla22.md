---
id: XL-A22
title: "применить пакет правок к профилю"
version: "1.0.0"
level: hard
tags: ["assistant-memory", "new"]
folder: 08_assistant_memory
---

# Задача XL-A22: применить пакет правок к профилю

**Блок:** XLA08 — Память помощника

**Сложность:** hard

**Темы:** assistant-memory, new

## Условие

**Формат работы:** НОВЫЙ КОД

### Общий договор данных

Профиль помощника — вложенный словарь с непустыми строковыми ключами.
Листья: str, int, bool или None; списков нет. Пустой словарь допустим.
Входы нельзя менять. Задачи независимы, используют только стандартную
библиотеку и обычные словари/списки.

### Задание

В настройках можно менять одну тему, например роль помощника, и
добавлять новые ветки вроде llm.language. Реализуй последовательное
применение обновлений, сохраняя исходные данные.

Аргументы: profile — корректный профиль; updates — список объектов
{"path": [непустые строки, ...], "value": scalar}. Путь непустой.
Промежуточные отсутствующие ключи создаются. Лист на конечном пути
добавляется или заменяется. Если промежуточный ключ уже содержит
**scalar либо конечный ключ содержит dict, обновление конфликтует:**
оно ничего не меняет, но следующие обновления всё равно выполняются.
Равенство учитывает тип: True и 1 — разные значения. Повтор того же
значения того же типа — no-op и в changes не попадает.

Верни {"profile": глубокую копию результата, "changes": [...],
"errors": [...]}. Изменение: {path: копия пути, kind: "added" или
"changed", before: прежний scalar или None, after: новое значение}.
Отсутствие ключа и ключ со значением None различаются через kind.
Записи идут в порядке обновлений, одинаковый путь не объединяй.
Ошибка: {index: индекс обновления, path: копия пути,
reason: "path_conflict"}. Изменение профиля и updates запрещено.

Примеры: роль tank -> healer даёт changed; отсутствующий путь
["llm", "language"] со значением "ru" даёт added и создаёт llm.
Повтор ["role"]="healer" не создаёт запись. Путь ["role", "name"]
при строковом role даёт path_conflict, не отменяя последующие правки.
Проверь также пустой профиль, значение None и True против 1.

**Пример 1:**

```python
profile = {"role": "tank"}
updates = [{"path": ["role"], "value": "healer"},
           {"path": ["llm", "language"], "value": "ru"}]
assert task_xla22_update_profile(profile, updates) == {
    "profile": {"role": "healer", "llm": {"language": "ru"}},
    "changes": [
        {"path": ["role"], "kind": "changed", "before": "tank", "after": "healer"},
        {"path": ["llm", "language"], "kind": "added", "before": None, "after": "ru"}],
    "errors": []}
```

**Пример 2 — отдельный вызов, индексы снова начинаются с нуля:**

```python
profile = {"role": "healer"}
updates = [{"path": ["role"], "value": "healer"},
           {"path": ["role", "name"], "value": "Mira"}]
assert task_xla22_update_profile(profile, updates) == {
    "profile": {"role": "healer"}, "changes": [],
    "errors": [{"index": 1, "path": ["role", "name"],
                "reason": "path_conflict"}]}
```
