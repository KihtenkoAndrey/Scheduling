from src.classes import Activity
from src.classes import Machine
from src.classes import Interval
from src import ModelConfig
from src import Model
from src import ModelInput
from src import ModelOutput




input = ModelInput(ModelConfig)
model = Model(input)
model.solve_model()
# output = ModelOutput(model, input)
# output.create_output()
model.output.transform_results()
model.output.create_output()
model.output.plot_gantt()
model.output.print_input()
# model.output.result_assignments_df.head()