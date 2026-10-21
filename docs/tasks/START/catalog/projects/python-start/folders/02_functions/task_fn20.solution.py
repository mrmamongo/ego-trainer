def task_fn20_can_enter(age, has_ticket, is_vip):
    return age >= 18 and (has_ticket or is_vip)
