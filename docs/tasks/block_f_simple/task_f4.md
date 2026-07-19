# Задача F4: Все ли тесты пройдены

**Блок:** F — Базовые паттерны
**Сложность:** easy
**Темы:** all, early exit

## Условие

CI/CD пайплайн проверяет, что все автотесты прошли успешно.
Функция возвращает `True`, если каждый тест имеет результат `"passed"`, иначе `False`.

## Аргументы

- `tests` — список словарей вида `[{"name": "test_login", "result": "passed"}, ...]`

## Возвращает

`True` — если все тесты имеют `result == "passed"`.
`False` — если хотя бы один тест не `"passed"`.
Если список пустой — верни `True`.

## Правила

- `True` — если ВСЕ тесты имеют `result == "passed"`.
- `False` — если хотя бы один не `"passed"`.
- Если список пустой — верни `True`.

## Пример

```python
tests = [
    {"name": "test_login", "result": "passed"},
    {"name": "test_logout", "result": "passed"},
    {"name": "test_payment", "result": "passed"},
]

task_f4_all_passed(tests)
# -> True
```

<details>
<summary>Эталонное решение</summary>

```python
def task_f4_all_passed(tests):
    for t in tests:
        if t["result"] != "passed":
            return False
    return True
```

</details>
