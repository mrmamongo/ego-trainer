from ego.testing import case

@case(
    args=(),
    expected=(3, 'email a@x.ru: Привет, мир', 'sms +7900: Приве', 'уведомление: Привет, мир', False),
    description='ответы на трассировку указаны верно',
    level='smoke',
    hide_expected=True,
)
def task_in04_poly():
    ...
