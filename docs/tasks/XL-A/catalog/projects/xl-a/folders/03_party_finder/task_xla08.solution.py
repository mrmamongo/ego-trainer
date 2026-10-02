def given_order_candidates(players):
    return sorted(players, key=lambda player: (-player["wait_seconds"], player["id"]))


def task_xla08_build_party(players, slots):
    members = []
    missing = {}
    for role in ("tank", "healer", "damage"):
        matching = given_order_candidates([player for player in players if player["role"] == role])
        selected = matching[: slots.get(role, 0)]
        members.extend(player["id"] for player in selected)
        missing[role] = slots.get(role, 0) - len(selected)
    return {
        "members": members,
        "missing": missing,
        "ready": all(value == 0 for value in missing.values()),
    }
