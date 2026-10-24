def task_di08_group_by_first(words):
    # Собери тело функции из строк ниже. Они перемешаны и записаны без отступов:
    # порядок и отступы придётся расставить самому. Лишних строк нет.
    #
    #   return result
    #   result[key].append(word)
    #   for word in words:
    #   if key not in result:
    #   key = word[0]
    #   result = {}
    #   result[key] = []
    #
    result = {}
    for word in words:
        key = word[0]
        if key not in result:
            result[key] = []
        result[key].append(word)
    return result
