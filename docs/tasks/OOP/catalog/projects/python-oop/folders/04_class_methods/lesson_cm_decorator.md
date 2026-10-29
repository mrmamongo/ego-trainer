---
id: cm-decorator
title: "Декоратор: функция над функцией"
order: 2
version: "1.0.0"
---

# Декоратор: функция над функцией

Иногда функции нужно добавить поведение «вокруг» — посчитать вызовы, записать в журнал, поправить ответ, — не переписывая саму функцию. Для этого пишут **декоратор**: функцию, которая принимает функцию и возвращает новую.

```python
def count_calls(func):                          # 1
    def wrapper(*args):                         # 2
        wrapper.calls = wrapper.calls + 1       # 3
        return func(*args)                      # 4
    wrapper.calls = 0                           # 5
    return wrapper                              # 6
```

Три шага, всегда одни и те же:

1. Внутри объявляем **обёртку** `wrapper`. Она делает свою добавку (строка 3) и вызывает настоящую `func` (строка 4). Результат нужно **вернуть**: `return func(*args)`.
2. Прикрепляем к обёртке начальное состояние (строка 5), как в предыдущей карточке.
3. Возвращаем саму обёртку, **без скобок** (строка 6).

`*args` в `def wrapper(*args)` значит «собери все переданные аргументы в кортеж `args`», а `func(*args)` значит «раскрой кортеж обратно в аргументы». Так обёртка подходит к функции с любым числом параметров.

## Знак @

Запись с `@` — короткий способ применить декоратор:

```python
@count_calls
def add(a, b):
    return a + b
```

Это ровно то же самое, что

```python
def add(a, b):
    return a + b
add = count_calls(add)       # имя add теперь указывает на wrapper
```

| Что выполнилось | `add.calls` | Что вернулось |
|---|---|---|
| `add = count_calls(add)` | `0` | |
| `add(2, 3)` | `1` | `5` |
| `add(10, 20)` | `2` | `30` |

Вызывая `add`, ты на самом деле вызываешь `wrapper`, а он уже вызывает исходную функцию.

В реальных проектах над `wrapper` ещё пишут `@functools.wraps(func)`: он переносит на обёртку имя и описание исходной функции. В учебных задачах он не нужен.

## Частые ошибки

Забыть вернуть обёртку:

```python
def count_calls(func):
    def wrapper(*args):
        return func(*args)
    # забыли return wrapper: декоратор вернёт None
```

После `add = count_calls(add)` в `add` окажется `None`, и первый же вызов даст `TypeError: 'NoneType' object is not callable`.

Забыть вернуть результат:

```python
def wrapper(*args):
    func(*args)              # неверно: ответ потерян, вызов вернёт None
```

```python
def wrapper(*args):
    return func(*args)       # верно
```

Поставить скобки при возврате: `return wrapper()` запустит обёртку сразу, а нужна сама функция: `return wrapper`.

## Для любопытных: декоратор с аргументами

Если декоратору нужен параметр (`@repeat(3)`), добавляют ещё один слой функций:

```python
def repeat(n):                       # получает параметр
    def decorator(func):             # это и есть настоящий декоратор
        def wrapper(*args):
            for _ in range(n):
                result = func(*args)
            return result
        return wrapper
    return decorator
```

`@repeat(3)` значит `f = repeat(3)(f)`. В задачах этой папки такие декораторы не нужны.

## Проверь себя

```python
def twice(func):
    def wrapper(x):
        return func(func(x))
    return wrapper

@twice
def inc(n):
    return n + 1
```

1. Чему равно `inc(5)`?
2. Что будет в `inc`, если из `twice` убрать последнюю строку `return wrapper`?

<details><summary>Ответ</summary>

1. `7`: `inc` теперь `wrapper`, он применяет исходную функцию два раза: `5 -> 6 -> 7`.
2. `None`: декоратор ничего не вернул, и вызов `inc(5)` упадёт с `TypeError`.

</details>
