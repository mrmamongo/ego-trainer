"""XL-M-14 — Кэшируй результаты tool call (правка).

Агент повторно вызывает одни и те же tools с
одинаковыми args. Реализуй memoize_tool(tool_fn):
- Кэшируй результат по (name, args_key) — args_key
  это frozenset(args.items()) если args dict,
  иначе tuple(args).
- Если результат уже в кэше — верни его
  без вызова tool_fn.
- Кэш хранится на уровне функции (nonlocal dict).

Пример:
    calls = 0
    def double(x):
        nonlocal calls; calls += 1; return x*2
    m = memoize_tool(double)
    m("double", (5,))  # вызовет double
    m("double", (5,))  # вернёт из кэша, calls не изменится
"""


def memoize_tool(tool_fn):
    cache = {}

    def wrapper(name, args):
        key = (name, args)
        if key in cache:
            return cache[key]
        result = tool_fn(*args) if isinstance(args, tuple) else tool_fn(args)
        cache[key] = result
        return result

    return wrapper


if __name__ == "__main__":
    def double(x):
        return x * 2
    m = memoize_tool(double)
    print(m("double", (5,)), m("double", (5,)))
