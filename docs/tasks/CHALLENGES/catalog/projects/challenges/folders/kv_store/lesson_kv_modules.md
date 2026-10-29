---
id: kv-modules
title: "Несколько файлов: import между своими модулями"
order: 1
version: "1.0.0"
---

# Несколько файлов: import между своими модулями

Пока программа маленькая, её можно держать в одном файле. Когда функций много, их раскладывают по файлам: в одном — разбор команд, в другом — хранилище, в третьем — главная программа. Каждый такой `.py`-файл называют **модулем**.

## Как один файл берёт функцию из другого

Если рядом лежат два файла:

```python
# commands.py
def parse_command(line):
    words = line.split()
    return (words[0].upper(), words[1:])
```

```python
# main.py
from commands import parse_command

name, args = parse_command("set a 1")
print(name, args)        # SET ['a', '1']
```

`from commands import parse_command` читается так: «из файла `commands.py` возьми функцию `parse_command`». Имя пишут **без** `.py`.

| Запись | Что значит |
|---|---|
| `from commands import parse_command` | взять одну функцию |
| `from storage import execute, load_store` | взять несколько функций через запятую |
| `import storage` | взять весь модуль; тогда вызывают так: `storage.execute(...)` |

Файлы должны лежать в одной папке: оттуда Python и ищет твои модули.

## Кто что делает

| Файл | Работа |
|---|---|
| `commands.py` | превращает строку в имя и аргументы |
| `storage.py` | выполняет команду над словарём |
| `main.py` | связывает остальное: читает, вызывает, печатает |

Хорошее правило: **функция делает одну работу**. `parse_command` ничего не печатает, `execute` ничего не читает с клавиатуры. Поэтому их легко проверять по отдельности: проверка просто вызывает `parse_command("set a 1")` и смотрит на результат.

## Защита `if __name__ == "__main__":`

В конце `main.py` стоят две строки:

```python
if __name__ == "__main__":
    main()
```

Они значат: «запусти `main()`, только если этот файл запустили как программу» (`python main.py`). Если другой файл импортирует `main.py`, `main()` не стартует. Так проверка может подключить твой файл как модуль и не зависнуть на `input()`.

## Пример целиком: путь строки по файлам

Ввод `set a 1`:

| Шаг | Где | Что происходит | Результат |
|---|---|---|---|
| 1 | `main.py` | `input()` прочитал строку | `"set a 1"` |
| 2 | `commands.py` | `parse_command("set a 1")` | `("SET", ["a", "1"])` |
| 3 | `storage.py` | `execute(store, "SET", ["a", "1"])` меняет `store` | `"OK"` |
| 4 | `main.py` | `print(...)` печатает ответ | `OK` |

## Частые ошибки

Написать `.py` в импорте:

```python
from commands.py import parse_command     # неверно
from commands import parse_command        # верно
```

Переименовать файл. Проверка ждёт `commands.py`, `storage.py` и `main.py` с точно такими именами.

Вызвать функцию, не импортировав её: `NameError: name 'execute' is not defined`.

## Проверь себя

```python
# main.py
from storage import execute
```

1. Из какого файла берётся `execute`?
2. Что нужно написать, чтобы взять ещё и `load_store`?
3. Что произойдёт, если вызвать `main.py` из другого файла командой `import main`?

<details><summary>Ответ</summary>

1. Из `storage.py`, который лежит в той же папке.
2. `from storage import execute, load_store`.
3. Код файла выполнится, но `main()` не запустится: условие `__name__ == "__main__"` ложно.

</details>
