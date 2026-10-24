"""
XL-A03. НОВЫЙ КОД — собрать запрос чатботу.

Здесь мы делаем то, что на продуктовой стороне решает, какой контекст
получит модель.

Как выглядит сообщение:
    {"id": str, "role": str, "text": str, "tokens": int}

ID у сообщений уникальны, tokens — целое число больше нуля, budget —
целое число не меньше нуля. Сколько токенов стоит каждое сообщение,
уже посчитано, поэтому по длине текста их считать не нужно.
Списки и словари, которые приходят на вход, менять нельзя.
Результаты сравниваем по значениям.

Формат работы над задачей:
- НАЙТИ БАГ: исправь функцию, напиши, в чём была причина, и приведи пример,
  на котором ошибка воспроизводится.
- ПРАВКИ: доработай готовый код и сохрани прежнее поведение там, где оно
  оговорено.
- НОВЫЙ КОД: допиши функцию, в которой сейчас стоит pass, опираясь на
  готовые функции, которые уже лежат в файле.

Задачи не зависят друг от друга. Готовые функции (GIVEN) можно вызывать,
но менять их нельзя.

Работай с этой функцией. GIVEN-помощники можно вызывать, но нельзя изменять.
"""


# GIVEN: готовый помощник для этой задачи.


def given_select_context(messages, budget):
    required = {m["id"] for m in messages if m["role"] == "system"}
    for message in reversed(messages):
        if message["role"] == "user":
            required.add(message["id"])
            break
    used = sum(m["tokens"] for m in messages if m["id"] in required)
    if used > budget:
        return {
            "status": "too_large",
            "messages": [],
            "used_tokens": 0,
            "missing_tokens": used - budget,
        }
    selected = set(required)
    for message in reversed(messages):
        if message["id"] not in selected and used + message["tokens"] <= budget:
            selected.add(message["id"])
            used += message["tokens"]
    return {
        "status": "ready",
        "messages": [dict(m) for m in messages if m["id"] in selected],
        "used_tokens": used,
        "missing_tokens": 0,
    }


# GIVEN: готовый помощник для этой задачи.


def given_api_messages(messages):
    return [{"role": m["role"], "content": m["text"]} for m in messages]


def task_xla03_build_request(system_message, history, user_message, budget):
    """
        XL-A03. НОВЫЙ КОД — собрать запрос чатботу.

        Экран чата хранит инструкцию, прошлые сообщения и новый вопрос
        по отдельности. Собери из них один согласованный запрос и скажи
        интерфейсу, какая часть истории не попала в контекст — чтобы это
        можно было показать пользователю.

        Аргументы:
            system_message — одно сообщение роли system.
            history — список прошлых сообщений user/assistant по времени.
            user_message — новый вопрос роли user, в history его ещё нет.
            budget — общий бюджет. ID уникальны среди ВСЕХ этих сообщений.

        Шаги:
            Составь последовательность system_message + history + user_message.
            Обязательно вызови given_select_context, чтобы выбрать сообщения.
            Для выбранных сообщений вызови given_api_messages.
            dropped_ids — ID невыбранных сообщений в порядке исходной
            последовательности. Не сортируй их по алфавиту.

        Верни:
            {"status": "ready" или "too_large",
             "messages": [{"role": ..., "content": ...}, ...],
             "used_tokens": int, "missing_tokens": int, "dropped_ids": [...]}.
            status и оба числа берутся из результата отбора.
            При too_large messages=[], used_tokens=0, dropped_ids содержит
            ВСЕ ID, включая инструкцию и новый вопрос.

        Пример:
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

        Проверь: пустую history; бюджет ровно на обязательные сообщения;
        сохранность всех входных объектов. Логику отбора повторять не нужно.
        """
    pass
