"""Хранилище ключ-значение: цикл команд (этап 2)."""

import json
import os
import sys

from commands import parse_command


def load(path):
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def save(path, store):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(store, handle)


def main():
    store = load("data/store.json")
    for line in sys.stdin:
        command, args = parse_command(line.strip())
        if command == "EXIT":
            break
        if command == "SET":
            store[args[0]] = args[1]
            print("OK")
        elif command == "GET":
            print(store.get(args[0], "NONE"))
    save("data/store.json", store)


if __name__ == "__main__":
    main()
