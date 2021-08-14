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
    for i in range(self.parsed.depth+1):
      self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in self.predicate_variables[i]) + ')'])

  def generate_black_transition(self, time_step):
    self.encoding.append(['# Player 1 (black) transition function for time step ' + str(time_step)+ ': '])
    # Time variable less than constraint t < time_step + 1:
    self.encoding.append(['# Less than constraint for time :'])
    lsc.add_circuit(self.gates_generator, self.time_variables, time_step + 1)
    time_output_gate = self.gates_generator.output_gate

    # Move equality constraint with position variables:
    self.encoding.append(['# Equality gate for move and forall positional variables:'])
    self.gates_generator.complete_equality_gate(self.move_variables[time_step], self.forall_position_variables)
    equality_output_gate = self.gates_generator.output_gate

    # conjuction for time and equality constraint:
    self.encoding.append(['# Conjuction for time and equality constraints:'])
    self.gates_generator.and_gate([time_output_gate,equality_output_gate])
    conditional_and_output_gate = self.gates_generator.output_gate

    # constraints choosing black position:
    self.encoding.append(['# Choosing black position constraints:'])
    self.encoding.append(['# In time step i, occupied must be false:'])
    self.encoding.append(['# In time step i+1, occupied must be true and color must be black (i.e., 0):'])
    self.gates_generator.and_gate([-self.predicate_variables[time_step][0], self.predicate_variables[time_step + 1][0], -self.predicate_variables[time_step + 1][1]])

    # Now if condition:
    self.encoding.append(['# If time and equality constraints hold then choosing black constraints must be true:'])
    self.gates_generator.if_then_gate(conditional_and_output_gate, self.gates_generator.output_gate)
    self.transition_step_output_gates.append(self.gates_generator.output_gate)

    # Finally propogation constraints:
    self.encoding.append(['# propagation constraints:'])
    self.gates_generator.complete_equality_gate(self.predicate_variables[time_step], self.predicate_variables[time_step+1])
    self.encoding.append(['# If the time and equality constraints does not hold predicates are propagated:'])
    self.gates_generator.or_gate([conditional_and_output_gate, self.gates_generator.output_gate])
    self.transition_step_output_gates.append(self.gates_generator.output_gate)


  def generate_white_transition(self, time_step):
    self.encoding.append(['# Player 2 (white) transition function for time step ' + str(time_step)+ ': '])
    # Time variable less than constraint t < time_step + 1:
    self.encoding.append(['# Less than constraint for time :'])
    lsc.add_circuit(self.gates_generator, self.time_variables, time_step + 1)
    time_output_gate = self.gates_generator.output_gate

    # Move equality constraint with position variables:
    self.encoding.append(['# Equality gate for move and forall positional variables:'])
    self.gates_generator.complete_equality_gate(self.move_variables[time_step], self.forall_position_variables)
    equality_output_gate = self.gates_generator.output_gate

    # conjuction for time and equality constraint:
    self.encoding.append(['# Conjuction for time and equality constraints:'])
    self.gates_generator.and_gate([time_output_gate,equality_output_gate])
    conditional_and_output_gate = self.gates_generator.output_gate

    # constraints choosing black position:
    self.encoding.append(['# Choosing white position constraints:'])
    self.encoding.append(['# In time step i, occupied must be false:'])
    self.encoding.append(['# In time step i+1, occupied must be true and color must be white (i.e., 1):'])
    self.gates_generator.and_gate([-self.predicate_variables[time_step][0], self.predicate_variables[time_step + 1][0], self.predicate_variables[time_step + 1][1]])

    # Now if condition:
    self.encoding.append(['# If time and equality constraints hold then choosing white constraints must be true:'])
    self.gates_generator.if_then_gate(conditional_and_output_gate, self.gates_generator.output_gate)
    self.transition_step_output_gates.append(self.gates_generator.output_gate)

    # Finally propogation constraints:
    self.encoding.append(['# propagation constraints:'])
    self.gates_generator.complete_equality_gate(self.predicate_variables[time_step], self.predicate_variables[time_step+1])
    self.encoding.append(['# If the time and equality constraints does not hold predicates are propagated:'])
    self.gates_generator.or_gate([conditional_and_output_gate, self.gates_generator.output_gate])
    self.transition_step_output_gates.append(self.gates_generator.output_gate)

  def generate_d_transitions(self):
    self.encoding.append(["# ------------------------------------------------------------------------"])
    self.encoding.append(['# Transitions: '])
    for i in range(self.parsed.depth):
      if (i%2 == 0):
        self.generate_black_transition(i)
      else:
        self.generate_white_transition(i)



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
    for i in range(parsed.depth+1):
      self.predicate_variables.append(self.encoding_variables.get_vars(2))

    if (parsed.args.debug == 1):
      print("Predicate variables: ",self.predicate_variables)

    # Allocating goal state variables:
    self.goal_state_variables = self.encoding_variables.get_vars(parsed.num_positions)

    if (parsed.args.debug == 1):
      print("Goal state variables: ",self.goal_state_variables)


    # Generating quantifer blocks:
    self.generate_quantifier_blocks()

    self.gates_generator = ggen(self.encoding_variables, self.encoding)

    # Generating d steps i.e., which includes black and white constraints:
    self.generate_d_transitions()

    print(self.transition_step_output_gates)

    self.generate_initial_gate()

    self.generate_goal_gate()

    self.generate_final_gate()
