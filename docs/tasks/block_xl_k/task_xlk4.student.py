"""Задача K4: Crafting с альтернативными ингредиентами — улучши код

Блок: XL-K — Игровая обвязка (MMO)
Сложность: medium
Тип: улучши код (добавь функционал)
Темы: crafting, рецепты, валидация, словари

== УСЛОВИЕ ==

Функция can_craft ниже проверяет, есть ли у игрока все ингредиенты
из рецепта recipe в инвентаре inventory.

Нужно улучшить её:
  1) Поддержать альтернативные ингредиенты: в рецепте значение может
     быть списком — подходит ЛЮБОЙ из перечисленных.
     Например: {"iron OR steel": ["iron", "steel"]}
  2) Если ингредиента нет вообще (ни один вариант) — вернуть False,
     а не кидать KeyError.
  3) Добавь docstring с описанием контракта.

== АРГУМЕНТЫ ==

- recipe — dict: {ингредиент: количество} или {ингредиент: [варианты]}
- inventory — dict: {предмет: количество}

== ВОЗВРАЩАЕТ ==

Bool: True — если можно скрафтить, False — иначе.

== ПРАВИЛА ==

- Количество в inventory должно быть >= требуемого.
- Для альтернатив: достаточно, чтобы ОДИН из вариантов был в inventory
  в нужном количестве.
- Пустой recipe → True (нечего проверять).

== ПРИМЕР ==

  can_craft({"iron": 2, "wood": 1}, {"iron": 3, "wood": 2})
  # -> True

  can_craft({"iron OR steel": ["iron", "steel"]}, {"steel": 5})
  # -> True  (есть steel)

  can_craft({"iron OR steel": ["iron", "steel"]}, {"wood": 10})
  # -> False (нет ни iron, ни steel)
"""


def can_craft(recipe, inventory):
    """Проверяет, можно ли скрафтить по рецепту с имеющимся инвентарём."""
    for ingredient, amount in recipe.items():
        if inventory.get(ingredient, 0) < amount:
            return False
    return True


def task_xlk4_can_craft(recipe, inventory):
    # Вызови улучшенный can_craft по условию
    return can_craft(recipe, inventory)
