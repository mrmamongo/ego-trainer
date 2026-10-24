def task_di18_trace():
    # Код для трассировки (не меняй и не запускай):
    #
    #   1 | base = {"lang": "ru", "tags": ["new"]}
    #   2 | users = {"anna": base, "boris": base}
    #   3 | users["anna"]["lang"] = "en"
    #   4 | a = users["boris"]["lang"]
    #   5 | copy1 = dict(base)
    #   6 | copy1["lang"] = "de"
    #   7 | b = base["lang"]
    #   8 | copy1["tags"].append("vip")
    #   9 | c = len(base["tags"])
    #  10 | d = users["anna"] is users["boris"]
    #  11 | e = copy1 is base
    #
    # boris_lang: значение a
    # base_lang: значение b (base["lang"] после строки 6)
    # base_tags_len: значение c (длина base["tags"] после строки 8)
    # same_user_dict: значение d (True или False)
    # copy_is_base: значение e (True или False)

    boris_lang = None
    base_lang = None
    base_tags_len = None
    same_user_dict = None
    copy_is_base = None

    # Ниже ничего не меняй: это рамка для проверки.
    return boris_lang, base_lang, base_tags_len, same_user_dict, copy_is_base
