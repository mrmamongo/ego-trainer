def given_order_candidates(players):
    return sorted(players, key=lambda player: (-player["wait_seconds"], player["id"]))


def task_xla09_party_from_tickets(tickets, slots):
    seen = set()
    candidates = []
    for ticket in tickets:
        if ticket["player_id"] in seen:
            continue
        seen.add(ticket["player_id"])
        candidates.append(
            {
                "id": ticket["player_id"],
                "role": ticket["role"],
                "wait_seconds": ticket["wait_seconds"],
            }
        )
    candidates = given_order_candidates(candidates)
    members = []
    missing = {}
    for role in ("tank", "healer", "damage"):
        matching = [player for player in candidates if player["role"] == role]
        selected = matching[: slots.get(role, 0)]
        members.extend(player["id"] for player in selected)
        missing[role] = slots.get(role, 0) - len(selected)
    return {
        "members": members,
        "missing": missing,
        "ready": all(value == 0 for value in missing.values()),
    }
