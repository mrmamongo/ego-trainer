"""XL-O-06 — Напиши валидатор ответа модели по простой схеме.

LLM возвращает JSON, который нужно проверить до передачи в бизнес-логику.
Реализуй validate_model_output(value, schema). Поддержи типы str, int, float,
bool, list и object. Для object схема задаёт properties, а required — имена
обязательных полей. Для list схема items описывает элементы.

Если поле отсутствует, но у него есть default, добавь default в нормализованный
результат. Лишние поля можно сохранить. Необходимо собрать все ошибки, а не
останавливаться на первой. Каждая ошибка должна содержать path и message;
пути выглядят как user.name или items[2].price.

Верни {'ok': True, 'value': normalized, 'errors': []}, если ошибок нет, или
{'ok': False, 'value': normalized, 'errors': [...]} иначе. Исходный value и
вложенные структуры не мутируй. Учти, что bool не должен считаться int.
"""


def validate_model_output(value, schema):
    # TODO: реализовать рекурсивную проверку
    raise NotImplementedError
