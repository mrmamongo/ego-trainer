"""Совпадение: подходит ли одна строка под шаблон."""


def matches(line, pattern):
    """Вернуть True, если шаблон pattern встречается в строке line."""
    return pattern in line
