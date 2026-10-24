def task_bk09_count_commands(commands):
    count = 0
    for command in commands:
        if command == "stop":
            break
        count = count + 1
    return count
