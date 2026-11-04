"""Свой grep: главная программа."""

import sys

from search import find_matches

USAGE = "использование: python main.py [-i] [-v] ШАБЛОН ФАЙЛ"


def main(argv):
    """Запуск программы: [-i] [-v] ШАБЛОН ФАЙЛ. Код завершения: 0, 1 или 2."""
    ignore_case = False
    invert = False
    position = 0
    while position < len(argv) and argv[position].startswith("-"):
        flag = argv[position]
        if flag == "-i":
            ignore_case = True
        elif flag == "-v":
            invert = True
        else:
            print(f"grep: неизвестный флаг {flag}", file=sys.stderr)
            return 2
        position += 1
    rest = argv[position:]
    if len(rest) < 2:
        print(USAGE, file=sys.stderr)
        return 2
    pattern, path = rest[0], rest[1]
    try:
        with open(path, encoding="utf-8") as handle:
            lines = [line.rstrip("\n") for line in handle]
    except FileNotFoundError:
        print(f"grep: {path}: нет такого файла", file=sys.stderr)
        return 2
    found = find_matches(lines, pattern, ignore_case, invert)
    for number, text in found:
        print(text)
    return 0 if found else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
