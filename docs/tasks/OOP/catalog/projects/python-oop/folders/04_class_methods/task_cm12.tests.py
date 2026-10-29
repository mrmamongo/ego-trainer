from ego.testing import case, rules

@rules(
    require_functions=['limit_three'],
)
@case(
    args=(['а', 'б'], ['в']),
    expected=[['отправлено: а', 'отправлено: б'], ['отправлено: в']],
    description='лимит не исчерпан',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(['а', 'б', 'в'], []),
    expected=[['отправлено: а', 'отправлено: б', 'отправлено: в'], []],
    description='ровно три вызова проходят',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(['а', 'б', 'в', 'г'], []),
    expected=[['отправлено: а', 'отправлено: б', 'отправлено: в', None], []],
    description='четвёртый вызов даёт None',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(['1', '2', '3', '4'], ['5', '6']),
    expected=[['отправлено: 1', 'отправлено: 2', 'отправлено: 3', None], ['отправлено: 5', 'отправлено: 6']],
    description='у каждой обёртки свой счётчик',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([], []),
    expected=[[], []],
    description='вызовов нет',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(['а', 'а', 'а', 'а', 'а', 'а'], ['б', 'б', 'б', 'б']),
    expected=[['отправлено: а', 'отправлено: а', 'отправлено: а', None, None, None], ['отправлено: б', 'отправлено: б', 'отправлено: б', None]],
    description='много вызовов сверх лимита',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_cm12_limit(first, second):
    ...
