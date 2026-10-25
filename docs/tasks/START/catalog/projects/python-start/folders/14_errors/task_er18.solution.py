def check_text(profile, key, path, problems):
    if key not in profile:
        problems.append(path + ": missing")
    elif type(profile[key]) is not str:
        problems.append(path + ": wrong_type")
    elif profile[key].strip() == "":
        problems.append(path + ": empty")


def task_er18_validate_profile(profile):
    problems = []
    check_text(profile, "name", "name", problems)
    if "age" not in profile:
        problems.append("age: missing")
    elif type(profile["age"]) is not int:
        problems.append("age: wrong_type")
    elif profile["age"] < 0 or profile["age"] > 150:
        problems.append("age: out_of_range")
    if "address" not in profile:
        problems.append("address: missing")
    elif type(profile["address"]) is not dict:
        problems.append("address: wrong_type")
    else:
        address = profile["address"]
        check_text(address, "city", "address.city", problems)
        if "zip" not in address:
            problems.append("address.zip: missing")
        elif type(address["zip"]) is not str:
            problems.append("address.zip: wrong_type")
        elif len(address["zip"]) != 6 or not address["zip"].isdigit():
            problems.append("address.zip: bad_format")
    if "email" in profile:
        if type(profile["email"]) is not str:
            problems.append("email: wrong_type")
        elif "@" not in profile["email"]:
            problems.append("email: bad_format")
    return sorted(problems)
