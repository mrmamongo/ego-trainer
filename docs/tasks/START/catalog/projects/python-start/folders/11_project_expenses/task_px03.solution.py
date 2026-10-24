def parse_command(line):
    words = line.strip().split()
    if len(words) == 0:
        return ["", []]
    return [words[0].lower(), words[1:]]


HELP_TEXT = (
    "Команды:\n"
    "add <сумма> <категория> — записать расход\n"
    "total — сколько потрачено\n"
    "help — эта справка\n"
    "exit — выйти"
)


def handle(entries, line):
    command, args = parse_command(line)
    if command == "add":
        if len(args) < 1:
            return "Сумма должна быть целым числом больше нуля"
        if not args[0].isdigit() or int(args[0]) == 0:
            return "Сумма должна быть целым числом больше нуля"
        if len(args) < 2:
            return "Укажи категорию"
        entries.append([int(args[0]), args[1]])
        return f"Записал: {args[0]} ₽ — {args[1]}"
    if command == "total":
        total = 0
        for entry in entries:
            total = total + entry[0]
        return f"Всего: {total} ₽"
    if command == "help":
        return HELP_TEXT
    return "Не понимаю команду. Напиши help."


def task_px03_session(lines):
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
