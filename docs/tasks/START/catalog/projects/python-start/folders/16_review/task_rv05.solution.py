def task_rv05_totals_by_customer(orders):
    totals = {}
    for order in orders:
        customer = order["customer"]
        if customer in totals:
            totals[customer] = totals[customer] + order["total"]
        else:
            totals[customer] = order["total"]
    return totals
