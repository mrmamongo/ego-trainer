#!/usr/bin/env python3
"""
student.py — ТВОЙ файл. Пиши решения здесь.

Блок H: 8 задач в игровом сеттинге.

Запуск проверки:
    python checker.py
"""


def task_h1_inventory_stack(items):
    """
    H1. Складываем стаки предметов

    Аргументы:
        items — список словарей:
        [{"name": "Iron Ore", "qty": 5}, {"name": "Iron Ore", "qty": 3}, ...]

    Верни:
        Словарь: name -> суммарное qty.
        {"Iron Ore": 8, "Herb": 12}
    """
    pass


def task_h2_loot_drop(drops, seed=42):
    """
    H2. Таблица дропа с шансами

    Аргументы:
        drops — список словарей:
        [{"item": "Gold", "chance": 100, "min": 5, "max": 15},
         {"item": "Iron Dagger", "chance": 30, "min": 1, "max": 1}]
        seed  — seed для random (фиксированный для проверки)

    Верни:
        Словарь: item -> сколько выпало (0 если не выпало).
        {"Gold": 12, "Iron Dagger": 0}

    Алгоритм:
        1. Зафиксировать random.seed(seed)
        2. Для каждого дропа: random.randint(1, 100) <= chance → выпало
        3. Если выпало → random.randint(min, max) = количество
        4. Если не выпало → 0
    """
    pass


def task_h3_power_score(character):
    """
    H3. Показатель силы персонажа

    Аргументы:
        character — словарь:
        {"name": "Warrior", "class": "warrior",
         "stats": {"str": 15, "agi": 8, "int": 4, "vit": 10}}

    Основной атрибут по классу:
        warrior  → str
        mage     → int
        rogue    → agi

    Формула:
        power = основной_стат × 2 + sum(остальные_статы)

    Верни:
        Целое число — power score.

    Пример:
        Warrior (str основной): 15×2 + 8 + 4 + 10 = 52
    """
    pass


def task_h4_backpack(items, capacity):
    """
    H4. Рюкзак: взять максимум ценного

    Аргументы:
        items — список словарей, отсортированных по убыванию ценность/вес:
        [{"name": "Sword", "weight": 3, "value": 150},
         {"name": "Shield", "weight": 5, "value": 120},
         {"name": "Potion", "weight": 1, "value": 40}]
        capacity — максимальный вес рюкзака

    Алгоритм (жадный):
        Берём предметы по порядку, пока влезает по весу.
        Если не влезает — пропускаем, идём к следующему.

    Верни:
        Словарь:
        {
            "taken": [{"name": "Sword", "weight": 3, "value": 150}, ...],
            "total_weight": N,
            "total_value": N,
            "remaining_capacity": N
        }
    """
    pass


def task_h5_xp_level_up(current_level, current_xp, xp_gained, base_xp=100, increment=50):
    """
    H5. Ап уровней от набранного XP

    Формула XP для уровня L:
        required = base_xp + L * increment

    Аргументы:
        current_level — текущий уровень
        current_xp    — текущий остаток XP
        xp_gained     — сколько XP получили
        base_xp       — базовое требование (по умолчанию 100)
        increment     — прирост за уровень (по умолчанию 50)

    Алгоритм:
        1. total_xp = current_xp + xp_gained
        2. while total_xp >= required для текущего уровня:
               total_xp -= required
               level += 1
               required = base_xp + level * increment  (пересчёт!)
        3. Вернуть результат

    Верни:
        {"new_level": N, "remaining_xp": N, "levels_gained": N}
    """
    pass


def task_h6_reward_split(items, players):
    """
    H6. Делим лут между игроками (round-robin)

    Аргументы:
        items   — список строк (названий предметов):
        ["Sword", "Shield", "Potion", "Ring", "Gem"]
        players — список строк (имён игроков):
        ["Anna", "Boris", "Clara"]

    Алгоритм:
        1-й предмет → 1-й игрок, 2-й → 2-й, 3-й → 3-й,
        4-й → снова 1-й, 5-й → 2-й, и так далее.

    Верни:
        Словарь: player -> список предметов.
        {"Anna": ["Sword", "Ring"], "Boris": ["Shield", "Gem"], "Clara": ["Potion"]}
    """
    pass


def task_h7_combo_system(hits, base_damage=10):
    """
    H7. Комбо-система: каждое 3-е попадание подряд = двойной урон

    Аргументы:
        hits — список True/False (попадание / промах):
        [True, True, False, True, True, True, False, True]
        base_damage — базовый урон за попадание

    Алгоритм:
        combo_counter = 0
        Для каждого удара:
            if hit:
                combo_counter += 1
                if combo_counter % 3 == 0:
                    урон = base_damage * 2  (комбо!)
                else:
                    урон = base_damage
            else:
                combo_counter = 0  (сброс!)
                урон = 0

    Верни:
        {"total_damage": N, "max_combo": N}
        max_combo — максимальное число попаданий подряд.
    """
    pass


def task_h8_tiered_synthesis(inventory):
    """
    H8. Каскадный синтез: 3C → 1U, 3U → 1R

    Аргументы:
        inventory — словарь предметов по редкостям:
        {
            "Iron Ore": {"C": 9, "U": 2, "R": 0},
            "Herb":     {"C": 5, "U": 1, "R": 0},
        }

    Алгоритм для КАЖДОГО предмета:
        1. u_crafted = C // 3,  c_rem = C % 3
        2. total_u = U + u_crafted
        3. r_crafted = total_u // 3,  u_rem = total_u % 3
        4. Итог: {"C": c_rem, "U": u_rem, "R": R + r_crafted}

    Верни:
        Словарь той же структуры с обновлёнными значениями.
        {
            "Iron Ore": {"C": 0, "U": 2, "R": 1},
            "Herb":     {"C": 2, "U": 2, "R": 0},
        }
    """
    pass
