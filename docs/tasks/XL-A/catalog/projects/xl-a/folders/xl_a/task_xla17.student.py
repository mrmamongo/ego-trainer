"""
XL-A17. НОВЫЙ КОД — очередь заказов мастерской.

Инвентарь: {название предмета: количество}, количества — целые >= 0.
Рецепт: ingredients — расходуемые материалы; tools — инструменты,
которые нужны для проверки наличия, но не расходуются; product —
создаваемый предмет и его количество. Все словари на входе неизменяемы.
Задачи независимы: в каждой есть весь нужный код или GIVEN-помощник.

Дополнительный договор данных

Данные одного рецепта:
    inventory = {"iron": 3, "hammer": 1}
    recipe = {"ingredients": {"iron": 2}, "tools": {"hammer": 1},
              "product": {"item": "sword", "qty": 1}}

Имена предметов — строки. В inventory количества целые >= 0.
ingredients обязательно и задаёт положительные количества расходуемых
материалов. tools необязательно, по умолчанию {}; инструменты нужны
для проверки наличия и не расходуются. product имеет поля item (строка)
и qty (положительное целое). Если один предмет нужен как материал и как
инструмент, до начала крафта требуется сумма количеств; списывается только
материал. Проверяются все требования по исходному запасу. Успех сохраняет
нулевые и посторонние ключи, добавляет продукт. При нехватке запас не меняется.
given_craft возвращает {status: "crafted" или "missing", inventory: новый
словарь, missing: словарь положительных нехваток}. Порядок ключей missing
не является критерием правильности: сравниваются названия и количества.

Работай с этой функцией. GIVEN-помощники можно вызывать, но нельзя изменять.
"""


# GIVEN: готовый помощник для этой задачи.


def given_craft(inventory, recipe):
    result = dict(inventory)
    required = dict(recipe["ingredients"])
    for item, qty in recipe.get("tools", {}).items():
        required[item] = required.get(item, 0) + qty
    missing = {
        item: required[item] - inventory.get(item, 0)
        for item in sorted(required)
        if inventory.get(item, 0) < required[item]
    }
    if missing:
        return {"status": "missing", "inventory": result, "missing": missing}
    for item, qty in recipe["ingredients"].items():
        result[item] = result.get(item, 0) - qty
    product = recipe["product"]
    result[product["item"]] = result.get(product["item"], 0) + product["qty"]
    return {"status": "crafted", "inventory": result, "missing": {}}


def task_xla17_craft_queue(inventory, orders, recipes):
    """
    XL-A17. НОВЫЙ КОД — очередь заказов мастерской.

    Игрок отправляет несколько заказов за один визит к ремесленнику.
    Каждый заказ содержит уникальный id и recipe_id; recipes — словарь
    идентификаторов рецептов к рецептам из договора данных этой задачи. Заказы выполняются
    строго в переданном порядке. Успешный результат сразу меняет запас,
    поэтому следующий заказ использует уже обновлённый инвентарь. Ошибка
    одного заказа не останавливает очередь и не откатывает предыдущие.

    Реализуй функцию через GIVEN given_craft(inventory, recipe), обязательно
    вызови его для каждого заказа с известным рецептом. Не копируй механику
    проверки и списания. Для неизвестного recipe_id helper не вызывается:
    заказ получает status="rejected", reason="unknown_recipe", missing={}.
    Для известного рецепта, который не помещается в текущий запас, верни
    status="rejected", reason="missing_resources" и missing из helper.
    Успех: status="crafted", reason=None, missing={}. Каждый элемент отчёта
    имеет ровно {"id", "status", "reason", "missing"}.

    Итоговый объект: {"inventory": финальный новый словарь, "orders": отчёты
    в исходном порядке, "crafted_count": число успехов}. При пустой очереди
    сохрани копию начального запаса, верни пустые orders и count=0.
    Все входные объекты должны остаться неизменными.

    Пример: запас iron=2; заказ A тратит 1 iron и даёт nail, B неизвестен,
    C тратит 2 iron. A успешен, B отклонён как unknown_recipe, C отклонён
    с missing={"iron": 1}; count=1, финально iron=1 и nail=1. Если C вместо
    этого тратит 1 iron, он тоже успешен, поскольку видит запас после A.
    Проверь также пустые рецепты/заказы и повторный отказ без изменения запаса.

    Проверочные вызовы и полные результаты:
        recipes = {
            "nail": {"ingredients": {"iron": 1}, "product": {"item": "nail", "qty": 1}},
            "plate": {"ingredients": {"iron": 2}, "product": {"item": "plate", "qty": 1}}}
        task_xla17_craft_queue({"iron": 2},
            [{"id": "A", "recipe_id": "nail"}, {"id": "B", "recipe_id": "unknown"},
             {"id": "C", "recipe_id": "plate"}], recipes) == {
            "inventory": {"iron": 1, "nail": 1}, "orders": [
                {"id": "A", "status": "crafted", "reason": None, "missing": {}},
                {"id": "B", "status": "rejected", "reason": "unknown_recipe", "missing": {}},
                {"id": "C", "status": "rejected", "reason": "missing_resources", "missing": {"iron": 1}}],
            "crafted_count": 1}
        task_xla17_craft_queue({"iron": 1}, [], recipes) == {
            "inventory": {"iron": 1}, "orders": [], "crafted_count": 0}
    """
    pass
