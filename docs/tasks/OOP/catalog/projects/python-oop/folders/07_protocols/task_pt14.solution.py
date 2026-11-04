import io


def non_empty(lines):
    for line in lines:
        text = line.strip()
        if text:
            yield text


def only_errors(lines):
    for line in lines:
        if line.startswith("ERROR"):
            yield line


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_pt14_first_error(text):
    consumed = []

    def given_source():
        for line in io.StringIO(text):
            consumed.append(line)
            yield line

    errors = only_errors(non_empty(given_source()))
    first = next(errors, "нет ошибок")
    return [first, len(consumed)]
