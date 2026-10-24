def task_di19_set_language(profiles, user, lang):
    result = dict(profiles)
    if user in result:
        result[user]["prefs"]["language"] = lang
    return result
