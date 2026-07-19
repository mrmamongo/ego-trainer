def task_d3_failed_builds(builds):
    return [
        {"build_id": b["build_id"], "duration_sec": b["duration_sec"], "branch": b["branch"]}
        for b in builds if b["status"] == "failed"
    ]
