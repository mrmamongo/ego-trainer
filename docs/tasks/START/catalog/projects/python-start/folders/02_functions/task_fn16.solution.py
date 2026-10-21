def task_fn16_triangle(a, b, c):
    if a >= b + c or b >= a + c or c >= a + b:
        return "не треугольник"
    elif a == b and b == c:
        return "равносторонний"
    elif a == b or b == c or a == c:
        return "равнобедренный"
    else:
        return "разносторонний"
