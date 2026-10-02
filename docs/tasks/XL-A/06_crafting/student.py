"""
XL-A / 06. Производство — задачи XL-A16, XL-A17, XL-A18.

Инвентарь: {название предмета: количество}, количества — целые >= 0.
Рецепт: ingredients — расходуемые материалы; tools — инструменты,
которые нужны для проверки наличия, но не расходуются; product —
создаваемый предмет и его количество. Все словари на входе неизменяемы.
Задачи независимы: в каждой есть весь нужный код или GIVEN-помощник.
"""


def task_xla16_craft(inventory, recipe):
    """
    XL-A16. ПРАВКИ — верстак получил требование учитывать инструменты.

    В игре мастерская принимает текущий инвентарь и один рецепт. Старая
    версия уже умеет списывать материалы и выдавать продукт. Она верна,
    если в рецепте нет поля tools; теперь расширь её так, чтобы инструмент
    требовался для работы, но оставался у игрока после успешного крафта.
    Не меняй интерфейс и сохрани прежнее поведение рецептов без tools.

    inventory имеет вид {item: qty}, где qty — целое >= 0. В recipe поле
    ingredients обязательно: {item: положительное количество}; tools
    необязательно и по умолчанию равно {}; product имеет вид
    {"item": строка, "qty": положительное целое}. Имена предметов — строки.
    Если предмет указан и как материал, и как инструмент, до начала работы
    нужна сумма двух количеств; после успеха списывается только материал.

    Верни ровно {"status": "crafted" или "missing", "inventory": новый
    словарь, "missing": словарь нехваток}. Проверяй все требования по
    исходному инвентарю. При отказе нехватки включают материалы и инструменты,
    сортируются по имени; исходный снимок инвентаря возвращается без изменений.
    При успехе уменьши материалы, добавь продукт, сохрани нулевые ключи и
    несвязанные предметы. Входные объекты менять нельзя.

    Пример: {"iron": 2, "hammer": 1} плюс рецепт на 2 iron, hammer и 1
    sword даёт iron=0, hammer=1, sword=1. Если hammer отсутствует, статус
    missing, missing={"hammer": 1}, а материалы не списываются. Если нужно
    2 iron как материал и 1 iron как инструмент, при запасе 2 отказ должен
    показать нехватку 1; при запасе 3 успех оставит 1 iron.
    Проверь также пустые tools, нулевые и посторонние ключи.

    Проверочные вызовы и полные результаты:
        inv = {"iron": 2, "hammer": 1, "gem": 0}
        rec = {"ingredients": {"iron": 2}, "tools": {"hammer": 1},
               "product": {"item": "sword", "qty": 1}}
        task_xla16_craft(inv, rec) == {
            "status": "crafted", "inventory": {"iron": 0, "hammer": 1, "gem": 0, "sword": 1}, "missing": {}}
        inv = {"iron": 2}
        task_xla16_craft(inv, rec) == {
            "status": "missing", "inventory": {"iron": 2}, "missing": {"hammer": 1}}
    Отказ во втором случае не должен списать iron.
    """
    result = dict(inventory)
    missing = {}
    for item in sorted(recipe["ingredients"]):
        quantity = recipe["ingredients"][item]
        shortage = quantity - inventory.get(item, 0)
        if shortage > 0:
            missing[item] = shortage
    if missing:
        return {"status": "missing", "inventory": result, "missing": missing}
    for item in sorted(recipe["ingredients"]):
        quantity = recipe["ingredients"][item]
        result[item] = result.get(item, 0) - quantity
    product = recipe["product"]
    result[product["item"]] = result.get(product["item"], 0) + product["qty"]
    return {"status": "crafted", "inventory": result, "missing": {}}


# GIVEN для XL-A17: независимая правильная операция одного крафта.
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
    идентификаторов рецептов к рецептам формата XL-A16. Заказы выполняются
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


def task_xla18_craft_atomic(inventory, recipe):
    """
    XL-A18. НАЙТИ БАГ — отказавшийся крафт оставляет верстак пустым.

    В мастерской операция должна быть атомарной: игрок либо получает весь
    продукт и оплачивает все материалы, либо не теряет ничего. После
    обновления интерфейса игроки сообщают, что при нехватке одного из
    компонентов часть других материалов исчезает, хотя заказ отмечен как
    отклонённый. Найди причину, исправь реализацию и сохрани её публичный
    интерфейс. Рецепт этой задачи содержит только ingredients и product;
    инструментов здесь нет.

    inventory — словарь {item: qty}, qty целые >= 0. ingredients — словарь
    положительных количеств материалов; product — {"item": имя,
    "qty": положительное целое}. Проверка нехваток идёт по именам предметов
    в алфавитном порядке. При первой нехватке верни ровно
    {"status": "rejected", "inventory": копия исходного инвентаря,
    "missing_item": имя первого недостаточного материала}. Никакие ресурсы
    при таком отказе не списываются. При успехе верни status="crafted",
    новый инвентарь и missing_item=None: вычти все материалы, затем добавь
    продукт. Нулевые ключи и посторонние предметы сохраняй. Не меняй входы.

    Пример: iron=2, wood=0, рецепт требует iron=1 и wood=1. Заказ отклонён,
    missing_item="wood", но возвращённый iron обязан остаться равен 2.
    Если wood=1, заказ успешен: iron=1, wood=0 и продукт добавлен.
    Результат не должен менять исходный словарь даже при успехе.

    Исправь намеренно неверный стартовый вариант ниже. Добавь в сдачу
    короткое объяснение причины и пример, который показывает частичную
    потерю ресурсов до исправления. Проверь пустой набор ингредиентов,
    нехватку первого по алфавиту предмета и отсутствие мутаций.

    Проверочные вызовы и полные результаты:
        inv = {"iron": 2, "wood": 0}
        rec = {"ingredients": {"iron": 1, "wood": 1}, "product": {"item": "handle", "qty": 1}}
        task_xla18_craft_atomic(inv, rec) == {
            "status": "rejected", "inventory": {"iron": 2, "wood": 0}, "missing_item": "wood"}
        inv = {"iron": 2, "wood": 1}
        task_xla18_craft_atomic(inv, rec) == {
            "status": "crafted", "inventory": {"iron": 1, "wood": 0, "handle": 1}, "missing_item": None}
    """
    result = dict(inventory)
    for item in sorted(recipe["ingredients"]):
        quantity = recipe["ingredients"][item]
        if result.get(item, 0) < quantity:
            return {"status": "rejected", "inventory": result, "missing_item": item}
        result[item] = result.get(item, 0) - quantity
    product = recipe["product"]
    result[product["item"]] = result.get(product["item"], 0) + product["qty"]
    return {"status": "crafted", "inventory": result, "missing_item": None}
