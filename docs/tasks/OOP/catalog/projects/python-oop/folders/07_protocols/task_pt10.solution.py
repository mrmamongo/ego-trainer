import io


def task_pt10_count(text):
    file = io.StringIO(text)
    count = 0
    for line in file:
        if line.startswith("ERROR"):
            count += 1
    return count
