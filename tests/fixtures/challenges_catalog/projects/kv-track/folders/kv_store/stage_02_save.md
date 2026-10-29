---
id: KV02
title: "Сохранение в JSON"
version: "1.0.0"
level: medium
tags: [challenge, json]
breaking: false
---

# Задача KV02: Сохранение в JSON

## Условие

`main.py` читает команды из stdin до `EXIT` и выполняет их:

- `SET <ключ> <значение>` печатает `OK`;
- `GET <ключ>` печатает значение или `NONE`.

После `EXIT` программа сохраняет хранилище в `data/store.json`
(создай папку, если её нет) и завершается.

## Пример

```text
SET a 1
GET a
EXIT
# -> OK
#    1
```
