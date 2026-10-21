def task_l22_final_balance(start, operations):
    balance = start
    for operation in operations:
        balance = balance + operation
        if balance < 0:
            return -1
    return balance
