def task_1_5_sla_report(logs):
    stats = {}
    for e in logs:
        svc = e["service"]
        if svc not in stats:
            stats[svc] = {"total": 0, "success": 0}
        stats[svc]["total"] += 1
        if 200 <= e["status"] <= 299:
            stats[svc]["success"] += 1
    report = []
    for svc, s in sorted(stats.items()):
        sla = round((s["success"] / s["total"]) * 100)
        report.append({
            "service": svc, "total": s["total"],
            "success": s["success"], "sla_percent": sla,
        })
    return report
