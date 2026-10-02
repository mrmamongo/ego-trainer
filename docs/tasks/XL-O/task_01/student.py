"""XL-O-01 — Исправь подсчёт токенов в контексте.

Представь, что ты исправляешь маленький кусок LLM-сервиса. Перед отправкой
запроса сервис проверяет, поместятся ли история диалога и максимально
возможный ответ в context window модели.

Каждый элемент history — словарь с полями role и tokens. В истории встречаются
system, user и assistant-сообщения. Поле tokens уже рассчитано токенизатором и
не требует пересчёта. Нужно учитывать токены всех сообщений истории, включая
system и assistant, потому что они реально отправляются модели. Нельзя
учитывать поле output_tokens: это только прогноз будущего ответа, а не часть
текущего input.

Исправь функцию fits_context(history, max_output_tokens, context_limit):
она возвращает True, если сумма токенов истории и max_output_tokens меньше или
равна context_limit. Пустая история считается имеющей 0 токенов. Не меняй
history и не удаляй из неё сообщения.

Примеры:
    fits_context([{'role': 'system', 'tokens': 8}], 2, 10) == True
    fits_context([{'role': 'user', 'tokens': 8}], 3, 10) == False
    fits_context([], 0, 0) == True

Проверь отдельно границу ровно в лимит и историю, где есть assistant-сообщение.
"""


def fits_context(history, max_output_tokens, context_limit):
    # В этой версии есть намеренные ошибки. Исправь их.
    input_tokens = sum(message.get("output_tokens", 0) for message in history)
    return input_tokens + max_output_tokens < context_limit


if __name__ == "__main__":
    print(fits_context([], 10, 10))
