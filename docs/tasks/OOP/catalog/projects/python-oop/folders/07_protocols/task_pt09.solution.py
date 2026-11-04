from contextlib import contextmanager


@contextmanager
def section(log, name):
    log.append("начало " + name)
    try:
        yield
    finally:
        log.append("конец " + name)


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_pt09_section(name, fail):
    log = []
    try:
        with section(log, name):
            log.append("работа")
            if fail:
                raise ValueError("сбой")
    except ValueError:
        log.append("ошибка")
    return log
