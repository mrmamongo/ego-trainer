from ego.testing import case, rules

@rules(
    require_classes=['Playlist'],
    require_methods={'Playlist': ['__init__', '__len__', '__getitem__']},
)
@case(
    args=(['rock', 'jazz'], [0, -1, 2]),
    expected={'len': 2, 'items': ['rock', 'jazz', ['IndexError', 'нет такого трека']]},
    description='обычные и лишний',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(['a', 'b', 'c'], [1]),
    expected={'len': 3, 'items': ['b']},
    description='один индекс',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([], [0]),
    expected={'len': 0, 'items': [['IndexError', 'нет такого трека']]},
    description='пустой плейлист',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(['a', 'b', 'c'], [-3, -4, 3]),
    expected={'len': 3, 'items': ['a', ['IndexError', 'нет такого трека'], ['IndexError', 'нет такого трека']]},
    description='границы',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(['solo'], []),
    expected={'len': 1, 'items': []},
    description='без запросов',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([], []),
    expected={'len': 0, 'items': []},
    description='всё пусто',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_mo14_playlist(tracks, indexes):
    ...
