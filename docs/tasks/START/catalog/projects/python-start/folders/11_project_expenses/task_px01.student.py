def parse_command(line):
    return None  # твой код


def handle(entries, line):
    return None  # твой код


def task_px01_session(lines):
    entries = []
    replies = []
    for line in lines:
        replies.append(handle(entries, line))
    return replies


# ===== готовый цикл программы =====
# Запускай весь файл: программа ждёт команды и выходит по exit.


def main():
    entries = []
    while True:
        line = input("> ")
        if line == "exit":
            break
        print(handle(entries, line))


if __name__ == "__main__":
    main()
# ===== конец готового цикла =====
