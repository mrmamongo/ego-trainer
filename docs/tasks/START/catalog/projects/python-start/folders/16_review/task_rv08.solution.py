def task_rv08_validate_request(request, prices):
    if not request.get("user"):
        return {"status": "rejected", "reason": "no_user"}
    if request["item"] not in prices:
        return {"status": "rejected", "reason": "unknown_item"}
    if request["qty"] < 1 or request["qty"] > 10:
        return {"status": "rejected", "reason": "bad_qty"}
    if request["gold"] < prices[request["item"]] * request["qty"]:
        return {"status": "rejected", "reason": "not_enough_gold"}
    return {"status": "done", "reason": None}
