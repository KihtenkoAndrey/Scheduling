
# Машины с производительностями
class Machine:
    def __init__(self, machine_id, power, type=None, name=None):
        self.machine_id = machine_id
        self.type = type
        self.power = power
        self.name = name
        self.label = f"Машина_{machine_id}" 
        self.ACTIVITIES = []  # Список активностей
        self.INTERVALS = set() # Список интервалов
        
    def add_activity(self, act):
        self.ACTIVITIES.append(act)
        
    def add_interval(self, interval):
        self.INTERVALS.add(interval)
        
    def __repr__(self):
        return (f"MACHINE(machine_id={self.machine_id}, name={self.name}, "
                f"power={self.power}, type={self.type})")
    
    def __eq__(self, other):
        return self.machine_id == other.machine_id

    def __hash__(self):
        return hash(self.machine_id)