# Задача H8: Каскадный синтез

**Блок:** H — Игры
**Сложность:** medium
**Темы:** синтез, редкости, целочисленное деление, каскад

## Условие

В крафтовой системе три редкости: Common (C), Uncommon (U) и Rare (R). Из трёх Common синтезируется один Uncommon, а из трёх Uncommon — один Rare, причём синтез каскадный: созданные из Common единицы сразу участвуют в подсчёте Uncommon для синтеза Rare. Функция пересчитывает инвентарь по этим правилам.

## Аргументы

- `inventory` — словарь предметов по редкостям:
```python
{
    "Iron Ore": {"C": 9, "U": 2, "R": 0},
    "Herb":     {"C": 5, "U": 1, "R": 0},
}
```

## Возвращает

Словарь той же структуры с обновлёнными значениями:
```python
{
    "Iron Ore": {"C": 0, "U": 2, "R": 1},
    "Herb":     {"C": 2, "U": 2, "R": 0},
}
```

## Правила

- Для каждого предмета:
  1. `u_crafted = C // 3`, `c_rem = C % 3`
  2. `total_u = U + u_crafted`
  3. `r_crafted = total_u // 3`, `u_rem = total_u % 3`
  4. Итог: `{"C": c_rem, "U": u_rem, "R": R + r_crafted}`
- Каскад: синтезированные Uncommon сразу учитываются при синтезе Rare.

## Пример

```python
inventory = {
    "Iron Ore": {"C": 9, "U": 2, "R": 0},
    "Herb":     {"C": 5, "U": 1, "R": 0},
}
# Iron Ore: u_crafted=3, c_rem=0, total_u=5, r_crafted=1, u_rem=2 → {C:0, U:2, R:1}
# Herb:     u_crafted=1, c_rem=2, total_u=2, r_crafted=0, u_rem=2 → {C:2, U:2, R:0}
# → {"Iron Ore": {"C": 0, "U": 2, "R": 1}, "Herb": {"C": 2, "U": 2, "R": 0}}
```

<details>
<summary>Эталонное решение</summary>

```python
def task_h8_tiered_synthesis(inventory):
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
```

</details>
