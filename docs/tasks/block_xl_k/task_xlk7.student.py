"""Задача K7: Экономика — инфляция цен NPC

Блок: XL-K — Игровая обвязка (MMO)
Сложность: hard
Тип: написать новый код
Темы: экономика, инфляция, игровая экономика, математика

== УСЛОВИЕ ==

В MMO цены у торговцев NPC зависят от количества золота в обращении
(всех игроков вместе). Если золота слишком много — цены растут (инфляция).

Формула новой цены:
  new_price = base_price * (1 + gold_in_circulation / gold_threshold * rate)
  new_price округляется ВВЕРХ до целого.

Если gold_in_circulation <= gold_threshold — цена не меняется (new_price = base_price).

== АРГУМЕНТЫ ==

- base_price — int, базовая цена предмета
- gold_in_circulation — int, всего золота у всех игроков
- gold_threshold — int, порог, выше которого начинается инфляция
- rate — float, коэффициент инфляции (например, 0.1 = 10% за превышение)

== ВОЗВРАЩАЕТ ==

Int — новая цена (>= base_price).

== ПРАВИЛА ==

- gold_in_circulation <= gold_threshold -> new_price = base_price.
- new_price округляется ВВЕРХ (ceil), даже если дробная часть маленькая.
- Пустой base_price = 0 -> 0.

== ПРИМЕР ==

  adjust_price(100, 15000, 10000, 0.1)
  # -> 100 * (1 + 15000/10000 * 0.1) = 100 * 1.15 = 115.0 -> ceil = 115

  adjust_price(100, 5000, 10000, 0.1)
  # -> 100  (золота меньше порога, цена не меняется)
"""


def task_xlk7_adjust_price(base_price, gold_in_circulation, gold_threshold, rate):
    # ТВОЙ КОД ЗДЕСЬ
    pass
