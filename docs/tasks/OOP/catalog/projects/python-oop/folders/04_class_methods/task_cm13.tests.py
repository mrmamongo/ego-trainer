from ego.testing import case, rules

@rules(
    require_functions=['retry_once'],
)
@case(
    args=(0,),
    expected=['готово', 1],
    description='сбоев нет — одна попытка',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(1,),
    expected=['готово', 2],
    description='один сбой — вторая попытка удалась',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(2,),
    expected=[['error', 'ValueError', 'сбой'], 2],
    description='два сбоя — ошибка уходит наружу',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(5,),
    expected=[['error', 'ValueError', 'сбой'], 2],
    description='больше двух попыток не делаем',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(3,),
    expected=[['error', 'ValueError', 'сбой'], 2],
    description='три сбоя — всё равно две попытки',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_cm13_retry(fail_times):
    ...
