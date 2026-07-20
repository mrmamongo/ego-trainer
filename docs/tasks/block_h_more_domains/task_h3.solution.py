def task_h3_power_score(character):
    main_stat = {"warrior": "str", "mage": "int", "rogue": "agi"}.get(
        character["class"], "str"
    )
    stats = character["stats"]
    total = 0
    for stat, value in stats.items():
        if stat == main_stat:
            total += value * 2
        else:
            total += value
    return total
