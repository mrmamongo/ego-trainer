#!/usr/bin/env python3
"""
checker.py — ПРОВЕРЯЮЩИЙ скрипт. Не редактируй.

Запуск:
    python checker.py
"""

import sys
import traceback
import random

# --- Импорт функций студента ---
try:
    import student
except Exception as e:
    print(f"❌ Не удалось импортировать student.py: {e}")
    sys.exit(1)


# =============================================================================
# ЭТАЛОННЫЕ РЕШЕНИЯ
# =============================================================================

def _ref_h1(items):
    result = {}
    for item in items:
        n = item["name"]
        result[n] = result.get(n, 0) + item["qty"]
    return result


def _ref_h2(drops, seed=42):
    rng = random.Random(seed)
    result = {}
    for d in drops:
        roll = rng.randint(1, 100)
        if roll <= d["chance"]:
            result[d["item"]] = rng.randint(d["min"], d["max"])
        else:
            result[d["item"]] = 0
    return result


def _ref_h3(character):
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


def _ref_h4(items, capacity):
    taken = []
    total_w = 0
    total_v = 0
    for item in items:
        if total_w + item["weight"] <= capacity:
            taken.append(item)
            total_w += item["weight"]
            total_v += item["value"]
    return {
        "taken": taken,
        "total_weight": total_w,
        "total_value": total_v,
        "remaining_capacity": capacity - total_w,
    }


def _ref_h5(current_level, current_xp, xp_gained, base_xp=100, increment=50):
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


def _ref_h6(items, players):
    result = {p: [] for p in players}
    for i, item in enumerate(items):
        result[players[i % len(players)]].append(item)
    return result


def _ref_h7(hits, base_damage=10):
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


def _ref_h8(inventory):
    result = {}
    for name, tiers in inventory.items():
        c, u, r = tiers["C"], tiers["U"], tiers["R"]
        u_crafted = c // 3
        c_rem = c % 3
        total_u = u + u_crafted
        r_crafted = total_u // 3
        u_rem = total_u % 3
        result[name] = {"C": c_rem, "U": u_rem, "R": r + r_crafted}
    return result


# =============================================================================
# ТЕСТЫ
# =============================================================================

def run_check(name, func_name, test_cases):
    full = f"H{name}"
    if not hasattr(student, func_name):
        return (full, False, [f"Функция {func_name} не найдена"])
    details = []
    all_ok = True
    for inp, expected, desc in test_cases:
        try:
            result = getattr(student, func_name)(*inp)
        except Exception:
            result = None
            error = traceback.format_exc()
        if result is None:
            details.append(f"✗ {desc}: Вернуло None")
            all_ok = False
            continue
        if isinstance(result, float) and isinstance(expected, float):
            ok = abs(result - expected) < 0.0001
        else:
            ok = result == expected
        if ok:
            details.append(f"✓ {desc}: {result}")
        else:
            details.append(f"✗ {desc}: ожидалось {expected}, получено {result}")
            all_ok = False
    return (full, all_ok, details)


