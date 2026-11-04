---
id: pt-pipeline
title: "Ленивые цепочки и next(gen, запасное)"
order: 4
version: "1.0.0"
---

# Ленивые цепочки и `next(gen, запасное)`

Генераторы удобно соединять в цепочку: один отдаёт строки, второй выбрасывает пустые, третий оставляет нужные. Данные идут по одной строке через всю цепочку, а не пачкой.

```python
import io

def non_empty(lines):
    for line in lines:
        text = line.strip()
        if text:
            yield text

def only_errors(lines):
    for line in lines:
        if line.startswith("ERROR"):
            yield line

file = io.StringIO("INFO старт\n\nERROR диск\nERROR сеть\n")
gen = only_errors(non_empty(file))     # 1
first = next(gen, "нет ошибок")        # 2
rest = list(gen)                       # 3
```

| После строки | Что получилось |
|---|---|
| 1 | ничего не прочитано: цепочка собрана, но ленивая |
| 2 | прочитаны строки `INFO старт`, пустая, `ERROR диск`; `first` равно `"ERROR диск"` |
| 3 | `rest` равно `["ERROR сеть"]` |

Остальной файл после первой ошибки не трогали, пока не попросили. Для огромного журнала это важно: нашли первую ошибку и остановились.

## Первый элемент или запасное значение

`next(gen)` на пустом генераторе бросает `StopIteration`. Если нужно «первый, а если нет, то вот это», пиши `next(gen, запасное)`:

```python
next(only_errors(non_empty(io.StringIO("INFO ок\n"))), "нет ошибок")    # "нет ошибок"
```

## Частые ошибки

Собрать промежуточный результат списком: цепочка перестаёт быть ленивой.

```python
def non_empty(lines):
    return [line.strip() for line in lines if line.strip()]    # прочитает весь файл сразу
```

Правильно: оставить `yield`, чтобы строки шли по одной.

## Проверь себя

```python
gen = only_errors(["INFO a", "ERROR b", "ERROR c"])
x = next(gen, "-")
y = next(gen, "-")
z = next(gen, "-")
```

<details><summary>Ответ</summary>

`x` равно `"ERROR b"`, `y` равно `"ERROR c"`, `z` равно `"-"`.

</details>
