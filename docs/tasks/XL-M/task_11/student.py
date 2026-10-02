"""XL-M-11 — Добавь retry для tool call (правка).

В цикле агента tool вызывается через agent.call_tool(name, args).
Если tool выбрасывает исключение — нужно retry до 3 раз,
посредством backoff. Реализуй call_tool_with_retry(agent, name, args):
- Пробует agent.call_tool(name, args)
- При исключении — retry с delay=0.01 * attempt (1-й, 2-й, 3-й)
- После 3-й неудачи — пробросить исключение
- Успех — вернуть результат

Не менять agent.call_tool, не менять сигнатуру.
"""

import time


def call_tool_with_retry(agent, name, args):
    # TODO: реализовать retry для tool call
    raise NotImplementedError


if __name__ == "__main__":
    class FakeAgent:
        def call_tool(self, name, args):
            return args["x"] * 2
    print(call_tool_with_retry(FakeAgent(), "mul", {"x": 5}))
