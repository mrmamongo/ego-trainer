# Сейчас функция меняет профиль на месте и ничего не возвращает.
def task_di21_add_tag(profile, tag):
    if tag not in profile["tags"]:
        profile["tags"].append(tag)
