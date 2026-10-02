"""XL-O-08 — Добавь расчёт стоимости LLM-запроса.

В сервисе уже собираются input/output tokens, но продукту нужно показывать
стоимость запроса и предупреждать о дневном лимите. Реализуй
estimate_cost(model, input_tokens, output_tokens, tariffs, daily_spent=0,
daily_budget=None).

В tariffs[model] лежит {'input_per_1k': ..., 'output_per_1k': ...}. Стоимость
считается отдельно для входа и выхода: токены / 1000 * соответствующий тариф,
затем складываются. Округли cost до 6 знаков после запятой. Верни словарь с
model, cost и budget_exceeded. Последний True только если daily_budget задан и
 daily_spent + cost строго больше него; ровное достижение лимита допустимо.

Для неизвестной модели выброси ValueError с понятным сообщением. Отрицательные
токены и отрицательный daily_spent тоже должны приводить к ValueError.
Нулевые токены и отсутствие дневного бюджета — нормальные случаи. Не меняй
словарь тарифов.
"""


def estimate_cost(model, input_tokens, output_tokens, tariffs, daily_spent=0, daily_budget=None):
    # TODO: реализовать
    raise NotImplementedError
