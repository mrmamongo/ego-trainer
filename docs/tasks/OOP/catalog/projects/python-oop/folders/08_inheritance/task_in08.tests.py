from ego.testing import case, rules

@rules(
    require_functions=['task_in08_total_damage'],
)
@case(
    args=(['Warrior', 'Mage', 'Unit'],),
    expected=26,
    description='три вида',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(['Warrior', 'Warrior'],),
    expected=24,
    description='два воина',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(['Mage'],),
    expected=9,
    description='один маг',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([],),
    expected=0,
    description='пустой отряд',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(['Unit', 'Unit', 'Mage', 'Warrior', 'Mage'],),
    expected=40,
    description='смешанный отряд',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_in08_total_damage(kinds):
    ...
