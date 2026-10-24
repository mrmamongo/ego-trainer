def task_fd17_report(text):
    # Собери тело функции из строк ниже. Они перемешаны и записаны без отступов:
    # порядок и отступы придётся расставить самому. Лишних строк нет.
    #
    #   return answer
    #   count = count_words(cleaned)
    #   answer = label(count)
    #   cleaned = clean(text)
    #
    cleaned = clean(text)
    count = count_words(cleaned)
    answer = label(count)
    return answer


# Помощники готовы, менять их не нужно.
def clean(text):
    return text.replace(",", " ").strip()


def count_words(text):
    return len(text.split())


def label(count):
    return "слов: " + str(count)
