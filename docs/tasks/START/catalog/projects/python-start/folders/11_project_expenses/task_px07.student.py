# ===== готово с прошлого шага: добавь команду limit и проверку лимита в add =====
def parse_command(line):
    words = line.strip().split()
    if len(words) == 0:
        return ["", []]
    return [words[0].lower(), words[1:]]


HELP_TEXT = (
    "Команды:\n"
    "add <сумма> <категория> — записать расход\n"
    "total — сколько потрачено\n"
    "report — отчёт по категориям\n"
    "undo — отменить последний расход\n"
    "limit <категория> <сумма> — поставить лимит на категорию\n"
    "help — эта справка\n"
    "exit — выйти"
)


def handle(entries, limits, line):
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
    if command == "report":
        if len(entries) == 0:
            return "Расходов пока нет"
        order = []
        sums = []
        for entry in entries:
            if entry[1] not in order:
                order.append(entry[1])
                sums.append(0)
            for i in range(len(order)):
                if order[i] == entry[1]:
                    sums[i] = sums[i] + entry[0]
        total = 0
        for entry in entries:
            total = total + entry[0]
        for i in range(len(sums)):
            for j in range(i + 1, len(sums)):
                if sums[j] > sums[i]:
                    sums[i], sums[j] = sums[j], sums[i]
                    order[i], order[j] = order[j], order[i]
        lines = []
        for i in range(len(order)):
            share = round(sums[i] * 100 / total)
            lines.append(f"{order[i]}: {sums[i]} ₽ ({share}%)")
        lines.append(f"Итого: {total} ₽")
        return "\n".join(lines)
    if command == "undo":
        if len(entries) == 0:
            return "Нечего отменять"
        entry = entries.pop()
        return f"Отменил: {entry[0]} ₽ — {entry[1]}"
    if command == "help":
        return HELP_TEXT
    return "Не понимаю команду. Напиши help."
# ===== конец готового кода =====


def task_px07_session(lines):
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
