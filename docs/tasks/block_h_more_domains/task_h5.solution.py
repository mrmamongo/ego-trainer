def task_h5_xp_level_up(current_level, current_xp, xp_gained, base_xp=100, increment=50):
    level = current_level
    xp = current_xp + xp_gained
    gained = 0
    while True:
        required = base_xp + level * increment
        if xp >= required:
            xp -= required
            level += 1
            gained += 1
        else:
            break
    return {"new_level": level, "remaining_xp": xp, "levels_gained": gained}
