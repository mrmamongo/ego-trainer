from dataclasses import dataclass


@dataclass(frozen=True)
class Message:
    author: str
    text: str


def task_mg10_dedupe(rows):
    # Собери тело функции из строк ниже. Они перемешаны и записаны без отступов:
    # порядок и отступы придётся расставить самому. Лишних строк нет.
    #
    #   result.append([author, text])
    #   return result
    #   if message not in seen:
    #   seen = set()
    #   message = Message(author, text)
    #   result = []
    #   for author, text in rows:
    #   seen.add(message)
    #
    return None  # собери тело функции из строк выше
