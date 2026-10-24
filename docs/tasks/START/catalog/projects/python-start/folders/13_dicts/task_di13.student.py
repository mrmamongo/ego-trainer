def task_di13_trace():
    # Код для трассировки (не меняй и не запускай):
    #
    #   1 | anna = {"name": "Аня", "tags": ["admin", "dev"]}
    #   2 | boris = {"name": "Боря", "tags": ["dev", "test", "ops"]}
    #   3 | data = {"users": [anna, boris], "total": 2}
    #   4 | a = data["users"][1]["name"]
    #   5 | b = data["users"][1]["tags"][0]
    #   6 | c = len(data["users"][0]["tags"])
    #   7 | d = data["total"] + len(boris["tags"])
    #   8 | data["users"][0]["tags"].append("qa")
    #   9 | e = len(anna["tags"])
    #
    # second_name: значение a (имя второго пользователя)
    # second_first_tag: значение b (первый тег второго пользователя)
    # first_tags_count: значение c (сколько тегов у первого пользователя)
    # sum_value: значение d
    # anna_tags_final: значение e (длина anna["tags"] после строки 8)

    second_name = None
    second_first_tag = None
    first_tags_count = None
    sum_value = None
    anna_tags_final = None

    # Ниже ничего не меняй: это рамка для проверки.
    return second_name, second_first_tag, first_tags_count, sum_value, anna_tags_final
