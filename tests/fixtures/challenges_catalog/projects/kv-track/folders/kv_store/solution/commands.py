"""Команды хранилища: разбор строк — здесь."""


def parse_command(line):
    parts = line.split()
    if not parts:
        return "EXIT", None
    return parts[0].upper(), parts[1:] or None
