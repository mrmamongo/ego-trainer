from ego.testing import case, rules

@rules(
    require_functions=['run_command'],
)
@case(
    args=('/hello Аня',),
    expected='Привет, Аня!',
    description='команда hello',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=('/shout привет мир',),
    expected='ПРИВЕТ МИР',
    description='аргумент из нескольких слов',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=('/count один два три',),
    expected=3,
    description='обработчик возвращает число',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=('/dance',),
    expected='неизвестная команда: dance',
    description='такой команды нет',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=('привет всем',),
    expected='это не команда',
    description='нет слэша в начале',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=('',),
    expected='это не команда',
    description='пустая строка',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=('/count',),
    expected=0,
    description='команда без аргумента',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=('/shout',),
    expected='',
    description='пустой аргумент отдаётся обработчику',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=('/hello Аня Петрова',),
    expected='Привет, Аня Петрова!',
    description='аргумент целиком, а не первое слово',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_cm11_chat(line):
    ...
