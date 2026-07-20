def task_f4_all_passed(tests):
    for t in tests:
        if t["result"] != "passed":
            return False
    return True
