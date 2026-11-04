"""Свой grep: главная программа."""

import sys

from search import find_matches


def main(argv):
    """Запуск программы: ШАБЛОН ФАЙЛ. Код завершения: 0, 1 или 2."""
    if len(argv) < 2:
        print("использование: python main.py ШАБЛОН ФАЙЛ", file=sys.stderr)
        return 2
    pattern, path = argv[0], argv[1]
    try:
        with open(path, encoding="utf-8") as handle:
            lines = [line.rstrip("\n") for line in handle]
    except FileNotFoundError:
        print(f"grep: {path}: нет такого файла", file=sys.stderr)
        return 2
    found = find_matches(lines, pattern)
    for number, text in found:
        print(text)
    return 0 if found else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
