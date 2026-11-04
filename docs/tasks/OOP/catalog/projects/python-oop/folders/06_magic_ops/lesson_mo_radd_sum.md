---
id: mo-radd-sum
title: "__radd__ и sum() для своих объектов"
order: 3
version: "1.0.0"
---

# `__radd__` и `sum()` для своих объектов

Функция `sum` складывает элементы по очереди, а начинает с числа `0`: сначала считается `0 + первый`, потом результат `+ второй` и так далее. Для списка чисел это незаметно. Для списка твоих объектов первый шаг выглядит как `0 + Score(5)`: слева стоит обычное число.

Python сначала зовёт `int.__add__(0, score)`, получает `NotImplemented` и тогда пробует **зеркальный** метод правого операнда: `score.__radd__(0)`. Буква `r` значит «right» (правый). Если такого метода нет, будет `TypeError`.

```python
class Score:
    def __init__(self, points):
        self.points = points

    def __add__(self, other):
        if not isinstance(other, Score):
            return NotImplemented
        return Score(self.points + other.points)

    def __radd__(self, other):
        if other == 0:
            return self
        return NotImplemented

parts = [Score(5), Score(7)]       # 1
total = sum(parts)                 # 2
nothing = sum([])                  # 3
bad = 3 + Score(1)                 # 4
```

| Строка | Что произошло |
|---|---|
| 2 | `0 + Score(5)` зовёт `__radd__(0)`, получаем `Score(5)`; дальше `Score(5) + Score(7)` даёт `Score(12)` |
| 3 | пустой список: `sum` вернул просто `0`, объекта `Score` нет |
| 4 | `__radd__(3)`: это не ноль, вернулся `NotImplemented`, итог `TypeError` |

Метод принимает только `0`, потому что нужен лишь для старта `sum`. Складывать число и `Score` вообще мы не разрешаем.

Заодно: если нужно ещё `2 * vector`, пишут `__rmul__`. Он работает так же: число слева, объект справа. Часто достаточно строки `__rmul__ = __mul__` в классе.

## Частые ошибки

Забыть `__radd__`: тогда `sum(parts)` падает с `TypeError`, хотя `a + b` работает.

Написать `__radd__`, который всегда возвращает `self`: тогда `3 + Score(1)` молча даст `Score(1)`, и число `3` потеряется.

## Проверь себя

С классом `Score` выше:

1. Чему равно `sum([Score(2), Score(3), Score(4)]).points`?
2. Чему равно `sum([])`?
3. Что даст `sum([Score(1)], 10)`?

<details><summary>Ответ</summary>

1. `9`.
2. `0`: просто число, это не `Score`.
3. `TypeError`: начало `10` не равно `0`, поэтому `__radd__(10)` вернул `NotImplemented`.

</details>
