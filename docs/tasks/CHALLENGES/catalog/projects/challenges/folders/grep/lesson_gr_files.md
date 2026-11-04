---
id: gr-files
title: "Читаем файл построчно: open, with, rstrip"
order: 1
version: "1.0.0"
---

# Читаем файл построчно: open, with, rstrip

`grep` работает с файлами, значит, нужно уметь их читать. Заодно коротко про то, как файлы программы берут функции друг у друга.

## Файлы программы и import

В челлендже три файла рядом: `matcher.py`, `search.py`, `main.py`. Один берёт функцию у другого через `import`:

```python
# search.py
from matcher import matches        # «из файла matcher.py возьми функцию matches»
```

Имя пишут **без** `.py`. Файлы должны лежать в одной папке. У каждой функции одна работа: `matches` отвечает про одну строку, `find_matches` обходит список, `main` читает аргументы и печатает. Поэтому проверка может вызвать `matches` отдельно, не запуская всю программу.

## open и with

Функция `open(путь, encoding="utf-8")` открывает файл. Закрывать его нужно обязательно, и это за тебя делает `with`:

```python
with open("notes.txt", encoding="utf-8") as handle:
    text = handle.read()
```

Пока идут отступы под `with`, файл открыт, потом закрывается сам, даже если внутри случилась ошибка. `encoding="utf-8"` нужен, чтобы русские буквы читались правильно на любой системе.

## Файл — это набор строк

По файлу можно пройти циклом `for`: каждый шаг отдаёт одну строку.

```python
with open("notes.txt", encoding="utf-8") as handle:
    for line in handle:
        print(line)
```

Если в файле `cat`, `dog`, `cow` на трёх строках, ты увидишь пустые строки между словами. Причина: каждая строка из файла приходит **вместе с переводом строки на конце** (`"cat\n"`), а `print` добавляет ещё один. Убирает лишнее `rstrip("\n")`:

```python
lines = []
with open("notes.txt", encoding="utf-8") as handle:
    for line in handle:
        lines.append(line.rstrip("\n"))
```

Короче то же самое пишется спискомным выражением: `lines = [line.rstrip("\n") for line in handle]`.

| Что читаем | Что получится |
|---|---|
| `for line in handle` | строки одна за другой, каждая с `"\n"` на конце (кроме, возможно, последней) |
| `line.rstrip("\n")` | та же строка без `"\n"` на конце |
| `handle.read()` | весь файл одной строкой |

Последняя строка файла может быть без `"\n"`: `rstrip` в таком случае ничего не уберёт и ничего не сломает.

## Если файла нет

`open` на несуществующий путь бросает `FileNotFoundError`. Эту ошибку ловят и сообщают своими словами:

```python
try:
    with open(path, encoding="utf-8") as handle:
        lines = [line.rstrip("\n") for line in handle]
except FileNotFoundError:
    print(f"grep: {path}: нет такого файла", file=sys.stderr)
```

## Пример целиком: от файла к найденным строкам

Файл `animals.txt`: `cat`, `dog`, `cow` (по строке).

| Шаг | Код | Результат |
|---|---|---|
| 1 | `open` и цикл по файлу | `"cat\n"`, `"dog\n"`, `"cow\n"` |
| 2 | `rstrip("\n")` | `["cat", "dog", "cow"]` |
| 3 | `find_matches(lines, "o")` | `[(2, "dog"), (3, "cow")]` |
| 4 | печать `text` из каждой пары | `dog`, затем `cow` |

## Частые ошибки

Забыть `rstrip("\n")`: после `print` в выводе появляются лишние пустые строки.

Написать `open("notes.txt")` без `encoding`: на русской Windows файл может читаться в чужой кодировке.

Читать файл за пределами `with`: после выхода из блока файл уже закрыт, и `for line in handle` упадёт с `ValueError`.

Ловить слишком широкую ошибку: `except Exception` спрячет настоящие поломки. Лови `FileNotFoundError`.

## Проверь себя

```python
with open("data.txt", encoding="utf-8") as handle:
    lines = [line.rstrip("\n") for line in handle]
print(len(lines))
```

Файл `data.txt` содержит три строки, после последней стоит перевод строки.

1. Что напечатает программа?
2. Что изменится, если убрать `rstrip`: изменится ли `len(lines)`?

<details><summary>Ответ</summary>

1. `3`: цикл `for` отдаёт три строки.
2. `len(lines)` останется `3`: меняется только содержимое строк. Каждая получит лишний `"\n"` на конце, и печать этих строк даст пустые строки между ними.

</details>
