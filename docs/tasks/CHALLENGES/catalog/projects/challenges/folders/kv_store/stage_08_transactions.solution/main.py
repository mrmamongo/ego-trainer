"""Хранилище ключ-значение: главная программа."""

from commands import parse_command
from storage import execute, load_store


def main():
    store = load_store()
    queue = None  # None — обычный режим, список — после MULTI
    while True:
        try:
            line = input()
        except EOFError:
            break  # ввод закончился
        name, args = parse_command(line)
        if name == "":
            continue  # пустая строка — просто идём дальше
        if name == "EXIT":
            break
        if name == "MULTI":
            if queue is not None:
                print("ERR MULTI calls can not be nested")
            else:
                queue = []
                print("OK")
        elif name == "DISCARD":
            if queue is None:
                print("ERR DISCARD without MULTI")
            else:
                queue = None
                print("OK")
        elif name == "EXEC":
            if queue is None:
                print("ERR EXEC without MULTI")
            else:
                if len(queue) == 0:
                    print("(empty)")
                for queued_name, queued_args in queue:
                    print(execute(store, queued_name, queued_args))
                queue = None
        elif queue is not None:
            queue.append((name, args))
            print("QUEUED")
        else:
            print(execute(store, name, args))


if __name__ == "__main__":
    main()
