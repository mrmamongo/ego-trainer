from ego.testing import case, rules

@rules(
    require_classes=['Temperature'],
    require_decorators={'Temperature.celsius': ['property'], 'Temperature.fahrenheit': ['property']},
    require_methods={'Temperature': ['__init__']},
)
@case(
    args=([['new', 100], ['get', 'celsius'], ['get', 'fahrenheit']],),
    expected=['ok', 100, 212.0],
    description='температура кипения',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 20], ['set', 'celsius', 37.5], ['get', 'celsius'], ['get', 'fahrenheit']],),
    expected=['ok', 'ok', 37.5, 99.5],
    description='новое значение через свойство',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', -300], ['new', 0], ['get', 'fahrenheit']],),
    expected=[['error', 'ValueError', 'ниже абсолютного нуля'], 'ok', 32.0],
    description='ниже абсолютного нуля объект не создаётся',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 10], ['set', 'celsius', -273.16], ['get', 'celsius']],),
    expected=['ok', ['error', 'ValueError', 'ниже абсолютного нуля'], 10],
    description='отклонённое значение не записывается',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 0], ['set', 'celsius', -273.15], ['get', 'celsius']],),
    expected=['ok', 'ok', -273.15],
    description='граница допустима',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', -40], ['get', 'fahrenheit']],),
    expected=['ok', -40.0],
    description='шкалы совпадают',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 10], ['set', 'fahrenheit', 50], ['get', 'celsius']],),
    expected=['ok', ['error', 'AttributeError', ''], 10],
    description='Фаренгейт только для чтения',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 0], ['set', 'celsius', 100], ['get', 'fahrenheit']],),
    expected=['ok', 'ok', 212.0],
    description='Фаренгейт пересчитывается',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_pr09_temperature(actions):
    ...
