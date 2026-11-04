"""Свой grep: главная программа."""

import sys

from search import find_matches

USAGE = "использование: python main.py [-i] [-v] [-n] [-c] ШАБЛОН ФАЙЛ"


def parse_args(argv):
    """Вернуть (флаги, шаблон, файл). Ошибка — ValueError с текстом для stderr."""
    options = {"i": False, "v": False, "n": False, "c": False}
    position = 0
    while position < len(argv) and argv[position].startswith("-"):
        flag = argv[position]
        if flag not in ("-i", "-v", "-n", "-c"):
            raise ValueError(f"grep: неизвестный флаг {flag}")
        options[flag[1]] = True
        position += 1
    rest = argv[position:]
    if len(rest) < 2:
        raise ValueError(USAGE)
    return options, rest[0], rest[1]


def main(argv):
    """Запуск программы. Код завершения: 0, 1 или 2."""
    try:
        options, pattern, path = parse_args(argv)
    except ValueError as error:
        print(error, file=sys.stderr)
        return 2
    try:
        with open(path, encoding="utf-8") as handle:
            lines = [line.rstrip("\n") for line in handle]
    except FileNotFoundError:
        print(f"grep: {path}: нет такого файла", file=sys.stderr)
        return 2
    found = find_matches(lines, pattern, options["i"], options["v"])
    if options["c"]:
        print(len(found))
    else:
        for number, text in found:
            if options["n"]:
                print(f"{number}:{text}")
            else:
                print(text)
    return 0 if found else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
