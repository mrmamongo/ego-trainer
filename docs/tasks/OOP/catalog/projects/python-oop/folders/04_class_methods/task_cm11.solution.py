def run_command(handlers, line):
    if not line.startswith("/"):
        return "это не команда"
    name, _, argument = line[1:].partition(" ")
    if name not in handlers:
        return "неизвестная команда: " + name
    return handlers[name](argument)


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def given_hello(text):
    return "Привет, " + text + "!"


def given_shout(text):
    return text.upper()


def given_count(text):
    return len(text.split())


def task_cm11_chat(line):
    handlers = {"hello": given_hello, "shout": given_shout, "count": given_count}
    return run_command(handlers, line)
