def task_ts10_count_unique_words(text):
    unique = set()
    for word in text.lower().split():
        unique.add(word.strip(".,!?"))
    return len(unique)
