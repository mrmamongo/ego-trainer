# Задача F2: Email'ы активных пользователей

**Блок:** F — Базовые паттерны
**Сложность:** easy
**Темы:** filter, list comprehension

## Условие

CRM хранит список пользователей с признаком активности.
Функция отбирает только активных пользователей и возвращает их email'ы в исходном порядке.

## Аргументы

- `users` — список словарей вида `[{"name": "Ivan", "email": "ivan@test.com", "active": True}, ...]`

## Возвращает

Список строк — email'ы только тех пользователей, у кого `active == True`.
Порядок сохраняется таким же, как во входном списке.

## Правила

- Верни список email'ов (строк) только тех, у кого `active == True`.
- Порядок: как во входном списке.

## Пример

```python
users = [
    {"name": "Ivan", "email": "ivan@test.com", "active": True},
    {"name": "Anna", "email": "anna@test.com", "active": False},
    {"name": "Boris", "email": "boris@test.com", "active": True},
    {"name": "Clara", "email": "clara@test.com", "active": False},
    {"name": "Dmitry", "email": "dmitry@test.com", "active": True},
]

task_f2_active_emails(users)
# -> ["ivan@test.com", "boris@test.com", "dmitry@test.com"]
```

<details>
<summary>Эталонное решение</summary>

```python
def task_f2_active_emails(users):
    return [u["email"] for u in users if u["active"]]
```

</details>