def main():
    print("=" * 60)
    print("  БЛОК H: 8 задач в игровом сеттинге")
    print("=" * 60)
    print()

    checks = [
        run_check("1", "task_h1_inventory_stack", [
            (([
                {"name": "Iron Ore", "qty": 5},
                {"name": "Iron Ore", "qty": 3},
                {"name": "Herb", "qty": 7},
            ],), {"Iron Ore": 8, "Herb": 7}, "2 предмета"),
            (([],), {}, "пустой"),
            (([{"name": "Gem", "qty": 10}],), {"Gem": 10}, "один предмет"),
        ]),
        run_check("2", "task_h2_loot_drop", [
            (([
                {"item": "Gold", "chance": 100, "min": 5, "max": 15},
                {"item": "Dagger", "chance": 30, "min": 1, "max": 1},
            ],), _ref_h2([
                {"item": "Gold", "chance": 100, "min": 5, "max": 15},
                {"item": "Dagger", "chance": 30, "min": 1, "max": 1},
            ]), "2 дропа"),
            (([],), {}, "пустой"),
        ]),
        run_check("3", "task_h3_power_score", [
            (({"name": "Warrior", "class": "warrior",
               "stats": {"str": 15, "agi": 8, "int": 4, "vit": 10}},), 52, "warrior"),
            (({"name": "Mage", "class": "mage",
               "stats": {"str": 4, "agi": 6, "int": 18, "vit": 5}},), 51, "mage"),
            (({"name": "Rogue", "class": "rogue",
               "stats": {"str": 8, "agi": 16, "int": 6, "vit": 7}},), 53, "rogue"),
        ]),
        run_check("4", "task_h4_backpack", [
            (([
                {"name": "Sword", "weight": 3, "value": 150},
                {"name": "Shield", "weight": 5, "value": 120},
                {"name": "Potion", "weight": 1, "value": 40},
            ], 8), _ref_h4([
                {"name": "Sword", "weight": 3, "value": 150},
                {"name": "Shield", "weight": 5, "value": 120},
                {"name": "Potion", "weight": 1, "value": 40},
            ], 8), "capacity 8"),
            (([
                {"name": "Heavy", "weight": 10, "value": 100},
            ], 5), _ref_h4([
                {"name": "Heavy", "weight": 10, "value": 100},
            ], 5), "не влезает"),
            (([], 10), _ref_h4([], 10), "пустой инвентарь"),
        ]),
        run_check("5", "task_h5_xp_level_up", [
            ((2, 50, 400, 100, 50), _ref_h5(2, 50, 400, 100, 50), "уровень 2, 400 XP"),
            ((5, 0, 0, 100, 50), _ref_h5(5, 0, 0, 100, 50), "0 XP"),
            ((1, 0, 250, 100, 50), _ref_h5(1, 0, 250, 100, 50), "ровно на 1 ап"),
        ]),
        run_check("6", "task_h6_reward_split", [
            ((["Sword", "Shield", "Potion", "Ring", "Gem"],
              ["Anna", "Boris", "Clara"]),
             _ref_h6(["Sword", "Shield", "Potion", "Ring", "Gem"], ["Anna", "Boris", "Clara"]),
             "5 предметов, 3 игрока"),
            (([], ["Anna", "Boris"]), _ref_h6([], ["Anna", "Boris"]), "пустой лут"),
            ((["Gold"], ["Solo"]), _ref_h6(["Gold"], ["Solo"]), "1 игрок"),
        ]),
        run_check("7", "task_h7_combo_system", [
            (([True, True, True, False, True, True, True, True], 10),
             _ref_h7([True, True, True, False, True, True, True, True], 10),
             "два комбо"),
            (([True, True, False, True, False, True], 10),
             _ref_h7([True, True, False, True, False, True], 10),
             "без комбо"),
            (([], 10), _ref_h7([], 10), "пустой"),
        ]),
        run_check("8", "task_h8_tiered_synthesis", [
            (({
                "Iron Ore": {"C": 9, "U": 2, "R": 0},
                "Herb": {"C": 5, "U": 1, "R": 0},
            },), _ref_h8({
                "Iron Ore": {"C": 9, "U": 2, "R": 0},
                "Herb": {"C": 5, "U": 1, "R": 0},
            }), "2 предмета"),
            (({"Gem": {"C": 2, "U": 0, "R": 0}},),
             _ref_h8({"Gem": {"C": 2, "U": 0, "R": 0}}), "не хватает"),
            (({"Ore": {"C": 27, "U": 0, "R": 0}},),
             _ref_h8({"Ore": {"C": 27, "U": 0, "R": 0}}), "идеальный каскад"),
        ]),
    ]

    passed = 0
    for name, ok, details in checks:
        icon = "✅" if ok else "❌"
        print(f"{icon} {name}")
        for d in details:
            print(f"   {d}")
        print()
        if ok:
            passed += 1

    print("=" * 60)
    if passed == len(checks):
        print(f"  🎉 Все {passed}/{len(checks)} задач пройдены!")
    else:
        print(f"  Пройдено: {passed}/{len(checks)}. Попробуй исправить ❌.")
    print("=" * 60)


if __name__ == "__main__":
    main()
