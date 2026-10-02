"""XL-M-20 — Добавь RSVP на гильдейский ивент (новый код).

Гильдия хранит {"members": [...], "events": [...]}.
Каждый event {"id": ..., "name": ..., "rsvps": {...}}
где rsvps[member_id] = "yes"/"no"/"maybe".

Реализуй rsvp(guild, event_id, member_id, status):
- Если event_id не найден — raise KeyError
- Если member_id не в guild["members"] — raise ValueError
- status должен быть "yes"/"no"/"maybe" иначе ValueError
- Обнови rsvps и верни guild (мутируй).

Пример:
    rsvp(g, "e1", "m1", "yes")
    → guild["events"][0]["rsvps"]["m1"] == "yes"
"""


def rsvp(guild, event_id, member_id, status):
    # TODO: реализовать RSVP
    raise NotImplementedError


if __name__ == "__main__":
    g = {
        "members": ["m1", "m2"],
        "events": [{"id": "e1", "name": "raid", "rsvps": {}}],
    }
    rsvp(g, "e1", "m1", "yes")
    print(g["events"][0]["rsvps"])
