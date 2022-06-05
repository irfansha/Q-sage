# Irfansha Shaik, 04.06.2022, Aarhus.

import math

import utils.adder_cir as addc
import utils.lessthen_cir as lsc
from utils.gates import GatesGen as ggen
from utils.variables_dispatcher import VarDispatcher as vd


class IndexBasedGeneral:

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

  # Takes a list of clause variables and maps to a integer value:
  def generate_binary_format(self, clause_variables, corresponding_number):
    num_variables = len(clause_variables)
    # Representation in binary requires number of variables:
    rep_string = '0' + str(num_variables) + 'b'
    bin_string = format(corresponding_number, rep_string)
    cur_variable_list = []
    # Depending on the binary string we set action variables to '+' or '-':
    for j in range(num_variables):
      if (bin_string[j] == '0'):
        cur_variable_list.append(-clause_variables[j])
      else:
        cur_variable_list.append(clause_variables[j])
    return cur_variable_list

  # Generates quanifier blocks:
  def generate_quantifier_blocks(self):

    # Move variables following time variables:
    if (self.makermaker_game == 1):
      self.quantifier_block.append(['# ' + str(self.num_black_action_variables) + '/' + str(self.num_white_action_variables) + ' (black/white) Action variables, ' + str(self.num_x_index_variables) + ' and ' + str(self.num_y_index_variables) +  ' (action parameter) index variables (x, y), and game stop variables : '])
    else:
      self.quantifier_block.append(['# ' + str(self.num_black_action_variables) + '/' + str(self.num_white_action_variables) + ' (black/white) Action variables, ' + str(self.num_x_index_variables) + ' and ' + str(self.num_y_index_variables) +  ' (action parameter) index variables (x, y): '])
    for i in range(self.parsed.depth):
      # starts with 0 and even is black (i.e., existential moves):
      cur_all_action_vars = []
      # adding action variables:
      cur_all_action_vars.extend(self.move_variables[i][0])
      # adding parameter variables:
      cur_all_action_vars.extend(self.move_variables[i][1])
      cur_all_action_vars.extend(self.move_variables[i][2])
      # adding game stop variable if present:
      cur_all_action_vars.extend(self.move_variables[i][3])
      if (i % 2 == 0):
        self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in cur_all_action_vars) + ')'])
      else:
        self.quantifier_block.append(['forall(' + ', '.join(str(x) for x in cur_all_action_vars) + ')'])

    # black goal variables:
    self.quantifier_block.append(['# black goal index variables: '])
    all_black_goal_vars = []
    all_black_goal_vars.extend(self.black_goal_index_variables[0])
    all_black_goal_vars.extend(self.black_goal_index_variables[1])
    self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in all_black_goal_vars) + ')'])

    # if maker-maker, white illegal variable before universal variables:
    if (self.makermaker_game == 1):
      self.quantifier_block.append(['# white illegal variable: '])
      self.quantifier_block.append(['exists(' + str(self.white_illegal) + ')'])

    # Forall position variables:
    self.quantifier_block.append(['# Forall index variables: '])
    forall_index_variables = []
    forall_index_variables.extend(self.forall_position_variables[0])
    forall_index_variables.extend(self.forall_position_variables[1])
    self.quantifier_block.append(['forall(' + ', '.join(str(x) for x in forall_index_variables) + ')'])

    # Finally predicate variables for each time step:
    self.quantifier_block.append(['# Predicate variables: '])
    for i in range(self.parsed.depth+1):
      self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in self.predicate_variables[i]) + ')'])

  def generate_black_transition(self, time_step):
    self.encoding.append(['# Player 1 (black) transition function for time step ' + str(time_step)+ ': '])

    # Move equality constraint with position variables:
    self.encoding.append(['# Equality gate for move and forall positional variables:'])
    self.gates_generator.complete_equality_gate(self.move_variables[time_step], self.forall_position_variables)
    #equality_output_gate = self.gates_generator.output_gate
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

    # Move equality constraint with position variables:
    self.encoding.append(['# Equality gate for move and forall positional variables:'])
    self.gates_generator.complete_equality_gate(self.move_variables[time_step], self.forall_position_variables)
    equality_output_gate = self.gates_generator.output_gate
    self.encoding.append(['# In time step i, occupied must be false:'])
    self.gates_generator.and_gate([equality_output_gate, -self.predicate_variables[time_step][0] ])

    conditional_and_output_gate = self.gates_generator.output_gate

    # constraints choosing white position:
    self.encoding.append(['# Choosing white position constraints:'])
    self.encoding.append(['# In time step i+1, occupied must be true and color must be white (i.e., 1):'])
    self.gates_generator.and_gate([self.predicate_variables[time_step + 1][0], self.predicate_variables[time_step + 1][1]])

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


    self.encoding.append(['# Final transition gate: '])
    self.gates_generator.and_gate(self.transition_step_output_gates)
    self.transition_output_gate = self.gates_generator.output_gate


  def generate_initial_gate(self):
    initial_step_output_gates = []

    self.encoding.append(["# ------------------------------------------------------------------------"])
    self.encoding.append(['# Initial state: '])

    # Constraints in forall branches for black positions:
    black_position_output_gates = []

    for position in self.parsed.black_initial_positions:
      # generating binary format for indexes separately:
      binary_format_clause1 = self.generate_binary_format(self.forall_position_variables[:self.num_single_index_move_variables],position[0])
      self.gates_generator.and_gate(binary_format_clause1)
      binary_output_gate1 = self.gates_generator.output_gate
      binary_format_clause2 = self.generate_binary_format(self.forall_position_variables[self.num_single_index_move_variables:],position[1])
      self.gates_generator.and_gate(binary_format_clause2)
      binary_output_gate2 = self.gates_generator.output_gate
      self.gates_generator.and_gate([binary_output_gate1,binary_output_gate2])
      black_position_output_gates.append(self.gates_generator.output_gate)


    self.encoding.append(['# Or for all black forall position clauses: '])
    self.gates_generator.or_gate(black_position_output_gates)

    black_final_output_gate = self.gates_generator.output_gate

    self.encoding.append(['# if black condition is true then first time step occupied and color black (i.e. 0): '])
    self.gates_generator.and_gate([self.predicate_variables[0][0], -self.predicate_variables[0][1]])
    self.gates_generator.if_then_gate(black_final_output_gate, self.gates_generator.output_gate)

    initial_step_output_gates.append(self.gates_generator.output_gate)

    # Constraints in forall branches for white positions:
    white_position_output_gates = []

    for position in self.parsed.white_initial_positions:
      # generating binary format for indexes separately:
      binary_format_clause1 = self.generate_binary_format(self.forall_position_variables[:self.num_single_index_move_variables],position[0])
      self.gates_generator.and_gate(binary_format_clause1)
      binary_output_gate1 = self.gates_generator.output_gate
      binary_format_clause2 = self.generate_binary_format(self.forall_position_variables[self.num_single_index_move_variables:],position[1])
      self.gates_generator.and_gate(binary_format_clause2)
      binary_output_gate2 = self.gates_generator.output_gate
      self.gates_generator.and_gate([binary_output_gate1,binary_output_gate2])
      white_position_output_gates.append(self.gates_generator.output_gate)

    self.encoding.append(['# Or for all white forall position clauses: '])
    self.gates_generator.or_gate(white_position_output_gates)

    white_final_output_gate = self.gates_generator.output_gate

    self.encoding.append(['# if white condition is true then first time step occupied and color white (i.e. 1): '])
    self.gates_generator.and_gate([self.predicate_variables[0][0], self.predicate_variables[0][1]])
    self.gates_generator.if_then_gate(white_final_output_gate, self.gates_generator.output_gate)

    initial_step_output_gates.append(self.gates_generator.output_gate)

    # Finally for all other forall branches, the position is unoccupied:
    self.encoding.append(['# for all other branches the occupied is 0: '])
    self.gates_generator.or_gate([black_final_output_gate, white_final_output_gate])
    self.gates_generator.or_gate([self.gates_generator.output_gate, -self.predicate_variables[0][0]])

    initial_step_output_gates.append(self.gates_generator.output_gate)

    # Now final output gate for the initial state:
    self.gates_generator.and_gate(initial_step_output_gates)
    self.initial_output_gate = self.gates_generator.output_gate


  # Generating goal constraints:
  def generate_goal_gate(self):
    goal_step_output_gates = []
    self.encoding.append(["# ------------------------------------------------------------------------"])
    self.encoding.append(['# Goal state: '])
    self.encoding.append(["# ------------------------------------------------------------------------"])


  # Final output gate is an and-gate with inital, goal and transition gates:
  def generate_final_gate(self):
    self.encoding.append(["# ------------------------------------------------------------------------"])
    self.encoding.append(['# Final gate: '])

    self.encoding.append(['# Conjunction of Initial gate and Transition gate and Goal gate: '])
    self.gates_generator.and_gate([self.initial_output_gate, self.transition_output_gate, self.goal_output_gate])
    self.final_output_gate = self.gates_generator.output_gate


  def __init__(self, parsed):
    self.parsed = parsed
    self.encoding_variables = vd()
    self.quantifier_block = []
    self.encoding = []
    self.initial_output_gate = 0 # initial output gate can never be 0
    self.goal_output_gate = 0 # goal output gate can never be 0
    self.transition_step_output_gates = []
    self.transition_output_gate = 0 # Can never be 0
    self.final_output_gate = 0 # Can never be 0


    # We generate game stop variables and white illegal variable only for maker-maker games, otherwise no need,
    # remembering which type of game:
    if (len(parsed.white_goal_constraints) == 1 and len(parsed.white_goal_constraints[0]) == 0):
      self.makermaker_game = 0
    else:
      self.makermaker_game = 1


    # Allocating action variables for each time step until depth:
    # for general board the board can be rectangular, allocating for both indexes separately:
    self.num_x_index_variables = int(math.ceil(math.log2(parsed.xmax)))
    self.num_y_index_variables = int(math.ceil(math.log2(parsed.ymax)))
    self.xmax = parsed.xmax
    self.ymax = parsed.ymax
    # number of black actions:
    self.num_black_actions = len(self.parsed.black_action_list)
    # we need logarithmic number of variables to represent them:
    self.num_black_action_variables = int(math.ceil(math.log2(self.num_black_actions)))
    # number of white actions:
    self.num_white_actions = len(self.parsed.white_action_list)
    # we need logarithmic number of variables to represent them:
    self.num_white_action_variables = int(math.ceil(math.log2(self.num_white_actions)))


    self.move_variables = []
    for i in range(parsed.depth):
      temp_list = []
      # for black we use the black log action variables:
      if (i%2 == 0):
        # we only generate new action variables if there are more than 1 actions, no need for extra variables if only one action:
        if (self.num_black_actions > 1):
          temp_list.append(self.encoding_variables.get_vars(self.num_black_action_variables))
        else:
          # else appending an empty list, for preserving structure of the list of lists:
          temp_list.append([])
      else:
        # same as black actions, we only generate new action variables if there are more than 1 actions, no need for extra variables if only one action:
        if (self.num_white_actions > 1):
          temp_list.append(self.encoding_variables.get_vars(self.num_white_action_variables))
        else:
          # else appending an empty list, for preserving structure of the list of lists:
          temp_list.append([])
      # Action parameter variables, these are essentially x,y indexes for the action chosen:
      temp_list.append(self.encoding_variables.get_vars(self.num_x_index_variables))
      temp_list.append(self.encoding_variables.get_vars(self.num_y_index_variables))
      # now appending game stop variable for current black move, if the game is maker-maker:
      if (i%2 == 0 and self.makermaker_game == 1):
        temp_list.append(self.encoding_variables.get_vars(1))
      else:
        # else appending an empty list, for preserving structure of the list of lists:
        temp_list.append([])

      self.move_variables.append(temp_list)

    if (parsed.args.debug == 1):
      print("Number of (log) black choosing variables: ", self.num_black_action_variables)
      print("Number of (log) white choosing variables: ", self.num_white_action_variables)
      print("Number of (log) x index variables: ", self.num_x_index_variables)
      print("Number of (log) y index variables: ", self.num_y_index_variables)
      print("Move variables: ",self.move_variables)


    # allocating variables for black constraints, for now looking at the strings to check if both indexes are necessary:
    # note that right now we only handle goal constraints based on single position:
    self.black_goal_index_variables = []
    # checking for x index:
    temp_x_index_black_variables = []
    for line in parsed.black_goal_constraints:
      for constraint in line:
        if ('?x' in constraint):
          # we have x indexed position:
          temp_x_index_black_variables = self.encoding_variables.get_vars(self.num_x_index_variables)
          break
        # we only allocate the variables once:
        if (len(temp_x_index_black_variables) != 0):
          break
    self.black_goal_index_variables.append(temp_x_index_black_variables)
    # checking for y index
    temp_y_index_black_variables = []
    for line in parsed.black_goal_constraints:
      for constraint in line:
        if ('?y' in constraint):
          # we have y indexed position:
          temp_y_index_black_variables = self.encoding_variables.get_vars(self.num_y_index_variables)
          break
        # we only allocate the variables once:
        if (len(temp_y_index_black_variables) != 0):
          break
    self.black_goal_index_variables.append(temp_y_index_black_variables)

    # for now only handing breakthrough and kinghtthrough, so we do not need any extra variables:
    # as long as we only have a single conjunction in each line of the goal, we do not need any universal variables:
    for line in parsed.white_goal_constraints:
      assert(len(line) <= 1)

    if (parsed.args.debug == 1):
      print("black goal variables: ",self.black_goal_index_variables)

    # if the game is maker-maker then we need to handle the white illegal moves,
    # so we generate a variable as a flag:
    if (self.makermaker_game == 1):
      self.white_illegal = self.encoding_variables.get_single_var()
      if (parsed.args.debug == 1):
        print("white illegal variable: ",self.white_illegal)

    # Allocating forall position variables:
    self.forall_position_variables = []
    self.forall_position_variables.append(self.encoding_variables.get_vars(self.num_x_index_variables))
    self.forall_position_variables.append(self.encoding_variables.get_vars(self.num_y_index_variables))

    if (parsed.args.debug == 1):
      print("Forall position variables: ",self.forall_position_variables)

    # Allocating predicate variables, two variables are used one is occupied and
    # other color (but implicitly) for each time step:
    self.predicate_variables = []
    for i in range(parsed.depth+1):
      self.predicate_variables.append(self.encoding_variables.get_vars(2))

    if (parsed.args.debug == 1):
      print("Predicate variables: ",self.predicate_variables)



    # Generating quantifer blocks:
    self.generate_quantifier_blocks()

    #self.gates_generator = ggen(self.encoding_variables, self.encoding)

    # Generating d steps i.e., which includes black and white constraints:
    #self.generate_d_transitions()

    #self.generate_initial_gate()

    #self.generate_goal_gate()

    #self.generate_final_gate()
