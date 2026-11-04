"""Свой grep: главная программа."""

import sys

from search import add_context, find_matches

USAGE = "использование: python main.py [-i] [-v] [-n] [-c] [-A N] [-B N] ШАБЛОН ФАЙЛ..."


def parse_args(argv):
    """Вернуть (флаги, шаблон, файлы). Ошибка — ValueError с текстом для stderr."""
    options = {"i": False, "v": False, "n": False, "c": False, "A": 0, "B": 0}
    position = 0
    while position < len(argv) and argv[position].startswith("-"):
        flag = argv[position]
        if flag in ("-i", "-v", "-n", "-c"):
            options[flag[1]] = True
            position += 1
        elif flag in ("-A", "-B"):
            if position + 1 >= len(argv):
                raise ValueError(f"grep: после {flag} нужно число")
            number = argv[position + 1]
            if not number.isdigit():
                raise ValueError(f"grep: {flag}: неверное число {number}")
            options[flag[1]] = int(number)
            position += 2
        else:
            raise ValueError(f"grep: неизвестный флаг {flag}")
    rest = argv[position:]
    if len(rest) < 2:
        raise ValueError(USAGE)
    return options, rest[0], rest[1:]


def format_line(path, number, text, options, show_file, separator):
    """Собрать строку вывода: `файл:` и `номер:` (у соседних строк вместо `:` стоит `-`)."""
    prefix = ""
    if show_file:
        prefix += path + separator
    if options["n"]:
        prefix += str(number) + separator
    return prefix + text


def main(argv):
    """Запуск программы. Код завершения: 0, 1 или 2."""
    try:
        options, pattern, files = parse_args(argv)
    except ValueError as error:
        print(error, file=sys.stderr)
        return 2
    show_file = len(files) > 1
    with_context = options["A"] > 0 or options["B"] > 0
    had_error = False
    found_any = False
    printed_group = False
    for path in files:
        try:
            with open(path, encoding="utf-8") as handle:
                lines = [line.rstrip("\n") for line in handle]
        except FileNotFoundError:
            print(f"grep: {path}: нет такого файла", file=sys.stderr)
            had_error = True
            continue
        found = find_matches(lines, pattern, options["i"], options["v"])
        if found:
            found_any = True
        if options["c"]:
            print(f"{path}:{len(found)}" if show_file else len(found))
        elif with_context:
            for group in add_context(lines, found, options["B"], options["A"]):
                if printed_group:
                    print("--")
                printed_group = True
                for number, text, is_match in group:
                    separator = ":" if is_match else "-"
                    print(format_line(path, number, text, options, show_file, separator))
        else:
            for number, text in found:
                print(format_line(path, number, text, options, show_file, ":"))
    if had_error:
        return 2
    return 0 if found_any else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
