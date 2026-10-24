def task_r17_years_to_target(balance, percent, target):
    years = 0
    while balance < target:
        balance = balance + balance * percent // 100
        years = years + 1
    return years
