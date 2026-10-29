from ego.testing import case, rules

@rules(
    require_classes=['Message'],
    require_decorators={'Message': ['dataclass']},
    require_methods={'Message': ['to_dict']},
)
@case(
    args=([{'author': 'Аня', 'text': 'раз', 'likes': 5}, {'author': 'Боря', 'text': 'два'}, {'author': 'Вика', 'text': 'три', 'likes': 9}], 1),
    expected=[{'author': 'Вика', 'text': 'три', 'likes': 9}, {'author': 'Аня', 'text': 'раз', 'likes': 5}],
    description='отсекаем сообщения без лайков',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([{'author': 'Аня', 'text': 'раз', 'likes': 5}, {'author': 'Боря', 'text': 'два'}, {'author': 'Вика', 'text': 'три', 'likes': 9}], 0),
    expected=[{'author': 'Вика', 'text': 'три', 'likes': 9}, {'author': 'Аня', 'text': 'раз', 'likes': 5}, {'author': 'Боря', 'text': 'два', 'likes': 0}],
    description='все сообщения, у Бори лайков нет — значит 0',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([], 1),
    expected=[],
    description='пустой список',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([{'author': 'Яна', 'text': 'а', 'likes': 4}, {'author': 'Анна', 'text': 'б', 'likes': 4}, {'author': 'Олег', 'text': 'в', 'likes': 4}], 4),
    expected=[{'author': 'Анна', 'text': 'б', 'likes': 4}, {'author': 'Олег', 'text': 'в', 'likes': 4}, {'author': 'Яна', 'text': 'а', 'likes': 4}],
    description='граница входит, равные — по автору',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([{'author': 'Аня', 'text': 'раз', 'likes': 5}, {'author': 'Боря', 'text': 'два'}, {'author': 'Вика', 'text': 'три', 'likes': 9}], 100),
    expected=[],
    description='никто не набрал',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([{'author': 'Аня', 'text': 'один', 'likes': 1}], 1),
    expected=[{'author': 'Аня', 'text': 'один', 'likes': 1}],
    description='ровно на границе',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_dc14_popular(items, min_likes):
    ...
