"""
XL-A05. НАЙТИ БАГ — награда выдаётся повторно.

Все ID и названия — строки, числа — целые. Входные объекты менять нельзя.
Каждая задача самостоятельна: всё, что нужно для решения, есть в её условии.
В задаче с ошибкой сдай исправление, объяснение причины
и пример, на котором ошибка воспроизводится.
В задаче на доработку проверь и старый простой случай, и новые требования.

Работай с этой функцией. GIVEN-помощники можно вызывать, но нельзя изменять.
"""


from copy import deepcopy


def task_xla05_claim_reward(player, quest_id, rewards):
    """
        XL-A05. НАЙТИ БАГ — награда выдаётся повторно.

        Игрок дважды нажал «Забрать», и награда за квест пришла два раза.
        Исправь код так, чтобы один квест приносил награду только один раз,
        в том числе при последовательных вызовах функции.

        Что приходит на вход:
            player = {"gold": 10, "completed": ["q1"], "claimed": []}.
            rewards = {"q1": 5, "q2": 20}; значения — золото >= 0.
            completed и claimed — списки уникальных ID; claimed входит в completed.

        Верни: {"status": строка, "player": новое состояние}.
        Проверки идут строго в таком порядке:
            1. quest_id нет в rewards -> "unknown_quest".
            2. Награда уже в claimed -> "already_claimed".
            3. quest_id нет в completed -> "not_completed".
            4. Иначе -> "claimed": прибавить золото, дописать ID в конец claimed.
        completed не меняется. При любом отказе состояние равно исходному.
        Входной player менять нельзя — в том числе его списки.

        Пример:
            first = task_xla05_claim_reward(
                {"gold": 10, "completed": ["q1"], "claimed": []}, "q1", {"q1": 5})
            Ожидаем:
                {"status": "claimed", "player":
                 {"gold": 15, "completed": ["q1"], "claimed": ["q1"]}}.
            Второй вызов с first["player"] -> status="already_claimed",
            gold остаётся 15, claimed остаётся ["q1"].
            Запрос неизвестного q9 -> unknown_quest, всё состояние прежнее.

            assert task_xla05_claim_reward(first["player"], "q1", {"q1": 5}) == {
                "status": "already_claimed", "player": first["player"]}
            assert task_xla05_claim_reward(first["player"], "q9", {"q1": 5}) == {
                "status": "unknown_quest", "player": first["player"]}

        Проверь также нулевую награду и известный, но незавершённый квест.
        Пример с повторным вызовом должен быть в твоей проверке исправления.
        """
    result = deepcopy(player)
    if quest_id not in rewards:
        return {"status": "unknown_quest", "player": result}
    if quest_id not in player["completed"]:
        return {"status": "not_completed", "player": result}
    result["gold"] += rewards[quest_id]
    result["claimed"].append(quest_id)
    return {"status": "claimed", "player": result}
