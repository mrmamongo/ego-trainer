def transform(n, rule):
    if rule == "double":
        return n * 2
    if rule == "square":
        return n * n
    if rule == "negate":
        return -n
    return n


def task_fd16_apply(nums, rule):
    result = []
    for n in nums:
        result.append(transform(n, rule))
    return result
