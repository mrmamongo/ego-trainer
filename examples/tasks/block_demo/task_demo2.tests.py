from ego.testing import case

@case(
    args=(4,),
    expected='even',
    description='even',
)
@case(
    args=(7,),
    expected='odd',
    description='odd',
)
@case(
    args=(0,),
    expected='even',
    description='zero',
)
def task_demo2_even_odd(n):
    ...
