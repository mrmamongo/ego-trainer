def task_di07_letter_freq(word):
    counts = {}
    for letter in word:
        counts[letter] = counts.get(letter, 0) + 1
    return counts
