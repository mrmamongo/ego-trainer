from ego.testing import case


@case(
    args=(500,),
    expected=300,
    description='маленький заказ — доставка платная',
    level="smoke",
)

@case(
    args=(1000,),
    expected=0,
    description='ровно 1000 — доставка бесплатная',
    level="smoke",
)

@case(
    args=(5000,),
    expected=0,
    description='большой заказ — бесплатно',
    level="smoke",
)

@case(
    args=(999,),
    expected=300,
    description='999 — ещё платно',
    level="full",
)

@case(
    args=(0,),
    expected=300,
    description='пустой заказ — платно',
    level="full",
)

@case(
    args=(1001,),
    expected=0,
    description='чуть больше границы',
    level="full",
)
def task_fn08_delivery_cost(total):
    ...
