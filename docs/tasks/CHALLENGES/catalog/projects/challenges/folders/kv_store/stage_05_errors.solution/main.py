"""Хранилище ключ-значение: главная программа."""

from commands import parse_command
from storage import execute


def main():
    store = {}
    while True:
        try:
            line = input()
        except EOFError:
            break  # ввод закончился
        name, args = parse_command(line)
        if name == "":
            continue  # пустая строка — просто идём дальше
        if name == "EXIT":
            break
        print(execute(store, name, args))


if __name__ == "__main__":
    main()
