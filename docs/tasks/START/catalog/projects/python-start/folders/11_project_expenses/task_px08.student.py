def parse_command(line):
    words = line.strip().split()  # твой код
    return [words[0].lower(), words[1:]]


def handle(entries, limits, line):
    return ""  # твой код: верни ответ на каждую команду


def task_px08_session(lines):
    # вызывается в конце файла: запоминаем, что файл запущен как программа, а не проверкой
    global STARTED_BY_USER
    STARTED_BY_USER = __file__ == sys.argv[0]
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


import sys

if __file__ == sys.argv[0]:
    main()
# ===== конец готового цикла =====
