# Задача H3: Показатель силы персонажа

**Блок:** H — Игры
**Сложность:** medium
**Темы:** power score, классы, вложенные словари, формулы

## Условие

У каждого персонажа есть класс и набор характеристик. Основной атрибут зависит от класса и считается вдвойне, остальные — однократно. Функция вычисляет показатель силы (power score) персонажа по заданной формуле.

## Аргументы

- `character` — словарь вида `{"name": "Warrior", "class": "warrior", "stats": {"str": 15, "agi": 8, "int": 4, "vit": 10}}`

## Возвращает

Целое число — power score.

## Правила

- Основной атрибут по классу:
  - `warrior` → `str`
  - `mage` → `int`
  - `rogue` → `agi`
  - (неизвестный класс → `str`)
- Формула: `power = основной_стат × 2 + sum(остальные_статы)`

## Пример

```python
character = {
    "name": "Warrior",
    "class": "warrior",
    "stats": {"str": 15, "agi": 8, "int": 4, "vit": 10},
}
# Warrior (str основной): 15×2 + 8 + 4 + 10 = 52
# → 52
```

<details>
<summary>Эталонное решение</summary>

```python
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
```

</details>
