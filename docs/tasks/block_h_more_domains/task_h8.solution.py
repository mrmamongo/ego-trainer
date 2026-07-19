def task_h8_tiered_synthesis(inventory):
    result = {}
    for name, tiers in inventory.items():
        c, u, r = tiers["C"], tiers["U"], tiers["R"]
        u_crafted = c // 3
        c_rem = c % 3
        total_u = u + u_crafted
        r_crafted = total_u // 3
        u_rem = total_u % 3
        result[name] = {"C": c_rem, "U": u_rem, "R": r + r_crafted}
    return result
