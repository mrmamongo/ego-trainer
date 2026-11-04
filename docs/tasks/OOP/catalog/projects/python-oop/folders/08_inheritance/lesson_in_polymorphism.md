---
id: in-polymorphism
title: "Полиморфизм: один вызов, разное поведение"
order: 4
version: "1.0.0"
---

# Полиморфизм: один вызов, разное поведение

Пусть в списке лежат объекты разных классов, и у всех есть метод `send`. Тогда не нужно выяснять, кто есть кто. Достаточно вызвать метод, а каждый объект сделает по-своему. Это и называют **полиморфизмом**.

Без него получается цепочка проверок, которую приходится дописывать при каждом новом виде:

```python
def deliver(item, text):
    if item.kind == "email":
        return "письмо: " + text
    elif item.kind == "sms":
        return "sms: " + text[:10]
    else:
        return "push: " + text
```

С классами каждый вид отвечает за себя:

```python
class Notification:
    def send(self, text):
        return "общее: " + text


class Email(Notification):
    def send(self, text):
        return "письмо: " + text


class Sms(Notification):
    def send(self, text):
        return "sms: " + text[:10]


items = [Email(), Sms(), Notification()]
log = []
for n in items:
    log.append(n.send("Привет, мир"))
```

| Проход | Объект | Сработал |
|---|---|---|
| 1 | `Email` | свой `send`, добавилось `"письмо: Привет, мир"` |
| 2 | `Sms` | свой `send`, добавилось `"sms: Привет, мир"[:10]` |
| 3 | `Notification` | родительский `send`, добавилось `"общее: Привет, мир"` |

Новый вид уведомлений — это новый класс. Цикл менять не нужно.

Хороший признак: в коде появляется `if type(x) == ...` или `if x.kind == ...` перед вызовом метода. Скорее всего, этот `if` стоит превратить в классы.

## Частые ошибки

Метод в наследниках называют по-разному (`send_email`, `send_sms`): тогда общий цикл не напишешь. Имя и параметры одинакового по смыслу метода держи одинаковыми.

## Проверь себя

```python
class Shape:
    def area(self):
        return 0

class Square(Shape):
    def __init__(self, side):
        self.side = side

    def area(self):
        return self.side * self.side

total = 0
for f in [Square(2), Shape(), Square(3)]:
    total = total + f.area()
```

Чему равно `total`?

<details><summary>Ответ</summary>

`13`: `4 + 0 + 9`. `Shape()` ответил родительским `area`.

</details>
