def task_f2_active_emails(users):
    return [u["email"] for u in users if u["active"]]
