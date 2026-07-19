# Задача G4: Accuracy

**Блок:** G — NLP пайплайн
**Сложность:** easy
**Темы:** accuracy, метрики, доля совпадений

## Условие

Есть список предсказаний модели и список правильных ответов. Посчитай долю совпадений — это базовая метрика качества классификации.

## Аргументы

- `predicted` — список строк: `["cat", "dog", "cat", "bird"]`
- `actual` — список строк: `["cat", "cat", "cat", "bird"]`

## Возвращает

`float` от `0.0` до `1.0` — доля совпадений. Если списки пустые — верни `0.0`.

## Правила

- Доля совпадений = количество совпадений / общее количество.
- Если список пустой — вернуть `0.0`.

## Пример

```python
>>> task_g4_compute_accuracy(["a", "b", "c"], ["a", "x", "c"])
0.666666...  # 2 из 3 совпали
```

<details>
<summary>Эталонное решение</summary>

```python
def task_g4_compute_accuracy(predicted, actual):
    if not predicted:
        return 0.0
    correct = sum(1 for p, a in zip(predicted, actual) if p == a)
    return correct / len(predicted)
```

</details>
