# from pyomo.environ import Var, Binary, Objective, quicksum, minimize, SolverFactory, ConcreteModel
# from pyomo.core import value
from pyomo.environ import *
import pyomo.environ as pyo

from src.classes import Activity
from src.classes import Machine
from src.classes import Interval
from src import ModelConfig
from src import ModelInput
from src import ModelOutput
from src.utils import constraints_from_dict

class Model:
    def __init__(self, input: ModelInput) -> None:
        self.model = ConcreteModel()
        self.input = input

        self.output = ModelOutput(
            self.model,
            self.input,
        )

        self.create_model()

    def create_model(self):
        print('Подготовка модели')

        ## Переменные
        # Доля и индикатор назначения машины на активность в интервал t
        self.model.assignment = Var(self.input.ASSIGNMENTS, domain=NonNegativeReals, bounds=(0, 1), initialize=0)
        self.model.assignment_bin = Var(self.input.ASSIGNMENTS, domain=Binary, initialize=0)
        
        
        # Отклонение машины на другую активность
        machine_diff_index = [(act, machine, interval) for machine in self.input.MACHINES
                                      for interval in machine.INTERVALS
                                      for act in machine.ACTIVITIES
                                      if len(machine.ACTIVITIES) >= 2]
        self.model.machine_diff = Var(machine_diff_index, domain=NonNegativeReals, bounds=(0, 1), initialize=0)

        
        # Накопленный невыполненный объем в интервал t
        self.model.running_undone_volume = dict()
        for act in self.input.ACTIVITIES:
            # Сохраняем пройденные интервалы для ускорения расчета
            PREV_INTERVALS = list()
            for interval in act.INTERVALS:
                PREV_INTERVALS.append(interval)
                
                self.model.running_undone_volume[act, interval] = 1 - \
                quicksum(
                self.model.assignment[act, machine, prev_interval] * machine.power * interval.duration
                    for machine in act.MACHINES
                    for prev_interval in PREV_INTERVALS 
                ) / act.volume
                

        ## Ограничения

        # Выполнение всего объема активностей
        cons_act_volume = {}
        for act in self.input.ACTIVITIES:
            cons_act_volume[act] = (
                quicksum(
                    self.model.assignment[act, machine, interval] * machine.power * interval.duration
                    for machine in act.MACHINES
                    for interval in act.INTERVALS 
                )
                ==
                act.volume
            )
            
        constraints_from_dict(cons_act_volume, self.model, 'cons_act_volume')
        
        # В каждый момент времени на активность назначается только одна машина
        cons_one_machine_for_act_t = {}
        for act in self.input.ACTIVITIES:
            for interval in act.INTERVALS:
                cons_one_machine_for_act_t[act, interval] = (
                quicksum(
                    self.model.assignment[act, machine, interval]
                    for machine in act.MACHINES
                )
                <= 1)
        
        constraints_from_dict(cons_one_machine_for_act_t, self.model, 'cons_one_machine_for_act_t')
        
        # В каждый момент времени машина назначается только на одну активность
        cons_one_act_for_machine_t = {}
        for machine in self.input.MACHINES:
