---
id: XL-A03
title: "собрать запрос чатботу"
version: "1.0.0"
level: medium
tags: ["chat-context", "new"]
folder: 01_chat_context
---

# Задача XL-A03: собрать запрос чатботу

**Блок:** XLA01 — История чатбота

**Сложность:** medium

**Темы:** chat-context, new

## Условие

**Формат работы:** НОВЫЙ КОД

### Общий договор данных

Работаем с продуктовой логикой: какой контекст получит модель.
Сообщение: {"id": str, "role": str, "text": str, "tokens": int}.
ID уникальны, tokens — положительное целое, budget — целое >= 0.
Стоимость уже известна: считать токены по длине строки не нужно.
Входные списки и словари менять нельзя. Сравниваем значения результатов.

Каждая задача самостоятельна. Помощники GIVEN можно читать, но не менять.

### Задание

Экран чата хранит инструкцию, прошлые сообщения и новый вопрос отдельно.
Собери из них один согласованный запрос и объясни интерфейсу,
какая часть истории не попала в контекст.

**Аргументы:**

```text
system_message — одно сообщение роли system.
history — список прошлых сообщений user/assistant по времени.
user_message — новый вопрос роли user, в history его ещё нет.
budget — общий бюджет. ID уникальны среди ВСЕХ этих сообщений.
```

**Шаги:**

```text
Составь последовательность system_message + history + user_message.
Обязательно вызови given_select_context для выбора сообщений.
Для выбранных сообщений вызови given_api_messages.
dropped_ids — ID невыбранных сообщений в порядке исходной
последовательности. Не сортируй их по алфавиту.
```

**Верни:**

```text
{"status": "ready" или "too_large",
 "messages": [{"role": ..., "content": ...}, ...],
 "used_tokens": int, "missing_tokens": int, "dropped_ids": [...]}.
status и оба числа берутся из результата отбора.
При too_large messages=[], used_tokens=0, dropped_ids содержит
ВСЕ ID, включая инструкцию и новый вопрос.
```

**Пример:**

```text
system_message = {"id": "s", "role": "system", "text": "Кратко", "tokens": 3}
history = [{"id": "h", "role": "assistant", "text": "Привет", "tokens": 4}]
user_message = {"id": "u", "role": "user", "text": "Где рейд?", "tokens": 5}
budget=8 -> {
    "status": "ready",
    "messages": [{"role": "system", "content": "Кратко"},
                 {"role": "user", "content": "Где рейд?"}],
    "used_tokens": 8, "missing_tokens": 0, "dropped_ids": ["h"]}
budget=7 -> {"status": "too_large", "messages": [],
             "used_tokens": 0, "missing_tokens": 1,
             "dropped_ids": ["s", "h", "u"]}.

assert task_xla03_build_request(system_message, [], user_message, 8) == {
    "status": "ready",
    "messages": [{"role": "system", "content": "Кратко"},
                 {"role": "user", "content": "Где рейд?"}],
    "used_tokens": 8, "missing_tokens": 0, "dropped_ids": []}
```

Проверь: пустую history; бюджет ровно на обязательные сообщения;
сохранность всех входных объектов. Логику отбора повторять не нужно.
