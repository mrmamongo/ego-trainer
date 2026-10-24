from copy import deepcopy


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
    if type(quantity) is not int or quantity <= 0:
        reason = "invalid_quantity"
    elif lot["status"] != "open" or lot["quantity"] <= 0:
        reason = "lot_closed"
    elif quantity > lot["quantity"]:
        reason = "not_enough_items"
    elif accounts["gold"][buyer_id] < lot["price"] * quantity:
        reason = "not_enough_gold"
    else:
        reason = None
    if reason is not None:
        return {
            "status": "rejected",
            "accounts": deepcopy(accounts),
            "lot": deepcopy(lot),
            "receipt": None,
            "reason": reason,
        }

    if quantity == lot["quantity"]:
        return given_buy_whole(accounts, lot, buyer_id, fee_percent)
    purchased_lot = deepcopy(lot)
    purchased_lot["quantity"] = quantity
    result = given_buy_whole(accounts, purchased_lot, buyer_id, fee_percent)
    result["lot"]["quantity"] = lot["quantity"] - quantity
    result["lot"]["status"] = "open"
    return result
