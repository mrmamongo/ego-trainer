def task_di21_add_tag(profile, tag):
    new_profile = dict(profile)
    new_profile["tags"] = list(profile["tags"])
    if tag not in new_profile["tags"]:
        new_profile["tags"].append(tag)
    return new_profile
