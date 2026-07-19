def task_g2_vocab_filter(vocab, min_count):
    return {token: count for token, count in vocab.items() if count >= min_count}
