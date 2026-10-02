"""XL-M-25 — Исправь дерево достижений (баг: родитель).

Дерево достижений: каждое достижение
{"id": ..., "parent": parent_id | None,
 "unlocked": bool}. Родитель должно
быть разблокировано ПЕРЕД
дочерним. Сейчас unlock_achievement
разблокирует даже если родитель
ещё закрыт.

Исправь: разблокируй только если
parent is None или parent уже
unlocked. Верни {"ok": True} или
{"ok": False, "reason": "parent locked"}.

Пример:
    tree = [{"id":"a","parent":None,"unlocked":False},
            {"id":"b","parent":"a","unlocked":False}]
    unlock_achievement(tree, "b")
    → {"ok": False, "reason": "parent locked"}
"""


def unlock_achievement(tree, ach_id):
    by_id = {a["id"]: a for a in tree}
    ach = by_id[ach_id]
    parent_id = ach["parent"]
    if parent_id is not None:
        parent = by_id[parent_id]
        if not parent["unlocked"]:
            return {"ok": False, "reason": "parent locked"}
    ach["unlocked"] = True
    return {"ok": True}


if __name__ == "__main__":
    tree = [
        {"id": "a", "parent": None, "unlocked": False},
        {"id": "b", "parent": "a", "unlocked": False},
    ]
    print(unlock_achievement(tree, "b"))
