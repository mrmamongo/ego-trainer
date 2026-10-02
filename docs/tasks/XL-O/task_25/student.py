"""XL-O-25 — Cooldown и очередь действий (правка).

Реализуй process_actions(actions, now, resources). Умение имеет name, cost,
cooldown и cast_time. Соблюдай global cooldown, локальный cooldown, наличие
ресурсов и порядок очереди. При смерти игрока отменяй оставшиеся действия.
Верни список событий с status success/rejected/cancelled и reason. now —
переданное число времени, не системные часы.
"""


def process_actions(actions, now, resources):
    # TODO: реализовать state machine очереди
    raise NotImplementedError
