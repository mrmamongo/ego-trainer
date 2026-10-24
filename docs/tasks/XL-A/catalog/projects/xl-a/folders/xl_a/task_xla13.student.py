"""
XL-A13. НОВЫЙ КОД — проверить намерение и подготовить команду.

Здесь мы безопасно готовим и проигрываем игровые действия: сначала
проверяем, что игрок имел в виду, а потом показываем (или применяем)
результат — без риска что-то сломать в игре.
Все данные локальные: функция не обращается к сети, модели или самой игре.
Аргументы не меняются. Задачи независимы друг от друга, а готовые
функции (GIVEN) можно вызывать, но нельзя изменять.

Работай с этой функцией. GIVEN-помощники можно вызывать, но нельзя изменять.
"""


# GIVEN: готовый помощник для этой задачи.


def given_find_matches(items, field, value):
    """GIVEN: найти все записи с точным совпадением значения поля."""
    return [item for item in items if item[field] == value]


def task_xla13_prepare_action(raw, members, events):
    """
        XL-A13. НОВЫЙ КОД — проверить намерение и подготовить команду.

        Модель Assistant уже разобрала просьбу игрока в словарь, но выполнять
        его сразу нельзя: игрок мог назвать несуществующего участника или
        событие. Проверь данные и преврати названия в реальные ID, чтобы
        команда гарантированно сработала. Настоящего вызова игры здесь нет.

        Аргументы:
            raw={tool: строка, args: словарь}.
            Допустимы create_event с title и capacity; join_event с member_name
            и event_title. members=[{id,name}], events=[{id,title,capacity,
            members:[member ID]}]. ID уникальны, имена — нет. Сравнение точное.
            Названия из raw сначала strip(); регистр не меняй. Для имени или
            названия события отсутствующее поле, None, значение не-строка или
            пустая после strip() строка считаются *_empty. Записи каталога
            гарантированно имеют строковые name/title и ID; у событий capacity
            — целое >= 1, members — список ID.

        Всегда верни {status:'ready' или 'rejected', command:..., errors:[...]}.
        Для create_event сначала проверь title: пустая после strip() строка
        даёт title_empty. Затем capacity: нужен int >= 1, bool целым не
        считается; иначе invalid_capacity. Готовая команда содержит tool и args
        с очищенным title и прежним capacity.
        Если неверны оба поля, верни обе ошибки в указанном порядке.
        Отсутствующий или нестроковый title тоже даёт title_empty.
        Лишние поля args игнорируй: в готовую команду входят только описанные поля.
        Для join_event сначала проверь участника, затем событие, и собери обе
        независимые ошибки поиска, если они есть. Пустые поля дают
        member_name_empty / event_title_empty. Ноль совпадений —
        unknown_member / unknown_event; больше одного — ambiguous_member /
        ambiguous_event. При уникальных совпадениях проверь уже вступил ли
        участник (already_joined), затем заполненность (event_full).
        Готовые args — только member_id и event_id. Ошибки возвращай в этом
        порядке; при отказе command=None. Неизвестный tool даёт ['unknown_tool'].

        Примеры:
            members=[{"id":"m1","name":"Ира"}]; events=[]
            raw={"tool":"create_event","args":{"title":"  Рейд  ","capacity":4}}
            task_xla13_prepare_action(raw, members, events) == {
                "status":"ready","command":{"tool":"create_event",
                "args":{"title":"Рейд","capacity":4}},"errors":[]}
        Второй пример: members=[{"id":"m1","name":"Ира"},
        {"id":"m2","name":"Ира"}], events=[] и raw=
        {"tool":"join_event","args":{"member_name":"Ира","event_title":"Луна"}}
        дают {"status":"rejected","command":None,
        "errors":["ambiguous_member","unknown_event"]}.
        Третий пример: members=[{"id":"m1","name":"Ира"}], events=[
        {"id":"e1","title":"Рейд","capacity":1,"members":["m2"]}];
        join Ира в Рейд даёт rejected, command=None, errors=['event_full'].
        Если участник уже в заполненном событии, ошибка только already_joined.
        Используй given_find_matches для поиска. Входные данные не меняй.
        """
    pass
