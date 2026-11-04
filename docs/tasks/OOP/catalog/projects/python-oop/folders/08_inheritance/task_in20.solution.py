class ShopError(Exception):
    pass


class OutOfStock(ShopError):
    def __init__(self, item):
        super().__init__("нет на складе: " + item)


class PriceError(ShopError):
    def __init__(self, price):
        super().__init__("цена " + str(price) + " меньше нуля")


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_in20_errors(rows):
    return given_catch(rows)


def given_catch(rows):
    """Готовый помощник: бросает ошибку по строке [вид, значение] и ловит её одним except ShopError."""
    results = []
    for kind, value in rows:
        try:
            if kind == "stock":
                raise OutOfStock(value)
            elif kind == "price":
                raise PriceError(value)
            elif kind == "shop":
                raise ShopError(value)
            else:
                raise ValueError(value)
        except ShopError as error:
            results.append(type(error).__name__ + ": " + str(error))
        except Exception as error:
            results.append("не наша ошибка: " + str(error))
    return results
