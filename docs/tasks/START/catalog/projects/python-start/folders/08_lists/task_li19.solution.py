def task_li19_row_sums(matrix):
    result = []
    for row in matrix:
        total = 0
        for value in row:
            total = total + value
        result.append(total)
    return result
