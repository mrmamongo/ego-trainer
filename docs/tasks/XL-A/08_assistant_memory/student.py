"""XL-A / 08. Память помощника — задачи XL-A22, XL-A23, XL-A24.

Профиль помощника — вложенный словарь с непустыми строковыми ключами.
Листья: str, int, bool или None; списков нет. Пустой словарь допустим.
Входы нельзя менять. Задачи независимы, используют только стандартную
библиотеку и обычные словари/списки. Здесь нет solution.py или checker.py.
"""


def task_xla22_update_profile(profile, updates):
    """XL-A22. НОВЫЙ КОД — применить пакет правок к профилю.

    В настройках можно менять одну тему, например роль помощника, и
    добавлять новые ветки вроде llm.language. Реализуй последовательное
    применение обновлений, сохраняя исходные данные.

    Аргументы: profile — корректный профиль; updates — список объектов
    {"path": [непустые строки, ...], "value": scalar}. Путь непустой.
    Промежуточные отсутствующие ключи создаются. Лист на конечном пути
    добавляется или заменяется. Если промежуточный ключ уже содержит
    scalar либо конечный ключ содержит dict, обновление конфликтует:
    оно ничего не меняет, но следующие обновления всё равно выполняются.
    Равенство учитывает тип: True и 1 — разные значения. Повтор того же
    значения того же типа — no-op и в changes не попадает.

    Верни {"profile": глубокую копию результата, "changes": [...],
    "errors": [...]}. Изменение: {path: копия пути, kind: "added" или
    "changed", before: прежний scalar или None, after: новое значение}.
    Отсутствие ключа и ключ со значением None различаются через kind.
    Записи идут в порядке обновлений, одинаковый путь не объединяй.
    Ошибка: {index: индекс обновления, path: копия пути,
    reason: "path_conflict"}. Изменение профиля и updates запрещено.

    Примеры: роль tank -> healer даёт changed; отсутствующий путь
    ["llm", "language"] со значением "ru" даёт added и создаёт llm.
    Повтор ["role"]="healer" не создаёт запись. Путь ["role", "name"]
    при строковом role даёт path_conflict, не отменяя последующие правки.
    Проверь также пустой профиль, значение None и True против 1.

    Пример 1:
        profile = {"role": "tank"}
        updates = [{"path": ["role"], "value": "healer"},
                   {"path": ["llm", "language"], "value": "ru"}]
        assert task_xla22_update_profile(profile, updates) == {
            "profile": {"role": "healer", "llm": {"language": "ru"}},
            "changes": [
                {"path": ["role"], "kind": "changed", "before": "tank", "after": "healer"},
                {"path": ["llm", "language"], "kind": "added", "before": None, "after": "ru"}],
            "errors": []}

    Пример 2 — отдельный вызов, индексы снова начинаются с нуля:
        profile = {"role": "healer"}
        updates = [{"path": ["role"], "value": "healer"},
                   {"path": ["role", "name"], "value": "Mira"}]
        assert task_xla22_update_profile(profile, updates) == {
            "profile": {"role": "healer"}, "changes": [],
            "errors": [{"index": 1, "path": ["role", "name"],
                        "reason": "path_conflict"}]}
    """
    pass


