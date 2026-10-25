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
    # Верни (номер строки с единицы, сообщение) для первой плохой записи или None.
    return None
