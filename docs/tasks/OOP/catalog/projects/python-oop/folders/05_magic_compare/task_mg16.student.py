from dataclasses import dataclass, field


@dataclass
class Run:
    pass  # твой код: три поля и порядок сравнения


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_mg16_results(rows):
    runs = [Run(seconds, name, note) for seconds, name, note in rows]
    return {
        "names": [run.name for run in sorted(runs)],
        "first_two_equal": len(runs) >= 2 and runs[0] == runs[1],
    }
