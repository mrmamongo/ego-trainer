"""
XL-A19. НАЙТИ БАГ — рыночная комиссия создаёт лишнее золото.

Все расчёты используют целое золото, настоящих платежей нет.
accounts = {gold: {user_id: qty}, bags: {user_id: {item: qty}},
treasury: qty}. Лот: id, seller_id, item, price (>0), quantity (>=0),
status (open/closed). Товар лота уже на рынке, не в сумке продавца.
Для каждого пользователя есть запись в gold и bags; сумка может быть пустым
словарём. Покупатель и продавец различны. fee_percent — целое от 0 до 100; id лотов уникальны.
Словари и списки входа менять запрещено.

Работай с этой функцией. GIVEN-помощники можно вызывать, но нельзя изменять.
"""


def task_xla19_buy_lot(accounts, lot, buyer_id, fee_percent=10):
    """
    XL-A19. НАЙТИ БАГ — рыночная комиссия создаёт лишнее золото.

    В игре игрок покупает весь лот одним действием. Сейчас после некоторых
    сделок сумма золота игроков и казны увеличивается, хотя рынок ничего
    не производит. Найди и исправь ошибку в расчёте выплаты. Важно сохранить
    интерфейс: accounts, lot, buyer_id и fee_percent; по умолчанию комиссия
    составляет 10 процентов. fee_percent — целое от 0 до 100 включительно.

    Покупка доступна, только если лот открыт и quantity > 0, иначе отказ с
    reason="lot_closed". Затем проверь средства покупателя; при нехватке
    верни reason="not_enough_gold". В обоих случаях результат должен содержать
    глубокие копии исходных accounts и lot, receipt=None; исходные данные
    неизменны. Успешный платёж: gross=price*quantity,
    fee=gross*fee_percent//100. Сними gross с покупателя, продавцу начисли
    gross-fee, казне — fee; добавь весь товар в сумку покупателя. Лот получает
    quantity=0 и status="closed".

    Верни {"status": "bought" или "rejected", "accounts": ...,
    "lot": ..., "receipt": ... или None, "reason": ... или None}.
    Квитанция при успехе ровно {"quantity", "gross", "fee"}.

    Пример: у покупателя 100, продавца 0, treasury=0; цена 10, запас 2,
    комиссия 10%. Итог: 80, 18 и 2 соответственно, сумка покупателя получает
    2 предмета, квитанция gross=20 fee=2. Суммарное золото остаётся 100.
    При 19 золота покупателя сделка отклоняется без изменений и без квитанции.
    Проверь также комиссию 0%, комиссию 100%, пустой лот и сохранность входов.

    Исправь стартовую реализацию; приложи объяснение и воспроизводящий пример.

    Проверочные вызовы и полные результаты:
        acc = {"gold": {1: 100, 2: 0}, "bags": {1: {}, 2: {}}, "treasury": 0}
        lot = {"id": "L", "seller_id": 2, "item": "ore", "price": 10, "quantity": 2, "status": "open"}
        task_xla19_buy_lot(acc, lot, 1) == {
            "status": "bought", "accounts": {"gold": {1: 80, 2: 18}, "bags": {1: {"ore": 2}, 2: {}}, "treasury": 2},
            "lot": {"id": "L", "seller_id": 2, "item": "ore", "price": 10, "quantity": 0, "status": "closed"},
            "receipt": {"quantity": 2, "gross": 20, "fee": 2}, "reason": None}
        poor = {"gold": {1: 19, 2: 0}, "bags": {1: {}, 2: {}}, "treasury": 0}
        task_xla19_buy_lot(poor, lot, 1) == {
            "status": "rejected", "accounts": poor, "lot": lot, "receipt": None, "reason": "not_enough_gold"}
    Первый результат должен сохранять общий золотой запас 100.
    """
    updated = {
        "gold": dict(accounts["gold"]),
        "bags": {user: dict(bag) for user, bag in accounts["bags"].items()},
        "treasury": accounts["treasury"],
    }
    new_lot = dict(lot)
    if lot["status"] != "open" or lot["quantity"] == 0:
        reason = "lot_closed"
    else:
        gross = lot["price"] * lot["quantity"]
        if accounts["gold"][buyer_id] < gross:
            reason = "not_enough_gold"
        else:
            reason = None
    if reason is not None:
        return {
            "status": "rejected",
            "accounts": updated,
            "lot": new_lot,
            "receipt": None,
            "reason": reason,
        }
    quantity = lot["quantity"]
    gross = lot["price"] * quantity
    fee = gross * fee_percent // 100
    updated["gold"][buyer_id] -= gross
    updated["gold"][lot["seller_id"]] += gross
    updated["treasury"] += fee
    bag = updated["bags"].setdefault(buyer_id, {})
    bag[lot["item"]] = bag.get(lot["item"], 0) + quantity
    new_lot["quantity"] = 0
    new_lot["status"] = "closed"
    return {
        "status": "bought",
        "accounts": updated,
        "lot": new_lot,
        "receipt": {"quantity": quantity, "gross": gross, "fee": fee},
        "reason": None,
    }
