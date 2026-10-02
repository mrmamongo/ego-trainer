from copy import deepcopy


def task_xla19_buy_lot(accounts, lot, buyer_id, fee_percent=10):
    updated = deepcopy(accounts)
    new_lot = deepcopy(lot)
    if lot["status"] != "open" or lot["quantity"] <= 0:
        reason = "lot_closed"
    elif accounts["gold"][buyer_id] < lot["price"] * lot["quantity"]:
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
    updated["gold"][lot["seller_id"]] += gross - fee
    updated["treasury"] += fee
    bag = updated["bags"][buyer_id]
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
