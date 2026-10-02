"""
XL-A02. ПРАВКИ — закреплённые инструкции и последний вопрос.

Работаем с продуктовой логикой: какой контекст получит модель.
Сообщение: {"id": str, "role": str, "text": str, "tokens": int}.
ID уникальны, tokens — положительное целое, budget — целое >= 0.
Стоимость уже известна: считать токены по длине строки не нужно.
Входные списки и словари менять нельзя. Сравниваем значения результатов.

Каждая задача самостоятельна. Помощники GIVEN можно читать, но не менять.

Работай с этой функцией. GIVEN-помощники можно вызывать, но нельзя изменять.
"""


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
