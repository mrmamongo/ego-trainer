def task_li20_find_in_matrix(matrix, x):
    for r in range(len(matrix)):
        for c in range(len(matrix[r])):
            if matrix[r][c] == x:
                return [r, c]
    return [-1, -1]
