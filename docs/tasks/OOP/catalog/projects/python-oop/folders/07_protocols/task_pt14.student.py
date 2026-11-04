import io


def non_empty(lines):
    return None  # твой код: генератор, отдающий непустые строки без пробелов по краям


def only_errors(lines):
    return None  # твой код: генератор, отдающий строки на ERROR


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
