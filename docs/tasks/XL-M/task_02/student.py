"""XL-M-02 — Исправь подсчёт стоимости токенов (баг: неправильная цена).

Сервис считает стоимость запроса: price_per_1k токенов × токены / 1000.
В текущей версии цена для user-токенов и output-токенов одинаковая,
но на самом деле модель берёт разную цену за input и output.

Исправь calc_cost(prompt_tokens, output_tokens, input_price, output_price):
- prompt_tokens × input_price / 1000 + output_tokens × output_price / 1000
- Все значения неотрицательные. Пустые токены = 0.

Примеры:
    calc_cost(1000, 500, 0.01, 0.03) == 0.01 * 1 + 0.03 * 0.5 == 0.025
    calc_cost(0, 0, 0.01, 0.03) == 0.0
"""


def calc_cost(prompt_tokens, output_tokens, input_price, output_price):
    # Намеренная ошибка: одна цена для обоих
    total = (prompt_tokens + output_tokens) * input_price / 1000
    return round(total, 6)


if __name__ == "__main__":
    print(calc_cost(1000, 500, 0.01, 0.03))
