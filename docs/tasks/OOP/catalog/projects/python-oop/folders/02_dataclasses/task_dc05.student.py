from dataclasses import dataclass


@dataclass(eq=False)
class Item:
    name: str
    qty: int


def task_dc05_has_item(stock, name, qty):
    items = []
    for row in stock:
        items.append(Item(row[0], row[1]))
    wanted = Item(name, qty)
    return wanted in items
