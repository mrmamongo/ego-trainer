class ShopError(Exception):
    pass


class OutOfStock(ShopError):
    def __init__(self, item):
        pass  # твой код: передай родителю текст "нет на складе: " и название товара


class PriceError(ShopError):
    def __init__(self, price):
        pass  # твой код: передай родителю текст "цена ... меньше нуля" с этой ценой


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
