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


def add_context(lines, found, before, after):
    """Добавить к найденным строкам соседей: before сверху и after снизу.

    Вернуть список групп. Группа — список троек (номер, строка, найдена_ли).
    Группы, которые касаются или пересекаются, склеиваются в одну.
    """
    texts = [line.rstrip("\n") for line in lines]
    hits = {number for number, _ in found}
    windows = []
    for number, _ in found:
        start = max(1, number - before)
        end = min(len(texts), number + after)
        if windows and start <= windows[-1][1] + 1:
            windows[-1][1] = max(windows[-1][1], end)
        else:
            windows.append([start, end])
    groups = []
    for start, end in windows:
        groups.append([(n, texts[n - 1], n in hits) for n in range(start, end + 1)])
    return groups
