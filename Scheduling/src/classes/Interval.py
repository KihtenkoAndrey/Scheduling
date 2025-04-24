# Интервалы
class Interval:
    def __init__(self, start, end, duration=None, number=None):
        self.start = start
        self.end = end
        self.duration = duration
        self.number = number
        self.ACTIVITIES = []  # Список активностей
        self.MACHINES = []  # Список машин с производительностями
        
    def add_activity(self, act):
        self.ACTIVITIES.append(act)
    
    def add_machine(self, machine):
        self.MACHINES.append(machine)
        
    def __eq__(self, other):
        return self.number == other.number

    def __hash__(self):
        return hash(self.number)