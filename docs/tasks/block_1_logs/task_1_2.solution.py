def task_1_2_errors_by_service(logs):
    d = {}
    for e in logs:
        if e["level"] == "ERROR":
            svc = e["service"]
            d[svc] = d.get(svc, 0) + 1
    return d
