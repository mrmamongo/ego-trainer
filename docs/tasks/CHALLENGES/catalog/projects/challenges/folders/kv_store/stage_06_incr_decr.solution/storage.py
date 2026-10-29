"""Хранилище: здесь команды работают со словарём store."""

# Сколько аргументов нужно каждой команде.
ARITY = {
    "SET": 2,
    "GET": 1,
    "DEL": 1,
    "EXISTS": 1,
    "KEYS": 0,
    "INCR": 1,
    "DECR": 1,
}


def change_number(store, key, step):
    """Прибавить step к числу, которое лежит в store[key] текстом."""
    text = store.get(key, "0")
    try:
        number = int(text)
    except ValueError:
        return "ERR value is not an integer"
    store[key] = str(number + step)
    return store[key]


def execute(store, name, args):
    """Выполнить команду над словарём store и вернуть ответ строкой.

    name — имя команды заглавными буквами ("SET"), args — список аргументов.
    Пример: execute({}, "SET", ["a", "1"]) -> "OK"
    """
    if name not in ARITY:
        return f"ERR unknown command '{name}'"
    if len(args) != ARITY[name]:
        return f"ERR wrong number of arguments for '{name}'"
    if name == "SET":
        store[args[0]] = args[1]
        return "OK"
    if name == "GET":
        return store.get(args[0], "(nil)")
    if name == "DEL":
        if args[0] in store:
            del store[args[0]]
            return "1"
        return "0"
    if name == "EXISTS":
        if args[0] in store:
            return "1"
        return "0"
    if name == "KEYS":
        if len(store) == 0:
            return "(empty)"
        return " ".join(sorted(store))
    if name == "INCR":
        return change_number(store, args[0], 1)
    if name == "DECR":
        return change_number(store, args[0], -1)
