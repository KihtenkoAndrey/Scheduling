from src.config import ModelConfig
from src.classes import Activity
from src.classes import Machine
from src.classes import Interval

import math

class ModelInput:
    def __init__(
            self,
            model_config: ModelConfig
    ):
        print('Подготовка входных данных модели')
        self.config: ModelConfig = model_config
            
        self.generate_data()
        
        self.calc_interval()
        self.generate_assignments()
        self.calc_params()
        
        
    # Генерация данных
    def generate_data(self):
        self.ACTIVITIES = []
        for i in range(self.config.act_amt):
            self.ACTIVITIES.append(Activity(i, 1000, 'Бурение'))

        self.MACHINES = []
        for i in range(self.config.machine_amt):
            self.MACHINES.append(Machine(i, 100 + 50*i))
        
        for i, act in enumerate(self.ACTIVITIES):
            for j, machine in enumerate(self.MACHINES):
                # if i % 2 == 0 and machine.machine_id % 2 == 0:
                #     act.add_machine(machine)
                # elif i % 2 != 0 and machine.machine_id % 2 != 0:
                #     act.add_machine(machine)
                # else:
                #     pass
                if i!= 4 and i == j:
                    act.add_machine(machine)
                    machine.add_activity(act)
                if i == 4 and j == 5:
                    act.add_machine(machine)
                    machine.add_activity(act)
                if i == 3 and j == 8:
                    act.add_machine(machine)
                    machine.add_activity(act)
        
                
    # Расчет максимального времени выполнения активности
    def calc_interval(self):
        for act in self.ACTIVITIES:
            # Считаем, что производительность задана в одинаковых приведенных единицах
            act.min_power = min(machine.power for machine in act.MACHINES)
            act.max_duration = math.ceil(act.volume / act.min_power)

        self.max_date = self.config.start_date + sum(act.max_duration for act in self.ACTIVITIES)
        
        for act in self.ACTIVITIES:
        # act.INTERVALS = [Interval(num, num+1, 1, num) for num in range(self.config.start_date, self.max_date+1)]
            for num in range(self.config.start_date, self.max_date+1):
                interval = Interval(num, num+1, 1, num)
                act.add_interval(interval)
                for machine in act.MACHINES:
                    machine.add_interval(interval)
                # act.fill_intervals_by_number()

        
    
            
                
    # Назначения машин на активности в интервал времени
    def generate_assignments(self):
        self.ASSIGNMENTS = [(act, machine, interval)
                            for act in self.ACTIVITIES
                            for machine in act.MACHINES
                            for interval in act.INTERVALS]
        
    
    # Расчет необходимых показателей для оптимизации
    def calc_params(self):
        
        # Суммарный объем по всем активностям
        self.sum_volume = sum(act.volume for act in self.ACTIVITIES)
        
        # Объединение интервалов
        # self.ALL_INTERVALS = list(set())
        

        
        
        

                    
                    