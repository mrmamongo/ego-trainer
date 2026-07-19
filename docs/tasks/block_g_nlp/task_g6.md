# Задача G6: Padding

**Блок:** G — NLP пайплайн
**Сложность:** easy
**Темы:** padding, attention_mask, батч

## Условие

Модель принимает только прямоугольные матрицы. Если в батче тексты разной длины — дописываем `pad_token` в конец коротких. Ещё создаём `attention_mask`: `1` — настоящий токен, `0` — паддинг, чтобы модель игнорировала добавленные позиции.

## Аргументы

- `sequences` — список списков чисел (токенов):
```python
[[101, 234, 456], [101, 234], [101, 234, 456, 789]]
```
- `pad_token` — число, которым дописываем: `0`

## Возвращает

Словарь:
```python
{
    "padded": [
        [101, 234, 456, 0],
        [101, 234, 0, 0],
        [101, 234, 456, 789],
    ],
    "attention_mask": [
        [1, 1, 1, 0],
        [1, 1, 0, 0],
        [1, 1, 1, 1],
    ]
}
```

## Правила

- `max_len` = длина самой длинной последовательности в батче.
- Короткие последовательности дописываем `pad_token`'ами в конец до `max_len`.
- `attention_mask`: `1` для настоящих токенов, `0` для паддинга.
- Если батч пустой — вернуть `{"padded": [], "attention_mask": []}`.

## Пример

```python
>>> task_g6_pad_batch([[101, 234, 456], [101, 234], [101, 234, 456, 789]], 0)
{
    "padded": [
        [101, 234, 456, 0],
        [101, 234, 0, 0],
        [101, 234, 456, 789],
    ],
    "attention_mask": [
        [1, 1, 1, 0],
        [1, 1, 0, 0],
        [1, 1, 1, 1],
    ],
}
```

<details>
<summary>Эталонное решение</summary>

```python
def task_g6_pad_batch(sequences, pad_token):
    if not sequences:
        return {"padded": [], "attention_mask": []}
    max_len = max(len(seq) for seq in sequences)
    padded = []
    masks = []
    for seq in sequences:
        pad_count = max_len - len(seq)
        padded.append(seq + [pad_token] * pad_count)
        masks.append([1] * len(seq) + [0] * pad_count)
    return {"padded": padded, "attention_mask": masks}
```

</details>
