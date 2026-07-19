# Задача H6: Делим лут между игроками

**Блок:** H — Игры
**Сложность:** medium
**Темы:** round-robin, распределение, словари списков

## Условие

После боя нужно поделить добычу между игроками по принципу round-robin: первый предмет уходит первому игроку, второй — второму и так далее, а когда игроки заканчиваются — счётчик возвращается к первому. Функция возвращает, кому какой предмет достался.

## Аргументы

- `items` — список строк (названий предметов): `["Sword", "Shield", "Potion", "Ring", "Gem"]`
- `players` — список строк (имён игроков): `["Anna", "Boris", "Clara"]`

## Возвращает

Словарь: `player` -> список предметов. Например: `{"Anna": ["Sword", "Ring"], "Boris": ["Shield", "Gem"], "Clara": ["Potion"]}`

## Правила

- 1-й предмет → 1-й игрок, 2-й → 2-й, 3-й → 3-й, 4-й → снова 1-й, 5-й → 2-й и так далее.
- Каждый игрок из списка должен присутствовать в результате (с пустым списком, если ему ничего не досталось).

## Пример

```python
items = ["Sword", "Shield", "Potion", "Ring", "Gem"]
players = ["Anna", "Boris", "Clara"]
# → {"Anna": ["Sword", "Ring"], "Boris": ["Shield", "Gem"], "Clara": ["Potion"]}
```

<details>
<summary>Эталонное решение</summary>

```python
def task_h6_reward_split(items, players):
    result = {p: [] for p in players}
    for i, item in enumerate(items):
        result[players[i % len(players)]].append(item)
    return result
```

</details>
