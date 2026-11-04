class Employee:
    def __init__(self, name, base):
        pass  # твой код

    def salary(self):
        return None  # твой код


class Manager(Employee):
    def __init__(self, name, base, bonus):
        pass  # твой код

    def salary(self):
        return None  # твой код


class Intern(Employee):
    def salary(self):
        return None  # твой код


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_in15_payroll(rows):
    return given_payroll({"Employee": Employee, "Manager": Manager, "Intern": Intern}, rows)


def given_payroll(classes, rows):
    """Готовый помощник: строит сотрудников по строкам [класс, аргументы...] и собирает "имя: зарплата"."""
    staff = [classes[row[0]](*row[1:]) for row in rows]
    return [f"{person.name}: {person.salary()}" for person in staff]
