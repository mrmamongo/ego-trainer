def task_h7_combo_system(hits, base_damage=10):
    combo = 0
    max_combo = 0
    total = 0
    for hit in hits:
        if hit:
            combo += 1
            max_combo = max(max_combo, combo)
            if combo % 3 == 0:
                total += base_damage * 2
            else:
                total += base_damage
        else:
            combo = 0
    return {"total_damage": total, "max_combo": max_combo}
