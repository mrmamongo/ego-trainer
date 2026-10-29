from ego.testing import case, rules

@rules(
    require_classes=['Message'],
    require_decorators={'Message': ['dataclass']},
    require_methods={'Message': ['to_dict']},
    require_functions=['message_from_dict'],
)
@case(
    args=({'author': 'Аня', 'text': 'привет', 'likes': 3},),
    expected={'author': 'Аня', 'text': 'привет', 'likes': 3},
    description='все поля на месте',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=({'author': 'Боря', 'text': 'hi'},),
    expected={'author': 'Боря', 'text': 'hi', 'likes': 0},
    description='лайков нет — ставим 0',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=({'author': 'Вика', 'text': 'ок', 'likes': 0, 'id': 17},),
    expected={'author': 'Вика', 'text': 'ок', 'likes': 0},
    description='лишние ключи отбрасываются',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=({'text': '', 'author': 'Ира'},),
    expected={'author': 'Ира', 'text': '', 'likes': 0},
    description='пустой текст, порядок ключей не важен',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=({'author': 'Толя', 'text': 'много', 'likes': 1000, 'tags': ['а'], 'id': 1},),
    expected={'author': 'Толя', 'text': 'много', 'likes': 1000},
    description='несколько лишних ключей',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_dc12_normalize(data):
    ...
