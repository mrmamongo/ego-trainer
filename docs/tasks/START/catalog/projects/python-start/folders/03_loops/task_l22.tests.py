from ego.testing import case

@case(
    args=(100, [50, -30]),
    expected=120,
    description='пополнение и списание',
    level="smoke",
)

@case(
    args=(100, [-50, -60]),
    expected=-1,
    description='уходим в минус',
    level="smoke",
)

@case(
    args=(50, []),
    expected=50,
    description='нет операций',
    level="smoke",
)

@case(
    args=(0, [10, -10]),
    expected=0,
    description='ноль не отрицательный',
    level="full",
)

@case(
    args=(10, [-20, 100]),
    expected=-1,
    description='минус нельзя исправить потом',
    level="full",
)

@case(
    args=(100, [-100, 5]),
    expected=5,
    description='опустились до нуля и вернулись',
    level="full",
)

@case(
    args=(5, [3, 3, -20, 100]),
    expected=-1,
    description='минус посреди цепочки',
    level="full",
)
def task_l22_final_balance(start, operations):
    ...
