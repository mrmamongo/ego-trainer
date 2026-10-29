def task_rv11_apply_changes(profile, changes):
    result = dict(profile)
    result["tags"] = list(profile["tags"])
    for change in changes:
        if change[0] == "set":
            result[change[1]] = change[2]
        elif change[0] == "add_tag":
            if change[1] not in result["tags"]:
                result["tags"].append(change[1])
        elif change[0] == "remove_tag":
            if change[1] in result["tags"]:
                result["tags"].remove(change[1])
    return result