def task_xla23_set_user_language(profiles, user_id, language):
    """XL-A23. НАЙТИ БАГ — смена языка одного пользователя.

    Настройки пользователей подставляются из шаблонов, поэтому профили
    могут содержать похожие предпочтения. Исправь функцию так, чтобы
    результат отражал смену языка только выбранного пользователя, а
    сохранённые исходные данные оставались прежними.

    Аргументы: profiles — словарь user_id -> профиль; каждый профиль
    содержит preferences с language и может иметь произвольные другие
    поля. user_id — строковый идентификатор; language — строка. Верни
    новый словарь профилей. Для известного пользователя в результате
    меняется только preferences.language; все остальные значения и
    профили сохраняются. Для неизвестного ID верни эквивалент исходных
    данных. Исходный profiles не меняй, включая вложенные словари.

    Пример утечки: shared={"language":"ru"}; profiles содержит
    A.preferences=shared и B.preferences=shared. Вызов для A с "en"
    должен вернуть A с "en", B с "ru", а исходные A и B оба с "ru".
    Проверь также два независимо созданных профиля: смена языка A не
    меняет B и не меняет исходный A. Неизвестный user_id не должен
    добавлять профиль или менять существующие поля. Сравнивай значения,
    но результат и вход должны быть независимы и при общих ссылках.

    Выполняемый пример: shared={"language":"ru"}; profiles={
    "A":{"preferences":shared,"theme":"dark"},
    "B":{"preferences":shared,"theme":"light"}}.
    set_user_language(profiles,"A","en") должен дать результат
    {"A":{"preferences":{"language":"en"},"theme":"dark"},
    "B":{"preferences":{"language":"ru"},"theme":"light"}};
    profiles после вызова всё ещё содержит language="ru" у A и B.
    Также вызов для user_id="missing" возвращает эквивалент входного
    словаря и не добавляет пользователя.

    Сдай исправление, кратко объясни наблюдаемый симптом и приведи
    воспроизводящий пример с ожидаемым результатом.
    """
    result = dict(profiles)
    if user_id in result:
        user = dict(result[user_id])
        preferences = user["preferences"]
        preferences["language"] = language
        user["preferences"] = preferences
        result[user_id] = user
    return result


def task_xla24_forget_topic(profile, path):
    """XL-A24. ПРАВКИ — забыть вложенную тему настроек.

    Старая команда удаляла только верхнеуровневую настройку. Теперь
    пользователь может забыть целую ветку, например игровые предпочтения,
    не потеряв соседние данные. Расширь исходное поведение до вложенных
    путей, сохранив совместимость для удаления листа верхнего уровня.

    Аргументы: profile — вложенный словарь с правилами XL-A22; path —
    список строк, который может быть пустым. Верни {"profile": глубокую
    копию результата, "removed_paths": список полных путей удалённых
    листьев}. Удаление ветки сообщает каждый её scalar-лист, включая
    None, False и 0. Пути упорядочены лексикографически по ключам на
    каждом уровне. Пустая ветка не даёт removed_paths. После удаления
    пустые словари-предки удаляются; корень остаётся словарём. Пустой
    path очищает весь профиль. Несуществующий путь или scalar на
    промежуточном шаге оставляет копию без изменений и список пустым.

    Примеры: удаление ["games", "preferences"] убирает её листья, но
    сохраняет games.rank и корневой llm. Удаление последнего листа в
    games удаляет также опустевший games. Неизвестный путь не меняет
    профиль. Пустой путь очищает профиль, а старый случай ["theme"]
    удаляет одиночный лист theme. Входные словари и path неизменны.

    Старая реализация умеет только один ключ верхнего уровня и сообщает
    удалённый лист как [path]. Доработай её; отдельно напиши рекурсивную
    функцию обхода листьев и проверь пустые словари и сортировку.

    Пример: profile={"games":{"preferences":{"sound":False,"mode":"solo"},
    "rank":0},"llm":{"language":"ru"}} и path=["games","preferences"]
    дают profile={"games":{"rank":0},"llm":{"language":"ru"}} и
    removed_paths=[["games","preferences","mode"],
    ["games","preferences","sound"]]. Путь ["missing"] оставляет
    профиль прежним и даёт []. Для profile={"games":{"x":None}} и
    path=["games","x"] результат profile={} и removed_paths=[["games","x"]].
    """
    updated = dict(profile)
    removed_paths = []
    if len(path) == 1 and path[0] in updated and not isinstance(updated[path[0]], dict):
        del updated[path[0]]
        removed_paths.append(list(path))
    return {"profile": updated, "removed_paths": removed_paths}
