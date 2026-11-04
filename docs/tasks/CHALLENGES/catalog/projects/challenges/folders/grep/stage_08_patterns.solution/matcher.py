"""Совпадение: подходит ли одна строка под шаблон.

Особые символы шаблона: `.` — любой один символ, `^` в самом начале —
начало строки, `$` в самом конце — конец строки. Всё остальное обычные буквы.
"""


def matches(line, pattern):
    """Вернуть True, если шаблон pattern подходит к какому-то месту строки line."""
    at_start = pattern.startswith("^")
    if at_start:
        pattern = pattern[1:]
    at_end = pattern.endswith("$")
    if at_end:
        pattern = pattern[:-1]
    if at_start:
        return matches_here(line, pattern, at_end)
    for start in range(len(line) + 1):
        if matches_here(line[start:], pattern, at_end):
            return True
    return False


def matches_here(text, pattern, at_end):
    """Подходит ли шаблон к самому началу text (at_end: и до самого конца)."""
    if len(text) < len(pattern):
        return False
    for index in range(len(pattern)):
        if pattern[index] != "." and pattern[index] != text[index]:
            return False
    if at_end:
        return len(text) == len(pattern)
    return True
