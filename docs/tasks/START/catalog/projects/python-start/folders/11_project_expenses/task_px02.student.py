# ===== готово с прошлого шага: добавь новые команды =====
def parse_command(line):
    words = line.strip().split()
    if len(words) == 0:
        return ["", []]
    return [words[0].lower(), words[1:]]


def handle(entries, line):
    command, args = parse_command(line)
    if command == "add":
        entries.append([int(args[0]), args[1]])
        return f"Записал: {args[0]} ₽ — {args[1]}"
    return "Не понимаю команду. Напиши help."
# ===== конец готового кода =====


def task_px02_session(lines):
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
