def task_ns06_trace():
    # Код для трассировки (не меняй и не запускай):
    #
    #   1 | def get_path(data, path, default):
    #   2 |     current = data
    #   3 |     for key in path:
    #   4 |         if type(current) is not dict or key not in current:
    #   5 |             return default
    #   6 |         current = current[key]
    #   7 |     return current
    #   8 | data = {"profile": {"settings": {"lang": "ru"}, "age": 30}}
    #   9 | a = get_path(data, ["profile", "settings", "lang"], "нет")
    #  10 | b = get_path(data, ["profile", "theme"], "пусто")
    #  11 | c = get_path(data, ["profile", "age", "x"], "-")
    #
    # Впиши вместо None, что получится (текст в кавычках, числа без кавычек).

    # lang_value: что вернул вызов a.
    lang_value = None
    # theme_value: что вернул вызов b.
    theme_value = None
    # through_scalar: что вернул вызов c.
    through_scalar = None
    # steps_a: сколько раз выполнилась строка 6 в вызове a.
    steps_a = None
    # steps_b: сколько раз выполнилась строка 6 в вызове b.
    steps_b = None
    # steps_c: сколько раз выполнилась строка 6 в вызове c.
    steps_c = None

    # Ниже ничего не меняй: это рамка для проверки.
    return lang_value, theme_value, through_scalar, steps_a, steps_b, steps_c
