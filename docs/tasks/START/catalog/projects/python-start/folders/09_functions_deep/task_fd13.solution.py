def normalize(word):
    return word.lower().strip(".,!?")


def task_fd13_count_unique_words(text):
    seen = []
    for word in text.split():
        clean = normalize(word)
        if clean != "" and clean not in seen:
            seen.append(clean)
    return len(seen)
