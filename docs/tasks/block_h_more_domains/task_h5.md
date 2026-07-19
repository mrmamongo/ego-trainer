# Задача H5: Ап уровней от набранного XP

**Блок:** H — Игры
**Сложность:** medium
**Темы:** XP, уровни, цикл while, формулы прогрессии

## Условие

Персонаж получает опыт, и если накопленного XP хватает для перехода на следующий уровень — он повышает уровень, а требование XP растёт с каждым уровнем. Функция должна накрутить все доступные апы уровней и вернуть финальный уровень, остаток XP и число полученных уровней.

## Аргументы

- `current_level` — текущий уровень (целое число)
- `current_xp` — текущий остаток XP (целое число)
- `xp_gained` — сколько XP получили (целое число)
- `base_xp` — базовое требование (по умолчанию `100`)
- `increment` — прирост за уровень (по умолчанию `50`)

## Возвращает

Словарь: `{"new_level": N, "remaining_xp": N, "levels_gained": N}`

## Правила

- Формула XP для уровня `L`: `required = base_xp + L * increment`.
- `total_xp = current_xp + xp_gained`.
- Пока `total_xp >= required` для текущего уровня:
  - `total_xp -= required`
  - `level += 1`
  - `required = base_xp + level * increment` (пересчёт!)
- `levels_gained` — на сколько уровней вырос персонаж.

## Пример

```python
current_level = 2
current_xp = 50
xp_gained = 400
base_xp = 100
increment = 50
# L=2: required=200, 450>=200 → xp=250, level=3, gained=1
# L=3: required=250, 250>=250 → xp=0,   level=4, gained=2
# L=4: required=300, 0<300 → стоп
# → {"new_level": 4, "remaining_xp": 0, "levels_gained": 2}
```

<details>
<summary>Эталонное решение</summary>

```python
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
```

</details>
