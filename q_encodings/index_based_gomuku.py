# Irfansha Shaik, 30.03.2022, Aarhus.

import math

import utils.adder_cir as addc
import utils.lessthen_cir as lsc
from utils.gates import GatesGen as ggen
from utils.variables_dispatcher import VarDispatcher as vd


class IndexBasedGomuku:

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
    self.quantifier_block.append(['# Move variables: '])
    for i in range(self.parsed.depth):
      # starts with 0 and even is black (i.e., existential moves):
      if (i % 2 == 0):
        self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in self.move_variables[i]) + ')'])
      else:
        self.quantifier_block.append(['forall(' + ', '.join(str(x) for x in self.move_variables[i]) + ')'])

    # witness index boolean variables:
    self.quantifier_block.append(['# Witness direction boolean variables: '])
    self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in self.index_line_boolean_variables) + ')'])


    # witness variables before forall position variables:
    self.quantifier_block.append(['# Starting witness index variables: '])
    self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in self.witness_variables) + ')'])

    # Forall position variables:
    self.quantifier_block.append(['# Forall position variables: '])
    self.quantifier_block.append(['forall(' + ', '.join(str(x) for x in self.forall_position_variables) + ')'])

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

    self.encoding.append(['# Black position constraints: '])
    self.gates_generator.and_gate([self.predicate_variables[-1][0], -self.predicate_variables[-1][1]])
    self.black_position_output_gate = self.gates_generator.output_gate

    # dividing the witness variables to two parts, x axis and y axis:
    x_vars = self.witness_variables[:self.num_single_index_move_variables]
    y_vars = self.witness_variables[self.num_single_index_move_variables:]

    # x_vars and y_vars must be within bounds, so adding upper bounds:
    self.encoding.append(['# bounds for x and y vars with board size: '])
    lsc.add_circuit(self.gates_generator, x_vars, self.board_size)
    goal_step_output_gates.append(self.gates_generator.output_gate)
    lsc.add_circuit(self.gates_generator, y_vars, self.board_size)
    goal_step_output_gates.append(self.gates_generator.output_gate)

    # Generate x increment list:
    x_increment_list = []
    # First appending itself:
    x_increment_list.append(x_vars)
    for i in range(self.max_witness_length-1):
      temp_increment_output_gates = addc.adder_circuit(self.gates_generator,x_vars, i+1)
      x_increment_list.append(temp_increment_output_gates)
    #print(x_increment_list)
    # Generate y increment list:
    y_increment_list = []
    # First appending itself:
    y_increment_list.append(y_vars)
    for i in range(self.max_witness_length-1):
      temp_increment_output_gates = addc.adder_circuit(self.gates_generator,y_vars, i+1)
      y_increment_list.append(temp_increment_output_gates)
    #print(y_increment_list)
    # Generate y decrement list:
    y_decrement_list = []
    # First appending itself:
    y_decrement_list.append(y_vars)
    for i in range(self.max_witness_length-1):
      temp_decrement_output_gates = addc.subtractor_circuit(self.gates_generator,y_vars, i+1)
      y_decrement_list.append(temp_decrement_output_gates)
    #print(y_decrement_list)

    # Upper bounds for x and y axis of the starting position in each of the following cases:
    #----------------------------------------------------------------------------------------------------------------
    #  constraints for down diagonal, the direction booleans are 00:
    down_diagonal_output_gates = []
    self.encoding.append(['# Constraints for down diagonal: '])

    step_down_diagonal_output_gates = []
    self.encoding.append(['# position equalities with forall variables: '])
    #  equality output gates for down diagonal:
    for i in range(self.max_witness_length):
      cur_x = x_increment_list[i]
      cur_y = y_decrement_list[i]
      cur_full_position_variables = []
      cur_full_position_variables.extend(cur_x)
      cur_full_position_variables.extend(cur_y)
      # equality with forall variables:
      self.gates_generator.complete_equality_gate(cur_full_position_variables,self.forall_position_variables)
      step_down_diagonal_output_gates.append(self.gates_generator.output_gate)

    #  disjunction of the equality gates:
    self.gates_generator.or_gate(step_down_diagonal_output_gates)
    # If then condition, if the diagonal constraints hold then all such positions are black:
    self.encoding.append(['# if then constraint, if the diagonal constraint holds then all such positions are black: '])
    self.gates_generator.if_then_gate(self.gates_generator.output_gate,self.black_position_output_gate)
    down_diagonal_output_gates.append(self.gates_generator.output_gate)

    #  y !< max - 1:
    self.encoding.append(['# y vars lower bound with y !< max - 1: '])
    lsc.add_circuit(self.gates_generator, y_vars, self.max_witness_length - 1)
    y_vars_lower_bound_output_gate = -self.gates_generator.output_gate
    down_diagonal_output_gates.append(y_vars_lower_bound_output_gate)

    #  x < size - max + 1:
    self.encoding.append(['# x vars upper bound with x < size - max + 1: '])
    lsc.add_circuit(self.gates_generator, x_vars, self.board_size - self.max_witness_length + 1)
    x_vars_upper_bound_output_gate = self.gates_generator.output_gate
    down_diagonal_output_gates.append(x_vars_upper_bound_output_gate)

    self.encoding.append(['# conjunction of all diagonal constraints: '])
    self.gates_generator.and_gate(down_diagonal_output_gates)
    final_diagonal_output_gate = self.gates_generator.output_gate

    # down diagonal bits, 00:
    self.encoding.append(['# down diagonal boolean variables, 00: '])
    self.gates_generator.and_gate([-self.index_line_boolean_variables[0], -self.index_line_boolean_variables[1]])
    # if then constraints, if the line chosen is diagonal then above constraints hold:
    self.gates_generator.if_then_gate(self.gates_generator.output_gate,final_diagonal_output_gate)
    goal_step_output_gates.append(self.gates_generator.output_gate)
    #----------------------------------------------------------------------------------------------------------------

    #   constraints for vertical, the direction booleans are 01:
    #----------------------------------------------------------------------------------------------------------------
    self.encoding.append(['# Constraints for vertical line: '])
    vertical_output_gates = []

    step_vertical_output_gates = []
    self.encoding.append(['# position equalities with forall variables: '])
    #  equality output gates for vertical:
    for i in range(self.max_witness_length):
      cur_x = x_vars
      cur_y = y_increment_list[i]
      cur_full_position_variables = []
      cur_full_position_variables.extend(cur_x)
      cur_full_position_variables.extend(cur_y)
      # equality with forall variables:
      self.gates_generator.complete_equality_gate(cur_full_position_variables,self.forall_position_variables)
      step_vertical_output_gates.append(self.gates_generator.output_gate)

    #  disjunction of the equality gates:
    self.gates_generator.or_gate(step_vertical_output_gates)
    self.encoding.append(['# if then constraint, if the vertical constraint holds then all such positions are black: '])
    self.gates_generator.if_then_gate(self.gates_generator.output_gate,self.black_position_output_gate)
    vertical_output_gates.append(self.gates_generator.output_gate)

    #  y < size - max + 1:
    self.encoding.append(['# y vars upper bound with y < size - max + 1: '])
    lsc.add_circuit(self.gates_generator, y_vars, self.board_size - self.max_witness_length + 1)
    y_vars_upper_bound_output_gate = self.gates_generator.output_gate
    vertical_output_gates.append(y_vars_upper_bound_output_gate)

    # If then condition, if the vertical constraints hold then all such positions are black:
    self.encoding.append(['# conjunction of vertical constraints: '])
    self.gates_generator.and_gate(vertical_output_gates)
    final_vertical_output_gate = self.gates_generator.output_gate

    # vertical bits, 01:
    self.encoding.append(['# vertical line boolean variables, 01: '])
    self.gates_generator.and_gate([-self.index_line_boolean_variables[0], self.index_line_boolean_variables[1]])
    self.gates_generator.if_then_gate(self.gates_generator.output_gate,final_vertical_output_gate)
    goal_step_output_gates.append(self.gates_generator.output_gate)
    #----------------------------------------------------------------------------------------------------------------

    #----------------------------------------------------------------------------------------------------------------
    #   constraints for horizontal, the direction booleans are 10:
    self.encoding.append(['# Constraints for horizontal line: '])
    horizontal_output_gates = []

    step_horizontal_output_gates = []
    self.encoding.append(['# position equalities with forall variables: '])
    #  equality output gates for down diagonal:
    for i in range(self.max_witness_length):
      cur_x = x_increment_list[i]
      cur_y = y_vars
      cur_full_position_variables = []
      cur_full_position_variables.extend(cur_x)
      cur_full_position_variables.extend(cur_y)
      # equality with forall variables:
      self.gates_generator.complete_equality_gate(cur_full_position_variables,self.forall_position_variables)
      step_horizontal_output_gates.append(self.gates_generator.output_gate)

    #  disjunction of the equality gates:
    self.gates_generator.or_gate(step_horizontal_output_gates)
    # If then condition, if the horizontal constraints hold then all such positions are black:
    self.encoding.append(['# if then constraint, if the horizontal constraint holds then all such positions are black: '])
    self.gates_generator.if_then_gate(self.gates_generator.output_gate,self.black_position_output_gate)
    horizontal_output_gates.append(self.gates_generator.output_gate)

    #  x < size - max + 1:
    self.encoding.append(['# x vars upper bound with x < size - max + 1: '])
    horizontal_output_gates.append(x_vars_upper_bound_output_gate)

    self.encoding.append(['# conjunction of horizontal constraints: '])
    self.gates_generator.and_gate(horizontal_output_gates)
    final_horizontal_output_gate = self.gates_generator.output_gate

    # horizontal bits, 10:
    self.encoding.append(['# horizontal boolean variables, 10: '])
    self.gates_generator.and_gate([self.index_line_boolean_variables[0], -self.index_line_boolean_variables[1]])
    self.gates_generator.if_then_gate(self.gates_generator.output_gate,final_horizontal_output_gate)
    goal_step_output_gates.append(self.gates_generator.output_gate)
    #----------------------------------------------------------------------------------------------------------------


    #   constraints for up diagonal, the direction booleans are 11:
    self.encoding.append(['# Constraints for up diagonal: '])
    up_diagonal_output_gates = []

    step_up_diagonal_output_gates = []
    self.encoding.append(['# position equalities with forall variables: '])
    #  equality output gates for up diagonal:
    for i in range(self.max_witness_length):
      cur_x = x_increment_list[i]
      cur_y = y_increment_list[i]
      cur_full_position_variables = []
      cur_full_position_variables.extend(cur_x)
      cur_full_position_variables.extend(cur_y)
      # equality with forall variables:
      self.gates_generator.complete_equality_gate(cur_full_position_variables,self.forall_position_variables)
      step_up_diagonal_output_gates.append(self.gates_generator.output_gate)

    #  disjunction of the equality gates:
    self.gates_generator.or_gate(step_up_diagonal_output_gates)
    # If then condition, if the diagonal constraints hold then all such positions are black:
    self.encoding.append(['# if then constraint, if the diagonal constraint holds then all such positions are black: '])
    self.gates_generator.if_then_gate(self.gates_generator.output_gate,self.black_position_output_gate)
    up_diagonal_output_gates.append(self.gates_generator.output_gate)

    #  y < size - max + 1:
    self.encoding.append(['# y vars upper bound with y < size - max + 1: '])
    up_diagonal_output_gates.append(y_vars_upper_bound_output_gate)

    #  x < size - max + 1:
    self.encoding.append(['# x vars upper bound with x < size - max + 1: '])
    up_diagonal_output_gates.append(x_vars_upper_bound_output_gate)

    self.encoding.append(['# conjunction of diagonal constraints: '])
    self.gates_generator.and_gate(up_diagonal_output_gates)
    final_up_diagonal_output_gate = self.gates_generator.output_gate

    # up diagonal bits, 11:
    self.encoding.append(['# up diagonal boolean variables, 11: '])
    self.gates_generator.and_gate([self.index_line_boolean_variables[0], self.index_line_boolean_variables[1]])
    self.gates_generator.if_then_gate(self.gates_generator.output_gate,final_up_diagonal_output_gate)
    goal_step_output_gates.append(self.gates_generator.output_gate)
    #----------------------------------------------------------------------------------------------------------------
    # Final goal gate:
    self.encoding.append(['# Final and gate for goal constraints: '])
    self.gates_generator.and_gate(goal_step_output_gates)
    self.goal_output_gate = self.gates_generator.output_gate

  def generate_restricted_black_moves(self):

    step_restricted_black_output_gates = []

    self.encoding.append(["# ------------------------------------------------------------------------"])
    self.encoding.append(['# Restricted black moves: '])

    for i in range(self.parsed.depth):
      if (i%2 == 0):
        # restricting indexes:
        lsc.add_circuit(self.gates_generator, self.move_variables[i][:self.num_single_index_move_variables], self.board_size)
        step_restricted_black_output_gates.append(self.gates_generator.output_gate)
        lsc.add_circuit(self.gates_generator, self.move_variables[i][self.num_single_index_move_variables:], self.board_size)
        step_restricted_black_output_gates.append(self.gates_generator.output_gate)


    self.encoding.append(['# And gate for all restricted black move clauses: '])
    self.gates_generator.and_gate(step_restricted_black_output_gates)
    self.restricted_black_gate = self.gates_generator.output_gate


  # Final output gate is an and-gate with inital, goal and transition gates:
  def generate_final_gate(self):
    self.encoding.append(["# ------------------------------------------------------------------------"])
    self.encoding.append(['# Final gate: '])

    self.encoding.append(['# Conjunction of Initial gate and Transition gate and Goal gate: '])
    # Restrictions on black moves are invalid if not powers of 2:
    if (self.parsed.num_available_moves != int(math.pow(2, self.num_move_variables)) and self.parsed.args.black_move_restrictions == 1):
      self.gates_generator.and_gate([self.restricted_black_gate, self.initial_output_gate, self.transition_output_gate, self.goal_output_gate])
    else:
      self.gates_generator.and_gate([self.initial_output_gate, self.transition_output_gate, self.goal_output_gate])
    temp_and_output_gate = self.gates_generator.output_gate

    temp_if_condition_gates = []

    # Adding restriction position gate to if condition if enabled:
    if (self.parsed.num_positions != int(math.pow(2, self.num_position_variables)) and self.parsed.args.restricted_position_constraints == 1):
      temp_if_condition_gates.append(self.restricted_positions_gate)

    # if atleast one restriction is enabled, we generate if condition:
    if (len(temp_if_condition_gates) != 0):
      self.encoding.append(['# If condition with position and/or white moves restriction : '])
      self.gates_generator.and_gate(temp_if_condition_gates)
      self.gates_generator.if_then_gate(self.gates_generator.output_gate, temp_and_output_gate)
      self.final_output_gate = self.gates_generator.output_gate
    else:
      self.final_output_gate = temp_and_output_gate


  def __init__(self, parsed):
    self.parsed = parsed
    self.encoding_variables = vd()
    self.quantifier_block = []
    self.encoding = []
    self.initial_output_gate = 0 # initial output gate can never be 0
    self.goal_output_gate = 0 # goal output gate can never be 0
    self.transition_step_output_gates = []
    self.transition_output_gate = 0 # Can never be 0
    self.restricted_black_gate = 0 # Can never be 0
    self.restricted_white_gate = 0 # Can never be 0
    self.final_output_gate = 0 # Can never be 0


    # Allocating action variables for each time step until depth:
    # board size is sqrt of number of positions, so the move needs 2 times of it:
    self.num_move_variables = 2*math.ceil(math.log2(math.sqrt(parsed.num_available_moves)))
    self.num_single_index_move_variables = int(self.num_move_variables/2)
    self.board_size = int(math.sqrt(parsed.num_available_moves))
    self.move_variables = []
    for i in range(parsed.depth):
      self.move_variables.append(self.encoding_variables.get_vars(self.num_move_variables))

    if (parsed.args.debug == 1):
      print("Number of (log) move variables: ", self.num_move_variables)
      print("Move variables: ",self.move_variables)

    # Moves are same as the vertexs/positions on the board:
    self.num_position_variables = self.num_move_variables


    # Allocating forall position variables:
    self.forall_position_variables = self.encoding_variables.get_vars(self.num_position_variables)

    if (parsed.args.debug == 1):
      print("Forall position variables: ",self.forall_position_variables)

    # Allocating predicate variables, two variables are used one is occupied and
    # other color (but implicitly) for each time step:
    self.predicate_variables = []
    for i in range(parsed.depth+1):
      self.predicate_variables.append(self.encoding_variables.get_vars(2))

    if (parsed.args.debug == 1):
      print("Predicate variables: ",self.predicate_variables)

    # For index based gomuku, we only need the starting position and 2 bits for specifying which line it is:
    self.index_line_boolean_variables = self.encoding_variables.get_vars(2)
    # For now reusing the max winning configuration length, later need to specify explicitly:
    self.max_witness_length = parsed.max_win_config_length

    # Allocating witness variables:
    self.witness_variables = self.encoding_variables.get_vars(self.num_position_variables)


    if (parsed.args.debug == 1):
      print("Index boolean variables: ",self.index_line_boolean_variables)
      print("Starting position of winning line: ",self.witness_variables)


    # Generating quantifer blocks:
    self.generate_quantifier_blocks()

    self.gates_generator = ggen(self.encoding_variables, self.encoding)

    # Generating d steps i.e., which includes black and white constraints:
    self.generate_d_transitions()

    self.generate_initial_gate()

    self.generate_goal_gate()

    # Note: Improved version needs to change this with only open positions:
    if (self.parsed.num_available_moves != int(math.pow(2, self.num_move_variables)) and self.parsed.args.black_move_restrictions == 1):
      self.generate_restricted_black_moves()

    self.generate_final_gate()
