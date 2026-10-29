def task_rv12_run(commands):
    value = 0
    applied = 0
    ignored = 0
    history = []
    for command in commands:
        parts = command.split()
        if parts[0] == "add":
            history.append(value)
            value = value + int(parts[1])
            applied = applied + 1
        elif parts[0] == "sub":
            history.append(value)
            value = value - int(parts[1])
            applied = applied + 1
        elif parts[0] == "reset":
            history.append(value)
            value = 0
            applied = applied + 1
        elif parts[0] == "undo":
            if history:
                value = history.pop()
                applied = applied + 1
            else:
                ignored = ignored + 1
        else:
            ignored = ignored + 1
    return value, applied, ignored
