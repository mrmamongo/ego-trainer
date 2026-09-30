"""
XL-A / 01. История чатбота — задачи XL-A01, XL-A02, XL-A03.

Работаем с продуктовой логикой: какой контекст получит модель.
Сообщение: {"id": str, "role": str, "text": str, "tokens": int}.
ID уникальны, tokens — положительное целое, budget — целое >= 0.
Стоимость уже известна: считать токены по длине строки не нужно.
Входные списки и словари менять нельзя. Сравниваем значения результатов.

НАЙТИ БАГ: исправь функцию, запиши причину и воспроизводящий пример.
ПРАВКИ: расширь исходный код, сохрани поведение в оговорённых старых случаях.
НОВЫЙ КОД: реализуй функцию с pass, используя данные помощники.
Каждая задача самостоятельна. Помощники GIVEN можно читать, но не менять.
Готового checker.py в этой пачке нет. Примеры можно вызывать самостоятельно.
"""


def task_xla01_recent_history(messages, budget):
    """
    XL-A01. НАЙТИ БАГ — чатбот отвечает на старый вопрос.

    Пользователь продолжает разговор. Когда история перестаёт помещаться
    в бюджет, чатбот иногда получает начало разговора вместо его конца.
    Исправь выбор сообщений. Не меняй интерфейс функции.

    Вход:
        messages — сообщения от старого к новому; роли user/assistant.
        budget — сколько токенов разрешено отправить модели.

    Договор:
        Верни самый длинный НЕПРЕРЫВНЫЙ хвост истории, сумма tokens
        которого не больше budget. Сообщения неделимы. Результат остаётся
        в хронологическом порядке. Перескакивать через сообщение нельзя.
        Если последнее сообщение не помещается, результат — [].
        Пустая история или нулевой бюджет тоже дают [].
        Новые словари сообщений должны содержать все исходные поля.

    Примеры:
        messages = [
            {"id": "a", "role": "user", "text": "Привет", "tokens": 2},
            {"id": "b", "role": "assistant", "text": "Привет!", "tokens": 3},
            {"id": "c", "role": "user", "text": "Где мой рейд?", "tokens": 4},
        ]
        При budget=7 вернутся сообщения b, c целиком, в этом порядке.
        При budget=4 вернётся только c. При budget=3 вернётся [].
        При budget=9 вернутся a, b, c.

        После исправления должны выполняться проверки:
        assert task_xla01_recent_history(messages, 7) == messages[1:]
        assert task_xla01_recent_history(messages, 3) == []

    Проверь также:
        сообщение ровно на весь бюджет; одно сообщение; пустой список.
        После вызова исходная история должна остаться прежней.

    Что сдать:
        исправление, объяснение причины и один пример с ожидаемым ответом,
        который отличает исходную реализацию от исправленной.
    """
    selected = []
    used = 0
    for message in messages:
        if used + message["tokens"] > budget:
            break
        selected.append(dict(message))
        used += message["tokens"]
    return selected


def task_xla02_pinned_context(messages, budget):
    """
    XL-A02. ПРАВКИ — закреплённые инструкции и последний вопрос.

    Исходная версия выбирает непрерывный хвост. Теперь продукт должен
    сохранять инструкцию бота и актуальный вопрос пользователя.

    Вход:
        messages — хронологическая история. Роли system/user/assistant.
        system бывает не более одного и, если есть, стоит первым.
        Другие предпосылки — в начале файла. История может быть пустой.

    Новые правила:
        1. Обязательны system и последний user, если они существуют.
        2. Если их суммарная стоимость больше budget, вернуть отказ.
        3. Иначе рассматривать остальные сообщения от нового к старому.
           Сообщение брать целиком, если оно помещается в остаток.
           Слишком большое пропустить и продолжить просмотр более старых.
        4. В ответе выбранные сообщения вернуть в исходном порядке.
        Каждое сообщение включается не больше одного раза.

    Результат всегда содержит четыре ключа:
        Успех: {"status": "ready", "messages": [...],
                "used_tokens": сумма, "missing_tokens": 0}.
        Отказ: {"status": "too_large", "messages": [],
                "used_tokens": 0, "missing_tokens": обязательные - budget}.
        Пустая история — ready с пустым списком и двумя нулями.

    Пример:
        messages = [
            {"id": "s", "role": "system", "text": "Кратко", "tokens": 3},
            {"id": "u1", "role": "user", "text": "Привет", "tokens": 4},
            {"id": "a1", "role": "assistant", "text": "Привет!", "tokens": 4},
            {"id": "u2", "role": "user", "text": "Где рейд?", "tokens": 5}]
        budget=12 -> ready, messages=[s, a1, u2], used_tokens=12.
        budget=8  -> ready, messages=[s, u2], used_tokens=8.
        budget=7  -> too_large, messages=[], missing_tokens=1.
        Здесь s, a1, u2 в описании ответа обозначают полные сообщения.

        assert task_xla02_pinned_context(messages, 8) == {
            "status": "ready", "messages": [messages[0], messages[3]],
            "used_tokens": 8, "missing_tokens": 0}
        assert task_xla02_pinned_context(messages, 7) == {
            "status": "too_large", "messages": [],
            "used_tokens": 0, "missing_tokens": 1}

    Совместимость:
        Если вся история помещается, результат сохраняет все сообщения.
        Если нет system, правило последнего user всё равно действует.
        Если нет user, обязательным может быть только system.

    Исходный код ниже работает для выбора хвоста. Доработай его под договор.
    """
    chosen = []
    used = 0
    for message in reversed(messages):
        if used + message["tokens"] > budget:
            break
        chosen.append(dict(message))
        used += message["tokens"]
    chosen.reverse()
    return {"status": "ready", "messages": chosen, "used_tokens": used, "missing_tokens": 0}


# GIVEN для XL-A03: готовая отдельная версия отбора контекста.
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


# GIVEN: преобразование внутреннего сообщения в формат запроса модели.
def given_api_messages(messages):
    return [{"role": m["role"], "content": m["text"]} for m in messages]


def task_xla03_build_request(system_message, history, user_message, budget):
    """
    XL-A03. НОВЫЙ КОД — собрать запрос чатботу.

    Экран чата хранит инструкцию, прошлые сообщения и новый вопрос отдельно.
    Собери из них один согласованный запрос и объясни интерфейсу,
    какая часть истории не попала в контекст.

    Аргументы:
        system_message — одно сообщение роли system.
        history — список прошлых сообщений user/assistant по времени.
        user_message — новый вопрос роли user, в history его ещё нет.
        budget — общий бюджет. ID уникальны среди ВСЕХ этих сообщений.

    Шаги:
        Составь последовательность system_message + history + user_message.
        Обязательно вызови given_select_context для выбора сообщений.
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
