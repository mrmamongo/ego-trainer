def task_di19_set_language(profiles, user, lang):
    result = {}
    for name, profile in profiles.items():
        new_profile = dict(profile)
        new_profile["prefs"] = dict(profile["prefs"])
        result[name] = new_profile
    if user in result:
        result[user]["prefs"]["language"] = lang
    return result
