# Задача G7: Top-k sampling

**Блок:** G — NLP пайплайн
**Сложность:** easy
**Темы:** top-k, sampling, logits

## Условие

Модель выдала «вероятности» (logits) для каждого токена. Для top-k sampling оставляем только `k` самых высоких значений, остальные обнуляем (заменяем на `-inf`), чтобы они не могли быть выбраны при сэмплировании.

## Аргументы

- `logits` — словарь: токен -> число (score):
```python
{"cat": 2.5, "dog": 1.2, "bird": 0.1, "fish": 3.0, "mouse": -0.5}
```
- `k` — сколько токенов оставить: `3`

## Возвращает

Словарь той же структуры, где:
- `k` самых высоких значений оставлены как есть;
- остальные заменены на `-inf` (`float('-inf')`).

## Правила

- Найти k-е по величине значение (threshold).
- Пройти по словарю: если `value >= threshold` — оставить, иначе `-inf`.
- Для равных значений — брать любые `k`.
- Если словарь пустой или `k <= 0` — все значения заменить на `-inf`.

## Пример

```python
>>> task_g7_top_k_filter({"cat": 2.5, "dog": 1.2, "bird": 0.1}, 2)
{"cat": 2.5, "dog": 1.2, "bird": float("-inf")}
```

<details>
<summary>Эталонное решение</summary>

```python
def task_g7_top_k_filter(logits, k):
    if not logits or k <= 0:
        return {token: float("-inf") for token in logits}
    sorted_values = sorted(logits.values(), reverse=True)
    threshold = sorted_values[min(k, len(sorted_values)) - 1]
    return {
        token: (value if value >= threshold else float("-inf"))
        for token, value in logits.items()
    }
```

</details>
