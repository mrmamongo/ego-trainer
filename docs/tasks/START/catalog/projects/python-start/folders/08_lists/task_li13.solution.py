def task_li13_even_squares(nums):
    # Собери тело функции из строк ниже (в форме с циклом). Они перемешаны и записаны без отступов:
    # порядок и отступы придётся расставить самому. Лишних строк нет.
    #
    #   return result
    #   if number % 2 == 0:
    #   result = []
    #   result.append(number * number)
    #   for number in nums:
    #
    result = []
    for number in nums:
        if number % 2 == 0:
            result.append(number * number)
    return result
