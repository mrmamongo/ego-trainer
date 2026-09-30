"""
XL-A / 07. Рынок — задачи XL-A19, XL-A20, XL-A21.

Все расчёты используют целое золото, настоящих платежей нет.
accounts = {gold: {user_id: qty}, bags: {user_id: {item: qty}},
treasury: qty}. Лот: id, seller_id, item, price (>0), quantity (>=0),
status (open/closed). Товар лота уже на рынке, не в сумке продавца.
Для каждого пользователя есть запись в gold и bags; сумка может быть пустым
словарём. В XL-A19/20 покупатель и продавец различны; XL-A21 пропускает
собственные лоты. fee_percent — целое от 0 до 100; id лотов в XL-A21 уникальны.
Словари и списки входа менять запрещено.
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


# GIVEN для XL-A20: старая корректная покупка всего лота.
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
    given_buy_whole как опору для старого полного сценария; не вызывай код
    задачи XL-A19 и не полагайся на него.

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


# GIVEN для XL-A21: покупка заданного количества на отдельном снимке данных.
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
