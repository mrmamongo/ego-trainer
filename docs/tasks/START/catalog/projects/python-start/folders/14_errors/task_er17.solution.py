def given_parse_age(text):
    """GIVEN: вернуть возраст или бросить ValueError("не число" / "меньше нуля" / "больше 150")."""
    try:
        age = int(text)
    except ValueError:
        raise ValueError("не число")
    if age < 0:
        raise ValueError("меньше нуля")
    if age > 150:
        raise ValueError("больше 150")
    return age


def task_er17_first_error_line(text):
    lines = text.split("\n")
    for index in range(len(lines)):
        line = lines[index]
        if line.strip() == "":
            continue
        parts = line.split(";")
        if len(parts) != 2:
            return index + 1, "ожидается имя;возраст"
        if parts[0].strip() == "":
            return index + 1, "пустое имя"
        try:
            given_parse_age(parts[1])
        except ValueError as error:
            return index + 1, str(error)
    return None
