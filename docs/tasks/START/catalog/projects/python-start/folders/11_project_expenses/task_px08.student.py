def parse_command(line):
    words = line.strip().split()  # твой код
    return [words[0].lower(), words[1:]]


def handle(entries, limits, line):
    return ""  # твой код: верни ответ на каждую команду


def task_px08_session(lines):
    entries = []
    limits = []
    replies = []
    for line in lines:
        replies.append(handle(entries, limits, line))
    return replies


# ===== готовый цикл программы =====
# Запускай весь файл: программа ждёт команды и выходит по exit.


def main():
    entries = []
    limits = []
    while True:
        line = input("> ")
        if line == "exit":
            break
        print(handle(entries, limits, line))


if __name__ == "__main__":
    main()
# ===== конец готового цикла =====
