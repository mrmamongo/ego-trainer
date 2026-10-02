"""XL-O-13 — Политика выбора tools (правка).

Реализуй check_tool_call(tool, args, policy, history). Policy содержит
allowed_tools, max_calls, confirm_required и allowed_args. Верни объект
{'allowed': bool, 'reason': str, 'requires_confirmation': bool}. Отклоняй
неизвестный tool, лишние аргументы, превышение лимита и повторный вызов с
теми же аргументами. Опасные tools требуют подтверждения.
"""


def check_tool_call(tool, args, policy, history):
    # TODO: реализовать проверку до фактического вызова
    raise NotImplementedError
