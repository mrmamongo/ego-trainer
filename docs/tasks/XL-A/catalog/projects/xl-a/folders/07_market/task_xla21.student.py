"""
XL-A21. НОВЫЙ КОД — собрать заказ из нескольких предложений.

Все расчёты используют целое золото, настоящих платежей нет.
accounts = {gold: {user_id: qty}, bags: {user_id: {item: qty}},
treasury: qty}. Лот: id, seller_id, item, price (>0), quantity (>=0),
status (open/closed). Товар лота уже на рынке, не в сумке продавца.
Для каждого пользователя есть запись в gold и bags; сумка может быть пустым
словарём. Собственные лоты пропускаются. fee_percent — целое от 0 до 100; id лотов уникальны.
Словари и списки входа менять запрещено.

Работай с этой функцией. GIVEN-помощники можно вызывать, но нельзя изменять.
"""


# GIVEN: готовый помощник для этой задачи.


def given_buy_quantity(accounts, lot, buyer_id, quantity, fee_percent=10):
    copied = {
        "gold": dict(accounts["gold"]),
        "bags": {user: dict(bag) for user, bag in accounts["bags"].items()},
        "treasury": accounts["treasury"],
    }
    changed_lot = dict(lot)
    if quantity <= 0:
        reason = "invalid_quantity"
    elif lot["status"] != "open" or lot["quantity"] <= 0:
        reason = "lot_closed"
    elif quantity > lot["quantity"]:
        reason = "not_enough_items"
    elif accounts["gold"][buyer_id] < lot["price"] * quantity:
        reason = "not_enough_gold"
    else:
        reason = None
    if reason:
        return {
            "status": "rejected",
            "accounts": copied,
            "lot": changed_lot,
            "receipt": None,
            "reason": reason,
        }
    gross = lot["price"] * quantity
    fee = gross * fee_percent // 100
    copied["gold"][buyer_id] -= gross
    copied["gold"][lot["seller_id"]] += gross - fee
    copied["treasury"] += fee
    bag = copied["bags"].setdefault(buyer_id, {})
    bag[lot["item"]] = bag.get(lot["item"], 0) + quantity
    changed_lot["quantity"] -= quantity
    if changed_lot["quantity"] == 0:
        changed_lot["status"] = "closed"
    return {
        "status": "bought",
        "accounts": copied,
        "lot": changed_lot,
        "receipt": {"quantity": quantity, "gross": gross, "fee": fee},
        "reason": None,
    }


def task_xla21_buy_cheapest(accounts, lots, buyer_id, item, requested, fee_percent=10):
    """
    XL-A21. НОВЫЙ КОД — собрать заказ из нескольких предложений.

    Игроку нужно requested единиц одного предмета; на рынке может быть
    несколько лотов с разными ценами и остатками. Реализуй покупку с
    несколькими продавцами, обязательно используя GIVEN given_buy_quantity
    для каждой фактической сделки. Функция-помощник независима от другой
    задачи и уже правильно обрабатывает один лот, комиссию и снимки данных.

    Ищи только открытые лоты с quantity > 0 и совпадающим item; собственные
    лоты buyer_id пропусти. Сортируй кандидатов по возрастанию price, затем
    по id лота лексикографически для однозначного выбора равных цен. Для
    каждого кандидата покупай min(остаток заказа, запас лота, текущие золото
    покупателя // price). Если получилось 0, пропускай его. Частичное
    исполнение допустимо и не откатывается; после исчерпания денег или
    предложений цикл заканчивается.

    requested — целое >= 0. Верни {"accounts": ..., "lots": список в исходном
    порядке с изменёнными выбранными лотами, "receipts": ..., "acquired": int,
    "missing_qty": int, "spent": int}. Каждая квитанция — {"lot_id", "quantity",
    "gross", "fee"}, в порядке сделок. При requested=0 входы копируются,
    квитанций нет, суммы равны нулю. Иные лоты неизменны, входы не мутировать.

    Пример: 13 золота, b: цена 3 запас 2, a: цена 5 запас 3, заказ 4. Купи
    2 у b и 1 у a: acquired=3, missing_qty=1, spent=11, остаток a=2; комиссия
    10% округляется вниз и обе квитанции имеют fee=0. Лоты другого предмета,
    собственные предложения и закрытые лоты пропускаются. При одинаковой
    цене сначала выбирается меньший id; если подходящих лотов нет, заказ
    полностью не исполнен. Проверь также нулевой заказ и нехватку средств.
    Проверочные вызовы и полные результаты:
        acc = {"gold": {1: 13, 2: 0, 3: 0}, "bags": {1: {}, 2: {}, 3: {}}, "treasury": 0}
        offers = [
            {"id": "b", "seller_id": 2, "item": "ore", "price": 3, "quantity": 2, "status": "open"},
            {"id": "a", "seller_id": 3, "item": "ore", "price": 5, "quantity": 3, "status": "open"}]
        task_xla21_buy_cheapest(acc, offers, 1, "ore", 4) == {
            "accounts": {"gold": {1: 2, 2: 6, 3: 5}, "bags": {1: {"ore": 3}, 2: {}, 3: {}}, "treasury": 0},
            "lots": [
                {"id": "b", "seller_id": 2, "item": "ore", "price": 3, "quantity": 0, "status": "closed"},
                {"id": "a", "seller_id": 3, "item": "ore", "price": 5, "quantity": 2, "status": "open"}],
            "receipts": [{"lot_id": "b", "quantity": 2, "gross": 6, "fee": 0},
                {"lot_id": "a", "quantity": 1, "gross": 5, "fee": 0}],
            "acquired": 3, "missing_qty": 1, "spent": 11}
        task_xla21_buy_cheapest(acc, [], 1, "ore", 2) == {
            "accounts": acc, "lots": [], "receipts": [], "acquired": 0, "missing_qty": 2, "spent": 0}
    """
    pass
