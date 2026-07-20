def task_1_3_slow_requests(logs):
    return [
        {"timestamp": e["timestamp"], "service": e["service"]}
        for e in logs if e["response_time_ms"] > 500
    ]
