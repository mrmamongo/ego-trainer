"""Поиск: какие строки списка подходят под шаблон."""

from matcher import matches


def find_matches(lines, pattern):
    """Вернуть список пар (номер, строка) для подходящих строк."""
    found = []
    for number, line in enumerate(lines, start=1):
        text = line.rstrip("\n")
        if matches(text, pattern):
            found.append((number, text))
    return found
