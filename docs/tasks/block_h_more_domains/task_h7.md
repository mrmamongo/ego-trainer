# Задача H7: Комбо-система

**Блок:** H — Игры
**Сложность:** medium
**Темы:** combo, последовательности, счётчик, условный урон

## Условие

Боевая система считает комбо: каждое третье попадание подряд наносит двойной урон, а промах сбрасывает счётчик комбо. Функция по списку попаданий вычисляет суммарный урон и максимальное число попаданий подряд.

## Аргументы

- `hits` — список `True`/`False` (попадание / промах): `[True, True, False, True, True, True, False, True]`
- `base_damage` — базовый урон за попадание (по умолчанию `10`)

## Возвращает

Словарь: `{"total_damage": N, "max_combo": N}`, где `max_combo` — максимальное число попаданий подряд.

## Правила

- `combo_counter` начинает с `0`.
- Для каждого удара:
  - если попадание (`True`): `combo_counter += 1`; если `combo_counter % 3 == 0` — урон `= base_damage * 2` (комбо!), иначе урон `= base_damage`.
  - если промах (`False`): `combo_counter = 0` (сброс!), урон `= 0`.
- `max_combo` — максимальное значение `combo_counter` за всю серию.

## Пример

```python
hits = [True, True, True, False, True, True, True, True]
base_damage = 10
# Серия 1: 10, 10, 20 (комбо) → 40, потом промах сбрасывает
# Серия 2: 10, 10, 20 (комбо), 10 → 50
# total_damage = 90, max_combo = 4
# → {"total_damage": 90, "max_combo": 4}
```

<details>
<summary>Эталонное решение</summary>

```python
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
```

</details>
