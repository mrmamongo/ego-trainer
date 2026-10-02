# Задача Demo2: Чётное или нечётное

**Блок:** Demo
**Сложность:** easy
**Темы:** condition, modulo

## Условие

Напиши функцию `task_demo2_even_odd(n)`, которая принимает целое число и возвращает строку `"even"` если число чётное, и `"odd"` если нечётное.

## Аргументы

- `n` — целое число

## Возвращает

Строку — `"even"` или `"odd"`.

## Правила

- Используй оператор `%` для проверки чётности.
- Верни строку `"even"` или `"odd"`.

## Пример

```python
task_demo2_even_odd(4)
# -> "even"

task_demo2_even_odd(7)
# -> "odd"
```

<details>
<summary>Эталонное решение</summary>

```python
def task_demo2_even_odd(n):
    return "even" if n % 2 == 0 else "odd"
```

</details>
