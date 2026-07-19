def task_1_4_services_with_500(logs):
    return list({e["service"] for e in logs if e["status"] == 500})