#             for interval in sorted(list(machine.INTERVALS), key=lambda interval: interval.start): 
            for interval in machine.INTERVALS:
                cons_one_act_for_machine_t[machine, interval] = (
                quicksum(
                    self.model.assignment[act, machine, interval]
                    for act in machine.ACTIVITIES)
                <= 1)
                
        constraints_from_dict(cons_one_act_for_machine_t, self.model, 'cons_one_act_for_machine_t')
        
        # Отклонение машины на другую активность
        cons_abs_deviation_machine = {}
        for machine in self.input.MACHINES:
            if len(machine.ACTIVITIES) >= 2:
                prev_interval = Interval(-1, -1, -1, -1)
                for interval in sorted(list(machine.INTERVALS), key=lambda interval: interval.start):
                    if prev_interval != Interval(-1, -1, -1, -1):
                        for act in machine.ACTIVITIES:
                            cons_abs_deviation_machine[act,machine,interval,1] = (
                                self.model.machine_diff[act,machine,interval] >= 
                                self.model.assignment_bin[act, machine, interval] - 
                                self.model.assignment_bin[act, machine, prev_interval]
                            )
                            
                            cons_abs_deviation_machine[act,machine,interval,2] = (
                                self.model.machine_diff[act,machine,interval] >= 
                                self.model.assignment_bin[act, machine, prev_interval] - 
                                self.model.assignment_bin[act, machine, interval]
                            )
                    prev_interval = interval
                    
        constraints_from_dict(cons_abs_deviation_machine, self.model, 'cons_abs_deviation_machine')
                    
        # cons_abs_deviation_machine = {}
        # for machine in self.input.MACHINES:
        #     if len(machine.ACTIVITIES) >= 2:
        #         for interval in sorted(list(machine.INTERVALS), key=lambda interval: interval.start):
        #             for act in machine.ACTIVITIES:
        #                 cons_abs_deviation_machine[act,machine,interval,1] = (
        #                     self.model.machine_diff[act,machine,interval] >= 
        #                     self.model.assignment[act, machine, interval] - 
        #                     0.5
        #                 )

        #                 cons_abs_deviation_machine[act,machine,interval,2] = (
        #                     self.model.machine_diff[act,machine,interval] >= 
        #                     0.5 - 
        #                     self.model.assignment[act, machine, interval]
        #                 )
        #         prev_interval = interval
                
        # constraints_from_dict(cons_abs_deviation_machine, self.model, 'cons_abs_deviation_machine')


        # Связь бинарных и вещественных переменных
        cons_assign_reals_bin_conn = {}
        for act,machine,interval in self.input.ASSIGNMENTS:
            if len(act.MACHINES) >= 2:
                cons_assign_reals_bin_conn[act,machine,interval,1] = (
                    self.model.assignment[act,machine,interval] 
                        <= 
                    self.model.assignment_bin[act, machine, interval])

                cons_assign_reals_bin_conn[act,machine,interval,2] = (
                    self.model.assignment[act,machine,interval] 
                        >= 
                    self.model.assignment_bin[act, machine, interval] * 5e-5)
                
        constraints_from_dict(cons_assign_reals_bin_conn, self.model, 'cons_assign_reals_bin_conn')
            
        


        ### Целевая функция 
        # Выполнение работ как можно раньше
        expr1 = quicksum(self.model.running_undone_volume[act, interval]
                        for act,interval in self.model.running_undone_volume.keys())
        
        # Минимизация переездов машин между активностями
        expr2 = quicksum(self.model.machine_diff[act,machine,interval]
                        for act,machine,interval in machine_diff_index)

        # Минимизация бинарных переменных
        expr3 = quicksum(self.model.assignment_bin[act,machine,interval]
                        for act,machine,interval in self.input.ASSIGNMENTS)

        # Минимизация времени выполнения работ
        self.model.obj = Objective(
            expr=(
                expr1 + expr2
                
            #  expr=(quicksum(
            #         self.model.assignment[act, machine, interval] * interval.number
            #             for act in self.input.ACTIVITIES 
            #             for machine in act.MACHINES
            #             for interval in act.INTERVALS
            #     )
                
            )
            , sense=minimize
        )

        return

    def solve_model(self):
        print('Запуск оптимизации')

        # Solver = SolverFactory('cbc')

        # Solver.options['Threads' ] = 10
        # Solver.options['second' ] = 1800
        # Solver.options['allowableGap' ] = 0.02

        #solver = SolverFactory('appsi_highs')
        #solver.options['time_limit'] = 900
        #solver.options['mip_rel_gap'] = 0.02

        solver_name = 'appsi_highs'
        solver = SolverFactory(solver_name)
        # self.model.write('1.lp', io_options={'symbolic_solver_labels': True})
        if solver_name == 'appsi_highs':
            solver.options['time_limit'] = 3600
            solver.options['mip_rel_gap'] = 1e-5
            SolverResults = solver.solve(self.model, tee=True)
        else:
            solver.options['TimeLimit'] = 3600
            solver.options['Method'] = 3
            SolverResults = solver.solve(self.model, tee=True, warmstart=True)
            
            
        # Обработка статусов    
        if (SolverResults.solver.termination_condition == TerminationCondition.infeasible 
            or SolverResults.solver.termination_condition == TerminationCondition.infeasibleOrUnbounded 
            # or SolverResults.solver.termination_condition == TerminationCondition.aborted
            ):
            ResultStatus = 'Infeasible'

            # sys.exit("\n\n #opti-model-status NOT_FOUND \n\n")
        else:
            ResultStatus = 'OK'

        return       

   