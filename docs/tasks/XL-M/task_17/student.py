"""XL-M-17 — Добавь guard-состояние для agent (правка).

Агент может находиться в состояниях:
"idle", "running", "paused", "stopped".
Реализуй set_state(agent, new_state):
- Допустимые переходы:
  idle → running, running → paused,
  paused → running, paused → stopped,
  running → stopped, stopped → idle
- Остальные переходы — raise ValueError.
- Мутируй agent["state"] и верни agent.

Пример:
    set_state({"state": "idle"}, "running")
    → {"state": "running"}
    set_state({"state": "running"}, "idle")  # ValueError
"""


def set_state(agent, new_state):
    allowed = {
        "idle": {"running"},
        "running": {"paused", "stopped"},
        "paused": {"running", "stopped"},
        "stopped": {"idle"},
    }
    cur = agent["state"]
    if new_state not in allowed.get(cur, set()):
        raise ValueError(f"bad transition {cur} -> {new_state}")
    agent["state"] = new_state
    return agent


if __name__ == "__main__":
    print(set_state({"state": "idle"}, "running"))
