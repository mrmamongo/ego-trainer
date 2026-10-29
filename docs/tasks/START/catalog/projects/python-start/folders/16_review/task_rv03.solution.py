def task_rv03_check_username(raw):
    name = raw.strip().lower()
    if len(name) < 3:
        return "too_short"
    allowed = "abcdefghijklmnopqrstuvwxyz0123456789_"
    for char in name:
        if char not in allowed:
            return "bad_char"
    return "ok"
