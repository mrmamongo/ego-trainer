def task_er11_process_lines(lines):
    total = 0
    results = []
    for line in lines:
        parts = line.split()
        if len(parts) == 0 or parts[0] not in ("add", "sub"):
            results.append("unknown_command")
            continue
        if len(parts) != 2:
            results.append("bad_number")
            continue
        try:
            number = int(parts[1])
        except ValueError:
            results.append("bad_number")
            continue
        if number < 0:
            results.append("bad_number")
            continue
        if parts[0] == "add":
            total = total + number
        elif number > total:
            results.append("not_enough")
            continue
        else:
            total = total - number
        results.append(total)
    return results
