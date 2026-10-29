from dataclasses import dataclass, field


@dataclass(order=True)
class Run:
    seconds: int
    name: str
    note: str = field(default="", compare=False)


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_mg16_results(rows):
    runs = [Run(seconds, name, note) for seconds, name, note in rows]
    return {
        "names": [run.name for run in sorted(runs)],
        "first_two_equal": len(runs) >= 2 and runs[0] == runs[1],
    }
