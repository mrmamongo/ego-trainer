def task_d2_sensor_alerts(readings):
    alerts = set()
    for r in readings:
        if r["temperature"] > 80 or r["humidity"] > 70:
            alerts.add(r["sensor_id"])
    return list(alerts)
