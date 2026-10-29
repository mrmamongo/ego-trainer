class Ticket:
    def __init__(self, number, priority):
        self.number = number
        self.priority = priority

    def __lt__(self, other):
        if self.priority != other.priority:
            return self.priority > other.priority
        return self.number < other.number


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_mg07_queue(rows):
    tickets = [Ticket(number, priority) for number, priority in rows]
    return [ticket.number for ticket in sorted(tickets)]
