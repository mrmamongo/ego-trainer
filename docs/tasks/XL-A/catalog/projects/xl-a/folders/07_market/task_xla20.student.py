"""
XL-A20. ПРАВКИ — покупателю нужна часть складского лота.

Все расчёты используют целое золото, настоящих платежей нет.
accounts = {gold: {user_id: qty}, bags: {user_id: {item: qty}},
treasury: qty}. Лот: id, seller_id, item, price (>0), quantity (>=0),
status (open/closed). Товар лота уже на рынке, не в сумке продавца.
Для каждого пользователя есть запись в gold и bags; сумка может быть пустым
словарём. Покупатель и продавец различны. fee_percent — целое от 0 до 100; id лотов уникальны.
Словари и списки входа менять запрещено.

Работай с этой функцией. GIVEN-помощники можно вызывать, но нельзя изменять.
"""


# GIVEN: готовый помощник для этой задачи.


def given_buy_whole(accounts, lot, buyer_id, fee_percent=10):
    updated = {
        "gold": dict(accounts["gold"]),
        "bags": {user: dict(bag) for user, bag in accounts["bags"].items()},
        "treasury": accounts["treasury"],
    }
    new_lot = dict(lot)
    if lot["status"] != "open" or lot["quantity"] <= 0:
        return {
            "status": "rejected",
            "accounts": updated,
            "lot": new_lot,
            "receipt": None,
            "reason": "lot_closed",
        }
    gross = lot["price"] * lot["quantity"]
    if updated["gold"][buyer_id] < gross:
        return {
            "status": "rejected",
            "accounts": updated,
            "lot": new_lot,
            "receipt": None,
            "reason": "not_enough_gold",
        }
    fee = gross * fee_percent // 100
    updated["gold"][buyer_id] -= gross
    updated["gold"][lot["seller_id"]] += gross - fee
    updated["treasury"] += fee
    bag = updated["bags"].setdefault(buyer_id, {})
    bag[lot["item"]] = bag.get(lot["item"], 0) + lot["quantity"]
    new_lot["quantity"] = 0
    new_lot["status"] = "closed"
    return {
        "status": "bought",
        "accounts": updated,
        "lot": new_lot,
        "receipt": {"quantity": lot["quantity"], "gross": gross, "fee": fee},
        "reason": None,
    }


def task_xla20_buy_quantity(accounts, lot, buyer_id, quantity, fee_percent=10):
    """
    XL-A20. ПРАВКИ — покупателю нужна часть складского лота.

    Рынок уже поддерживает покупку всего лота. Расширь операцию: покупатель
    указывает точное количество. Старые успешные запросы с quantity, равным
    полному запасу, должны вести себя как раньше, включая комиссию, квитанцию,
    закрытие лота и сохранение денежных средств. Используй заданный
    given_buy_whole как опору для старого полного сценария.

    accounts и lot имеют формат в начале файла. quantity должен быть целым
    положительным числом; полный старый сценарий — quantity равен всему
    остатку лота. Если quantity <= 0, верни отказ
    reason="invalid_quantity". Иначе сначала проверь, что лот открыт и в нём
    есть товар (иначе "lot_closed"), затем что запрошено не больше наличия
    (иначе "not_enough_items"), затем средства покупателя (иначе
    "not_enough_gold"). Отказы не меняют данные и возвращают receipt=None.

    Успех рассчитывает gross=price*quantity, fee=gross*fee_percent//100;
    покупатель платит gross, продавец получает gross-fee, казна получает fee,
    сумка покупателя увеличивается на quantity. Лот уменьшается на купленное:
    если остаток нулевой, status="closed", иначе остаётся "open". Результат
    имеет те же ключи, что у given_buy_whole, а receipt содержит quantity,
    gross и fee. Все входы неизменны.

    Пример: цена 7, запас 5, запрос 2, комиссия 10%: gross=14, fee=1,
    остаток лота 3 и он открыт. Запрос всех 5 закрывает лот. При запасе 5,
    запросе 6 отказ not_enough_items предшествует проверке золота. Проверь
    нулевой/отрицательный запрос и каждый вид отказа.

    Доработай исходную версию ниже, которая игнорирует quantity.
    Проверочные вызовы и полные результаты:
        acc = {"gold": {1: 100, 2: 0}, "bags": {1: {}, 2: {}}, "treasury": 0}
        lot = {"id": "L", "seller_id": 2, "item": "ore", "price": 7, "quantity": 5, "status": "open"}
        task_xla20_buy_quantity(acc, lot, 1, 2) == {
            "status": "bought", "accounts": {"gold": {1: 86, 2: 13}, "bags": {1: {"ore": 2}, 2: {}}, "treasury": 1},
            "lot": {"id": "L", "seller_id": 2, "item": "ore", "price": 7, "quantity": 3, "status": "open"},
            "receipt": {"quantity": 2, "gross": 14, "fee": 1}, "reason": None}
        task_xla20_buy_quantity(acc, lot, 1, 0) == {
            "status": "rejected", "accounts": acc, "lot": lot, "receipt": None, "reason": "invalid_quantity"}
    Запрос quantity=5 сохраняет старое поведение полного выкупа.
    """
    old_result = given_buy_whole(accounts, lot, buyer_id, fee_percent)
    return old_result
