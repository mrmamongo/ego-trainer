from ego.testing import case

@case(
    args=(['ананас', 'банан', 'арбуз'],),
    expected={'а': ['ананас', 'арбуз'], 'б': ['банан']},
    description='две группы',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(['кот'],),
    expected={'к': ['кот']},
    description='одно слово',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([],),
    expected={},
    description='пустой список',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(['дом', 'дым', 'дно'],),
    expected={'д': ['дом', 'дым', 'дно']},
    description='все на одну букву, порядок сохраняется',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(['a', 'b', 'c'],),
    expected={'a': ['a'], 'b': ['b'], 'c': ['c']},
    description='каждое слово в своей группе',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(['лук', 'мак', 'лис', 'мёд', 'лев'],),
    expected={'л': ['лук', 'лис', 'лев'], 'м': ['мак', 'мёд']},
    description='группы чередуются',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_di08_group_by_first(words):
    ...
