---
id: dc-to-dict
title: "Запись и словарь: to_dict, from_dict и сортировка"
order: 5
version: "1.0.0"
---

# Запись и словарь: `to_dict`, `from_dict` и сортировка

Данные снаружи (файл, ответ сервера, сообщение) приходят словарями, а работать удобнее с записями. Нужны два перехода: **запись → словарь** и **словарь → запись**.

```python
@dataclass
class Message:
    author: str
    text: str
    likes: int = 0

    def to_dict(self):
        return {"author": self.author, "text": self.text, "likes": self.likes}


def message_from_dict(data):
    return Message(data["author"], data["text"], data.get("likes", 0))
```

`to_dict` — метод: он берёт поля `self`. `message_from_dict` — обычная функция: объекта ещё нет, он как раз создаётся. (Способ положить такую функцию внутрь класса появится в папке 04, пока пиши её отдельно.)

```python
m = message_from_dict({"author": "Аня", "text": "привет"})   # 1
d = m.to_dict()                                              # 2
```

| После строки | Что получилось |
|---|---|
| 1 | `m` — запись `Message(author='Аня', text='привет', likes=0)`; `data.get("likes", 0)` подставил `0` |
| 2 | `d` равно `{"author": "Аня", "text": "привет", "likes": 0}` |

Для простых записей есть готовая `dataclasses.asdict(m)`, она делает то же, что наш `to_dict`. А `Message(**data)` работает, только если ключи словаря в точности равны полям: лишний ключ даст `TypeError`.

## Сортировка списка записей

Список записей сортируют через `sorted` и `key=`, как список пар из словаря:

```python
messages = [Message("Аня", "а", 5), Message("Боря", "б", 9), Message("Вика", "в", 5)]
top = sorted(messages, key=lambda m: m.likes, reverse=True)
# Боря(9), Аня(5), Вика(5): равные остаются в прежнем порядке
```

Два критерия: сначала по лайкам по убыванию, потом по автору по алфавиту. Для числа ставят минус:

```python
sorted(messages, key=lambda m: (-m.likes, m.author))
```

`sorted` возвращает новый список и не меняет исходный. В ответ функции кладут уже словари: `[m.to_dict() for m in top]`, а не записи.

## Частые ошибки

Ждать, что `m["author"]` сработает:

```python
author = m["author"]        # неверно: у записи нет ключей
```

```python
author = m.author           # верно
```

Вернуть из функции записи там, где просят словари: потом такой результат нельзя сравнить с данными, его покажут как `Message(...)`.

## Проверь себя

```python
m = message_from_dict({"author": "Боря", "text": "ок", "likes": 2})
```

1. Чему равно `m.likes`?
2. Что вернёт `m.to_dict()["author"]`?
3. Как отсортировать список `messages` по `likes` по возрастанию?

<details><summary>Ответ</summary>

1. `2`.
2. `"Боря"`.
3. `sorted(messages, key=lambda m: m.likes)`.

</details>
