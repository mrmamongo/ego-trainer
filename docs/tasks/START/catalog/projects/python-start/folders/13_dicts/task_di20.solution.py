def task_di20_deep_copy_profiles(profiles):
    result = {}
    for name, profile in profiles.items():
        new_profile = {}
        for field, items in profile.items():
            new_profile[field] = list(items)
        result[name] = new_profile
    return result
