"""Поиск: какие строки списка подходят под шаблон."""

from matcher import matches


def find_matches(lines, pattern, ignore_case=False, invert=False):
    """Вернуть список пар (номер, строка) для выбранных строк.

    ignore_case: не различать большие и маленькие буквы.
    invert: выбирать строки, которые НЕ подходят.
    """
    if ignore_case:
        pattern = pattern.lower()
    found = []
    for number, line in enumerate(lines, start=1):
        text = line.rstrip("\n")
        subject = text.lower() if ignore_case else text
        if matches(subject, pattern) != invert:
            found.append((number, text))
    return found
