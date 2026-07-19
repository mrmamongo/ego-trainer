def task_g6_pad_batch(sequences, pad_token):
    if not sequences:
        return {"padded": [], "attention_mask": []}
    max_len = max(len(seq) for seq in sequences)
    padded = []
    masks = []
    for seq in sequences:
        pad_count = max_len - len(seq)
        padded.append(seq + [pad_token] * pad_count)
        masks.append([1] * len(seq) + [0] * pad_count)
    return {"padded": padded, "attention_mask": masks}
