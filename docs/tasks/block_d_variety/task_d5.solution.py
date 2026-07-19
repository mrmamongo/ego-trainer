def task_d5_endpoint_stats(requests):
    stats = {}
    for req in requests:
        ep = req["endpoint"]
        if ep not in stats:
            stats[ep] = {"total_ms": 0, "count": 0}
        stats[ep]["total_ms"] += req["ms"]
        stats[ep]["count"] += 1
    report = []
    for ep, s in sorted(stats.items()):
        report.append({
            "endpoint": ep,
            "count": s["count"],
            "avg_ms": round(s["total_ms"] / s["count"]),
        })
    return report
