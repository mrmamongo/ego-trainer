def parse_command(line):
    return None  # твой код


def handle(entries, line):
    return None  # твой код


def task_px01_session(lines):
    # вызывается в конце файла: запоминаем, что файл запущен как программа, а не проверкой
    global STARTED_BY_USER
    STARTED_BY_USER = __file__ == sys.argv[0]
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


import sys

if __file__ == sys.argv[0]:
    main()
# ===== конец готового цикла =====
