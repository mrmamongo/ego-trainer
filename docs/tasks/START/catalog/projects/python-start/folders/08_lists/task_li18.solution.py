def task_li18_transpose(matrix):
    if len(matrix) == 0:
        return []
    rows = len(matrix)
    cols = len(matrix[0])
    result = []
    for col in range(cols):
        new_row = []
        for row in range(rows):
            new_row.append(matrix[row][col])
        result.append(new_row)
    return result
