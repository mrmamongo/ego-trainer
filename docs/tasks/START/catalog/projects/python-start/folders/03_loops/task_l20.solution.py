def task_l20_shortest_word(words):
    best = words[0]
    for word in words:
        if len(word) < len(best):
            best = word
    return best
