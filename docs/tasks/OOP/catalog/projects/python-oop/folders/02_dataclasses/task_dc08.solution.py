from dataclasses import dataclass


@dataclass
class Item:
    name: str
    qty: int
    price: int


def task_dc08_stock_value(rows, min_price):
    # Собери тело функции из строк ниже. Они перемешаны и записаны без отступов:
    # порядок и отступы придётся расставить самому. Лишних строк нет.
    #
    #   return total
    #   if item.price >= min_price:
    #   total = 0
    #   for data in rows:
    #   total = total + item.qty * item.price
    #   item = Item(data["name"], data["qty"], data["price"])
    #
    total = 0
    for data in rows:
        item = Item(data["name"], data["qty"], data["price"])
        if item.price >= min_price:
            total = total + item.qty * item.price
    return total
