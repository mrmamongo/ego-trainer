from ego.testing import case

@case(
    args=("Хлеб", 2, 45.5),
    expected="Хлеб x2 = 91.00",
    description="дробная цена",
    level="smoke",
)

@case(
    args=("Чай", 1, 120),
    expected="Чай x1 = 120.00",
    description="целая цена",
    level="smoke",
)

@case(
    args=("Сок", 3, 59.9),
    expected="Сок x3 = 179.70",
    description="ноль после запятой дописывается",
    level="smoke",
)

@case(
    args=("Яблоко", 0, 30),
    expected="Яблоко x0 = 0.00",
    description="ноль штук",
    level="full",
)

@case(
    args=("Ручка", 10, 15),
    expected="Ручка x10 = 150.00",
    description="двузначное количество",
    level="full",
)

@case(
    args=("Молоко 3.2%", 2, 79),
    expected="Молоко 3.2% x2 = 158.00",
    description="знаки в названии",
    level="full",
)
def task_s20_receipt_line(name, qty, price):
    ...
