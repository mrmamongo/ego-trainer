def task_s03_count_vowels(text):
    vowels = "аеёиоуыэюяaeiou"
    count = 0
    for ch in text.lower():
        if ch in vowels:
            count += 1
    return count
