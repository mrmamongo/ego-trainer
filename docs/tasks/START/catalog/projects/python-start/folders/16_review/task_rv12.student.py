# Сейчас функция знает только add, sub и reset.
def task_rv12_run(commands):
    value = 0
    applied = 0
    ignored = 0
    for command in commands:
        parts = command.split()
        if parts[0] == "add":
            value = value + int(parts[1])
            applied = applied + 1
        elif parts[0] == "sub":
            value = value - int(parts[1])
            applied = applied + 1
        elif parts[0] == "reset":
            value = 0
            applied = applied + 1
        else:
            ignored = ignored + 1
    return value, applied, ignored
