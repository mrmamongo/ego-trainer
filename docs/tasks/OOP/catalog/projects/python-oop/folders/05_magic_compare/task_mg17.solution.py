class Book:
    def __init__(self, title, year):
        self.title = title
        self.year = year

    def __lt__(self, other):
        return (self.year, self.title) < (other.year, other.title)


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_mg17_shelf(rows):
    books = [Book(title, year) for title, year in rows]
    return [book.title for book in sorted(books)]
