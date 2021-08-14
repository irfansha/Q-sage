# Irfansha Shaik, 14.08.2021, Aarhus.

from utils.variables_dispatcher import VarDispatcher as vd
from utils.gates import GatesGen as ggen
import math
import utils.lessthen_cir as lsc



class GroundedGoalEncoding:

  def print_gate_tofile(self, gate, f):
    if len(gate) == 1:
      f.write(gate[0] + '\n')
    else:
      f.write(str(gate[1]) + ' = ' + gate[0] + '(' + ', '.join(str(x) for x in gate[2]) + ')\n')

  def print_encoding_tofile(self, file_path):
    f = open(file_path, 'w')
    for gate in self.quantifier_block:
      self.print_gate_tofile(gate, f)
    f.write('output(' + str(self.final_output_gate) + ')\n')
    for gate in self.encoding:
      self.print_gate_tofile(gate, f)

  # Generates quanifier blocks:
  def generate_quantifier_blocks(self):
    # Time variables in outer most layer:
    self.quantifier_block.append(['# Time variables: '])
    self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in self.time_variables) + ')'])

    # Move variables following time variables:
    self.quantifier_block.append(['# Move variables: '])
    for i in range(self.parsed.depth):
      # starts with 0 and even is black (i.e., existential moves):
      if (i % 2 == 0):
        self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in self.move_variables[i]) + ')'])
      else:
        self.quantifier_block.append(['forall(' + ', '.join(str(x) for x in self.move_variables[i]) + ')'])

    # Grounded goal variables before forall position variables:
    self.quantifier_block.append(['# Grounded goal variables: '])
    self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in self.goal_state_variables) + ')'])

    # Forall position variables:
    self.quantifier_block.append(['# Forall position variables: '])
    self.quantifier_block.append(['forall(' + ', '.join(str(x) for x in self.forall_position_variables) + ')'])

    # Finally predicate variables for each time step:
    self.quantifier_block.append(['# Predicate variables: '])
    for i in range(self.parsed.depth):
      self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in self.predicate_variables[i]) + ')'])

  def generate_k_transitions(self):
    self.encoding.append(["# ------------------------------------------------------------------------"])
    self.encoding.append(['# Transitions: '])


  # TODO: Testing is needed
  def generate_initial_gate(self):
    initial_step_output_gates = []

    self.encoding.append(["# ------------------------------------------------------------------------"])
    self.encoding.append(['# Initial state: '])


  # Generating goal constraints:
  def generate_goal_gate(self):
    goal_step_output_gates = []
    self.encoding.append(["# ------------------------------------------------------------------------"])
    self.encoding.append(['# Goal state: '])


  def generate_simple_restricted_forall_constraints(self):

    self.encoding.append(["# ------------------------------------------------------------------------"])
    self.encoding.append(['# Conditional forall constraints: '])



  # Final output gate is an and-gate with inital, goal and transition gates:
  def generate_final_gate(self):
    self.encoding.append(["# ------------------------------------------------------------------------"])
    self.encoding.append(['# Final gate: '])

  def __init__(self, parsed):
    self.parsed = parsed
    self.encoding_variables = vd()
    self.quantifier_block = []
    self.encoding = []
    self.initial_output_gate = 0 # initial output gate can never be 0
    self.goal_output_gate = 0 # goal output gate can never be 0
    self.transition_step_output_gates = []
    self.conditional_final_output_gate = 0 # Can never be 0
    self.final_output_gate = 0 # Can never be 0



    # Allocating time variables first:
    self.time_num_variables = math.ceil(math.log2(parsed.depth))
    self.time_variables = self.encoding_variables.get_vars(self.time_num_variables)
    if (parsed.args.debug == 1):
      print("------------------------------------------------------------")
      print("Number of (log) time variables: ", self.time_num_variables)
      print("Time variables: ",self.time_variables)

    # Allocating action variables for each time step until depth,
    # Moves are same as the vertexs/positions on the board:
    self.num_move_variables = math.ceil(math.log2(parsed.num_positions))
    self.move_variables = []
    for i in range(parsed.depth):
      self.move_variables.append(self.encoding_variables.get_vars(self.num_move_variables))

    if (parsed.args.debug == 1):
      print("Number of (log) move variables: ", self.num_move_variables)
      print("Move variables: ",self.move_variables)

    # Allocating forall position variables:
    self.forall_position_variables = self.encoding_variables.get_vars(self.num_move_variables)

    if (parsed.args.debug == 1):
      print("Forall position variables: ",self.forall_position_variables)

    # Allocating predicate variables, two variables are used one is occupied and
    # other color (but implicitly) for each time step:
    self.predicate_variables = []
    for i in range(parsed.depth):
      self.predicate_variables.append(self.encoding_variables.get_vars(2))

    if (parsed.args.debug == 1):
      print("Predicate variables: ",self.predicate_variables)

    # Allocating goal state variables:
    self.goal_state_variables = self.encoding_variables.get_vars(parsed.num_positions)

    if (parsed.args.debug == 1):
      print("Goal state variables: ",self.goal_state_variables)


    # Generating quantifer blocks:
    self.generate_quantifier_blocks()
    # Generating k steps i.e., plan length number of transitions:
    self.generate_k_transitions()

    self.gates_generator = ggen(self.encoding_variables, self.encoding)

    self.generate_initial_gate()

    self.generate_goal_gate()

    self.generate_final_gate()
