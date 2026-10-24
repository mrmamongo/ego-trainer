def task_bk12_count_even_pairs(a, b):
    # Собери тело функции из строк ниже. Они перемешаны и записаны без отступов:
    # порядок и отступы придётся расставить самому. Лишних строк нет.
    #
    #   return count
    #   count = count + 1
    #   for y in b:
    #   count = 0
    #   if (x + y) % 2 == 0:
    #   for x in a:
    #
    count = 0
    for x in a:
        for y in b:
            if (x + y) % 2 == 0:
                count = count + 1
    return count
