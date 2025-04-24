from pyomo.environ import Var, Binary, Objective, quicksum, minimize, SolverFactory, ConcreteModel
from pyomo.core import value
import random
from sympy import Union
from sympy import Interval as SympyInterval
import pandas as pd
from collections import defaultdict

from src.classes import Activity
from src.classes import Machine
from src.classes import Interval
from src import ModelConfig
from src import Model
from src import ModelInput

class ModelOutput:
    def __init__(self, model: ConcreteModel, input: ModelInput):
        self.model = model
        self.input = input

        self.result_assignments_df = pd.DataFrame(
            columns=[
                'act',
                'machine',
                'Start',
                'Finish'
            ]
        )
        
        
    def transform_results(self):
        
        self.ROUNDING_CONST = 1e-4
        assignment_result = defaultdict(int, {(act,machine,interval): round(value(self.model.assignment[act,machine,interval]), 3)
                            for act,machine,interval in self.input.ASSIGNMENTS})
        
        # Соединение в крупные интервалы
        self.RESULT_GANTT = list()
        for act in self.input.ACTIVITIES:
            for machine in act.MACHINES:
                prev_interval = Interval(1,1,0,1)
                full_interval_flg = defaultdict(int)
                INTERVALS = list()
                for interval in act.INTERVALS:
                    if assignment_result[act,machine,interval] > 1 - self.ROUNDING_CONST:
                        full_interval_flg[act,machine,interval] = 1

                    if assignment_result[act,machine,interval] > self.ROUNDING_CONST:
                        if full_interval_flg[act,machine,prev_interval] == 1:
                            start = interval.start
                            end = interval.start + interval.duration*assignment_result[act,machine,interval]
                        else:
                            start = interval.end - interval.duration*assignment_result[act,machine,interval]
                            end = interval.end
                        INTERVALS.append(SympyInterval(start,end))
                    prev_interval = interval
                        
                        
                # intervals = [SympyInterval(interval.start, interval.start+interval.duration*assignment_result[act,machine,interval]) 
                #              for interval in act.INTERVALS
                #              if assignment_result[act,machine,interval] > ROUNDING_CONST]
                INTERVALS.append(SympyInterval(0,0))
                u = Union(*INTERVALS)
                for subset in u.args:
                    if subset.measure > 0:
                        self.RESULT_GANTT.append((act,machine,Interval(float(subset.start), float(subset.end))))
        # self.RESULT_GANTT = list()
        # for act in self.input.ACTIVITIES:
        #     for machine in act.MACHINES:
        #         intervals = [SympyInterval(interval.start, interval.end) for interval in act.INTERVALS
        #                 if assignment_result[act,machine,interval] > 1e-4]
        #         u = Union(*intervals)
        #         if act.label == 'Бурение_1' and machine.label == 'Машина_1':
        #             print(u)
        #             sys.exit()
        #         start_interval, prev_interval = Interval(1,1,0,1), Interval(1,1,0,1)
        #         for interval in act.INTERVALS:
        #             if assignment_result[act,machine,interval] > 1e-4:
        #                 if interval.number - prev_interval.number > 1:
        #                     end = prev_interval.start + prev_interval.duration * assignment_result[act,machine,prev_interval]
        #                     self.RESULT_GANTT.append((act,machine,Interval(start_interval.start, end)))
        #                     start_interval = interval
        #                 prev_interval = interval
                            
                
        #         end = prev_interval.start + prev_interval.duration * assignment_result[act,machine,prev_interval]
        #         self.RESULT_GANTT.append((act,machine,Interval(start_interval.start, end)))
            
                
        
        # Детальный аутпут
        assignment_result = [[act.label, machine.label, interval.start, interval.end, value(self.model.assignment[act,machine,interval])]
                                      for act in self.input.ACTIVITIES
                                      for machine in act.MACHINES
                                      for interval in act.INTERVALS
                                  if value(self.model.assignment[act,machine,interval]) > self.ROUNDING_CONST]
        self.result_detailed_df = pd.DataFrame(
            columns=[
                'act',
                'machine',
                'Start',
                'End',
                'Frac'
            ])
            
        self.result_detailed_df = pd.DataFrame(assignment_result, columns=self.result_detailed_df.columns)
        
                                            
                            
        

    def create_output(self):
        print('Подготовка выходных данных')
        
                            

        result_assignments = [
            [
                act.label,
                machine.label,
                interval.start,
                interval.end

            ]
            for act,machine,interval in self.RESULT_GANTT
        ]
        self.result_assignments_df = pd.DataFrame(result_assignments, columns=self.result_assignments_df.columns)
        
        # self.result_jobs_df = self.result_assignments_df.groupby(['act', 'machine']).agg(
        #     Start=pd.NamedAgg(column="interval", aggfunc="min"),
        #     Finish=pd.NamedAgg(column="interval", aggfunc="max")
        #     ).reset_index()
        # self.result_jobs_df = self.result_assignments_df.copy()
        
    def plot_gantt(self):
        df = self.result_assignments_df.copy()
        df['Task'] = df['act'] + ' ' + df['machine'].astype(str)
        df['Complete'] = 100

        colors = dict()
        random.seed(42)
        for i, act in enumerate(self.input.ACTIVITIES):
            colors[act.label] = f"rgb({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)})"
            
        fig = ff.create_gantt(df, colors=colors, index_col='act', show_colorbar=True)
        fig.update_layout(xaxis_type='linear')
        # fig.show()
        
    
    def print_input(self):
        print('Активности:')
        for act in self.input.ACTIVITIES:
            print(f"{act.label}: {act.volume}")
            print(f"{[f'{machine.label}: {machine.power}'for machine in act.MACHINES]}\n")
            
        # print('\nМашины:')
        # for machine in self.input.MACHINES:
        #     print(f"{machine.label}: {machine.power}")


        