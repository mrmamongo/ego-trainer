def task_g4_compute_accuracy(predicted, actual):
    if not predicted:
        return 0.0
    correct = sum(1 for p, a in zip(predicted, actual) if p == a)
    return correct / len(predicted)
