from copy import deepcopy


def task_xla23_set_user_language(profiles, user_id, language):
    result = deepcopy(profiles)
    if user_id in profiles:
        # Separate the selected profile even when multiple users share it.
        user = deepcopy(profiles[user_id])
        # Preferences may also be shared with another field of this profile.
        user["preferences"] = deepcopy(user["preferences"])
        user["preferences"]["language"] = language
        result[user_id] = user
    return result
