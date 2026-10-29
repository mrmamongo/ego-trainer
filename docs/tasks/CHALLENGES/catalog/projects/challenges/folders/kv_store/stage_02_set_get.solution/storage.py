"""Хранилище: здесь команды работают со словарём store."""


def execute(store, name, args):
    """Выполнить команду над словарём store и вернуть ответ строкой.

    name — имя команды заглавными буквами ("SET"), args — список аргументов.
    Пример: execute({}, "SET", ["a", "1"]) -> "OK"
    """
    if name == "SET":
        store[args[0]] = args[1]
        return "OK"
    if name == "GET":
        return store.get(args[0], "(nil)")
