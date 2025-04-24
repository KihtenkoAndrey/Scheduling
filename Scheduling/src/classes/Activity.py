from collections import defaultdict

# Активности
class Activity:
    def __init__(self, act_id, volume, type, direction=None, name=None):
        self.act_id = act_id
        self.volume = volume
        self.type = type
        self.direction = direction
        self.name = name
        self.label = f"{self.type}_{act_id}" 
        self.MACHINES = []  # Список машин с производительностями
        self.INTERVALS = [] # Список интервалов
        

    def add_machine(self, machine):
        self.MACHINES.append(machine)
        
    def add_interval(self, interval):
        self.INTERVALS.append(interval)
        
        
    def fill_intervals_by_number(self):
        self.interval_by_num = defaultdict(int, {interval.number: interval for interval in self.INTERVALS})

    def __repr__(self):
        return (f"ACTIVITY(act_id={self.act_id}, name={self.name}, "
                f"volume={self.volume}, type={self.type}, "
                f"direction={self.direction},"
                f"MACHINES={str(self.MACHINES)}")
    
    def __eq__(self, other):
        return self.act_id == other.act_id and self.type == other.type

    def __hash__(self):
        return hash((self.act_id, self.type))