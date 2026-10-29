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
        # TODO (этап 4): разбери строку через parse_command.
        # Пустая команда — пропусти, EXIT — выйди из цикла,
        # остальное выполни через execute и напечатай ответ.


if __name__ == "__main__":
    main()
