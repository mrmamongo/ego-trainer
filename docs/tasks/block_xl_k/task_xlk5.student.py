"""Задача K5: Аукцион — найди баг (целочисленное деление)

Блок: XL-K — Игровая обвязка (MMO)
Сложность: medium
Тип: найди баг
Темы: аукцион, сортировка, деление, отладка

== УСЛОВИЕ ==

Ниже функция sort_lots сортирует лоты аукциона по возрастанию
цены за единицу (unit_price = price / quantity).

Баги:
  1) Используется целочисленное деление (//) — теряется точность,
     лоты с дробной unit_price сортируются неправильно
  2) При равенстве unit_price вторичный ключ — name, но сортировка
     должна быть по убыванию name (Z -> A), а не по возрастанию
  3) Функция мутирует входной список (sort in-place) — нужно вернуть копию

== АРГУМЕНТЫ ==

- lots — список dict: [{"name": str, "price": int, "quantity": int}, ...]

== ВОЗВРАЩАЕТ ==

Новый отсортированный список (не мутирует вход).
Сортировка: по возрастанию unit_price, при равенстве — по убыванию name.

== ПРАВИЛА ==

- unit_price = price / quantity (float, не целочисленное).
- Входной список не мутируется.

== ПРИМЕР ==

  lots = [
      {"name": "Sword", "price": 100, "quantity": 3},
      {"name": "Shield", "price": 100, "quantity": 2},
      {"name": "Potion", "price": 50, "quantity": 1},
  ]
  sort_lots(lots)
  # -> [Potion(50.0), Shield(50.0), Sword(33.33)]
  #    Potion и Shield: unit_price 50.0, но Shield > Potion по name (Z>A)

НАЙДИ И ИСПРАВЬ БАГИ. Не переписывай функцию с нуля — только исправления.
"""


def sort_lots(lots):
    """Сортирует лоты по unit_price (float), при равенстве — name по убыванию."""
    return sorted(lots, key=lambda lot: (lot["price"] // lot["quantity"], lot["name"]))


def task_xlk5_sort_lots(lots):
    # Вызови исправленный sort_lots, исправив баги выше
    return sort_lots(lots)
