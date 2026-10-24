from copy import deepcopy


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
    updated = deepcopy(accounts)
    updated_lots = deepcopy(lots)
    candidates = [
        index
        for index, lot in enumerate(lots)
        if lot["status"] == "open"
        and lot["quantity"] > 0
        and lot["item"] == item
        and lot["seller_id"] != buyer_id
    ]
    candidates.sort(key=lambda index: (lots[index]["price"], lots[index]["id"]))
    receipts = []
    acquired = 0
    spent = 0
    for index in candidates:
        if acquired == requested:
            break
        lot = updated_lots[index]
        quantity = min(
            requested - acquired,
            lot["quantity"],
            updated["gold"][buyer_id] // lot["price"],
        )
        if quantity == 0:
            continue
        purchase = given_buy_quantity(updated, lot, buyer_id, quantity, fee_percent)
        updated = purchase["accounts"]
        updated_lots[index] = purchase["lot"]
        receipt = purchase["receipt"]
        receipts.append({"lot_id": lot["id"], **receipt})
        acquired += quantity
        spent += receipt["gross"]
    return {
        "accounts": updated,
        "lots": updated_lots,
        "receipts": receipts,
        "acquired": acquired,
        "missing_qty": requested - acquired,
        "spent": spent,
    }
