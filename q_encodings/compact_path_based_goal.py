# Irfansha Shaik, 12.09.2021, Aarhus.

import math

import utils.lessthen_cir as lsc
from utils.gates import GatesGen as ggen
from utils.variables_dispatcher import VarDispatcher as vd


class CompactPathBasedGoal:

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

    # Grounded goal variables before forall position variables:
    self.quantifier_block.append(['# goal path variables: '])

    self.quantifier_block.append(['# start path variables :'])
    self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in self.start_path_variables) + ')'])

    self.quantifier_block.append(['# end path variables :'])
    self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in self.end_path_varaibles) + ')'])

    self.quantifier_block.append(['# Quantifier path variables and forall path variables:'])
    for i in range(self.path_depth):
      self.quantifier_block.append(['# Layer ' + str(i) + ':'])
      self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in self.goal_path_variables[3*i]) + ')'])
      self.quantifier_block.append(['forall(' + str(self.forall_path_variables[i]) + ')'])
      self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in self.goal_path_variables[3*i + 1]) + ')'])
      self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in self.goal_path_variables[3*i + 2]) + ')'])

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

    # Generating move restriction clauses inside if condition if enabled:
    if (self.parsed.args.forall_move_restrictions == 'in' and self.parsed.num_available_moves != int(math.pow(2, self.num_move_variables))):
      # White move restriction:
      self.encoding.append(['# Move constraints (if not powers of 2 or simply restricting moves) :'])
      #lsc.add_circuit(self.gates_generator, self.move_variables[time_step], self.parsed.num_positions)
      # using new open moves, further restricting search space:
      lsc.add_circuit(self.gates_generator, self.move_variables[time_step], self.parsed.num_available_moves)
      move_restriction_output_gate = self.gates_generator.output_gate

    # Move equality constraint with position variables:
    self.encoding.append(['# Equality gate for move and forall positional variables:'])
    self.gates_generator.complete_equality_gate(self.move_variables[time_step], self.forall_position_variables)
    equality_output_gate = self.gates_generator.output_gate
    self.encoding.append(['# In time step i, occupied must be false:'])
    self.gates_generator.and_gate([equality_output_gate, -self.predicate_variables[time_step][0] ])

    # If inside move restrictions are enables, including in the if condition:
    if (self.parsed.args.forall_move_restrictions == 'in' and self.parsed.num_available_moves != int(math.pow(2, self.num_move_variables))):
      # conjuction for move restriction and equality constraint:
      self.encoding.append(['# Conjuction for move restriction and above conjunction constraints:'])
      self.gates_generator.and_gate([move_restriction_output_gate, self.gates_generator.output_gate])

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


  # TODO: Testing is needed
  def generate_initial_gate(self):
    initial_step_output_gates = []

    self.encoding.append(["# ------------------------------------------------------------------------"])
    self.encoding.append(['# Initial state: '])

    if (len(self.parsed.black_initial_positions) != 0):

       # Constraints in forall branches for black positions:
       black_position_output_gates = []
       for position in self.parsed.black_initial_positions:
         binary_format_clause = self.generate_binary_format(self.forall_position_variables,position)
         self.gates_generator.and_gate(binary_format_clause)
         black_position_output_gates.append(self.gates_generator.output_gate)

       self.encoding.append(['# Or for all black forall position clauses: '])
       self.gates_generator.or_gate(black_position_output_gates)

       black_final_output_gate = self.gates_generator.output_gate

       self.encoding.append(['# if black condition is true then first time step occupied and color black (i.e. 0): '])
       self.gates_generator.and_gate([self.predicate_variables[0][0], -self.predicate_variables[0][1]])
       self.gates_generator.if_then_gate(black_final_output_gate, self.gates_generator.output_gate)

       initial_step_output_gates.append(self.gates_generator.output_gate)

    if (len(self.parsed.white_initial_positions) != 0):

      # Constraints in forall branches for white positions:
      white_position_output_gates = []

      for position in self.parsed.white_initial_positions:
        binary_format_clause = self.generate_binary_format(self.forall_position_variables,position)
        self.gates_generator.and_gate(binary_format_clause)
        white_position_output_gates.append(self.gates_generator.output_gate)

      self.encoding.append(['# Or for all white forall position clauses: '])
      self.gates_generator.or_gate(white_position_output_gates)

      white_final_output_gate = self.gates_generator.output_gate

      self.encoding.append(['# if white condition is true then first time step occupied and color white (i.e. 1): '])
      self.gates_generator.and_gate([self.predicate_variables[0][0], self.predicate_variables[0][1]])
      self.gates_generator.if_then_gate(white_final_output_gate, self.gates_generator.output_gate)

      initial_step_output_gates.append(self.gates_generator.output_gate)

    if (len(initial_step_output_gates) != 0):

      # Finally for all other forall branches, the position is unoccupied:
      self.encoding.append(['# for all other branches the occupied is 0: '])
      self.gates_generator.or_gate([black_final_output_gate, white_final_output_gate])
      self.gates_generator.or_gate([self.gates_generator.output_gate, -self.predicate_variables[0][0]])

      initial_step_output_gates.append(self.gates_generator.output_gate)
    else:
      self.encoding.append(['# In all branches the occupied is 0: '])
      self.gates_generator.and_gate([-self.predicate_variables[0][0]])

      initial_step_output_gates.append(self.gates_generator.output_gate)

    # Now final output gate for the initial state:
    self.gates_generator.and_gate(initial_step_output_gates)
    self.initial_output_gate = self.gates_generator.output_gate



  # Generating goal constraints:
  def generate_goal_gate(self):
    goal_step_output_gates = []
    self.encoding.append(["# ------------------------------------------------------------------------"])
    self.encoding.append(['# Goal state: '])


    # Generating equality constraints for zero layer:
    self.encoding.append(['# Constraints in zero layer, connecting with start and end path positions :'])
    self.encoding.append(['# Equality clause between S1 and START positons: '])
    self.gates_generator.complete_equality_gate(self.goal_path_variables[1], self.start_path_variables)
    temp_first_equality_output_gate = self.gates_generator.output_gate

    self.encoding.append(['# Equality clause between S2 and S0 positons: '])
    self.gates_generator.complete_equality_gate(self.goal_path_variables[2], self.goal_path_variables[0])
    temp_second_equality_output_gate = self.gates_generator.output_gate

    self.encoding.append(['# if then for negative forall 0 variable and conjunction of two equality gates: '])
    self.gates_generator.if_then_gate(-self.forall_path_variables[0], [temp_first_equality_output_gate, temp_second_equality_output_gate])
    goal_step_output_gates.append(self.gates_generator.output_gate)

    self.encoding.append(['# Equality clause between S1 and S0 positons: '])
    self.gates_generator.complete_equality_gate(self.goal_path_variables[1], self.goal_path_variables[0])
    temp_first_equality_output_gate = self.gates_generator.output_gate

    self.encoding.append(['# Equality clause between S2 and END positons: '])
    self.gates_generator.complete_equality_gate(self.goal_path_variables[2], self.end_path_varaibles)
    temp_second_equality_output_gate = self.gates_generator.output_gate

    self.encoding.append(['# if then for positive forall 0 variable and conjunction of two equality gates: '])
    self.gates_generator.if_then_gate(self.forall_path_variables[0], [temp_first_equality_output_gate, temp_second_equality_output_gate])
    goal_step_output_gates.append(self.gates_generator.output_gate)

    # For each layer until path depth, generate equality clauses:
    for i in range(1,self.path_depth):
      self.encoding.append(['# Constraints in ' + str(i) + 'th layer, connecting with start and end path positions :'])
      self.encoding.append(['# Equality clause between S' + str(3*i) + ' and S' + str((3*i)+2) + ' positons: '])
      self.gates_generator.complete_equality_gate(self.goal_path_variables[3*i], self.goal_path_variables[(3*i) + 2])
      temp_first_equality_output_gate = self.gates_generator.output_gate

      self.encoding.append(['# Equality clause between S' + str((3*i)+1) + ' and S' + str((3*i)-2) + ' positons: '])
      self.gates_generator.complete_equality_gate(self.goal_path_variables[(3*i)+1], self.goal_path_variables[(3*i)-2])
      temp_second_equality_output_gate = self.gates_generator.output_gate

      self.encoding.append(['# if then for negative forall ' + str(i) + ' variable and conjunction of two equality gates: '])
      self.gates_generator.if_then_gate(-self.forall_path_variables[i], [temp_first_equality_output_gate, temp_second_equality_output_gate])
      goal_step_output_gates.append(self.gates_generator.output_gate)

      self.encoding.append(['# Equality clause between S' + str(3*i) + ' and S' + str((3*i)+1) + ' positons: '])
      self.gates_generator.complete_equality_gate(self.goal_path_variables[3*i], self.goal_path_variables[(3*i) + 1])
      temp_first_equality_output_gate = self.gates_generator.output_gate

      self.encoding.append(['# Equality clause between S' + str((3*i)+2) + ' and S' + str((3*i)-1) + ' positons: '])
      self.gates_generator.complete_equality_gate(self.goal_path_variables[(3*i)+2], self.goal_path_variables[(3*i)-1])
      temp_second_equality_output_gate = self.gates_generator.output_gate

      self.encoding.append(['# if then for positive forall ' + str(i) + ' variable and conjunction of two equality gates: '])
      self.gates_generator.if_then_gate(self.forall_path_variables[i], [temp_first_equality_output_gate, temp_second_equality_output_gate])
      goal_step_output_gates.append(self.gates_generator.output_gate)


    # Finally neighbour constraints for the final two positions:

    self.encoding.append(['# Constratins for neighbours :'])
    # Connections with nieghbour information:
    # symbolic witness positions are connected:
    # iterating through each possible position value:
    for i in range(self.parsed.num_positions):
      self.encoding.append(['# position clauses: '])
      binary_format_clause = self.generate_binary_format(self.goal_path_variables[-2],i)
      self.gates_generator.and_gate(binary_format_clause)
      if_condition_output_gate = self.gates_generator.output_gate
      neighbour_output_gates = []
      self.encoding.append(['# neighbour clauses: '])

      # For each neighbour we generate a clause:
      for cur_neighbour in self.parsed.neighbour_dict[i]:
        temp_binary_format_clause = self.generate_binary_format(self.goal_path_variables[-1],cur_neighbour)
        self.gates_generator.and_gate(temp_binary_format_clause)
        neighbour_output_gates.append(self.gates_generator.output_gate)

      # For allowing shorter paths, we say the position is also its neighbour:
      temp_binary_format_clause = self.generate_binary_format(self.goal_path_variables[-1],i)
      self.gates_generator.and_gate(temp_binary_format_clause)
      neighbour_output_gates.append(self.gates_generator.output_gate)

      # One of the values must be true, so a disjunction:
      self.gates_generator.or_gate(neighbour_output_gates)

      # If then clause for the neighbour implication:
      self.encoding.append(['# if then clause : '])
      self.gates_generator.if_then_gate(if_condition_output_gate,self.gates_generator.output_gate)
      goal_step_output_gates.append(self.gates_generator.output_gate)

    # in the branches of inner most positions, the positions must be black:
    self.encoding.append(['# Equality clause for the last second path variables and forall position variables: '])
    self.gates_generator.complete_equality_gate(self.goal_path_variables[-2], self.forall_position_variables)
    if_second_inner_position_gate = self.gates_generator.output_gate

    self.encoding.append(['# Equality clause for the inner most path variables and forall position variables: '])
    self.gates_generator.complete_equality_gate(self.goal_path_variables[-1], self.forall_position_variables)
    if_inner_most_position_gate = self.gates_generator.output_gate

    self.gates_generator.or_gate([if_second_inner_position_gate, if_inner_most_position_gate])
    if_both_inner_positions_gate = self.gates_generator.output_gate

    # the position must be occupied and the color must be black:
    self.encoding.append(['# The goal position is occupied and the color is black and conjuction with neighbour equality gate: '])
    self.gates_generator.and_gate([self.predicate_variables[-1][0], -self.predicate_variables[-1][1]])
    constraints_output_gate = self.gates_generator.output_gate

    self.encoding.append(['# if then clause : '])
    # The if condition for the path constraints:
    self.gates_generator.if_then_gate(if_both_inner_positions_gate, constraints_output_gate)
    goal_step_output_gates.append(self.gates_generator.output_gate)



    start_border_output_gates = []
    self.encoding.append(['# Start boarder clauses : '])
    # Specifying the start borders:
    for pos in self.parsed.start_boarder:
      binary_format_clause = self.generate_binary_format(self.start_path_variables,pos)
      self.gates_generator.and_gate(binary_format_clause)
      start_border_output_gates.append(self.gates_generator.output_gate)

    self.encoding.append(['# disjunction of all start boarder positions : '])
    self.gates_generator.or_gate(start_border_output_gates)

    goal_step_output_gates.append(self.gates_generator.output_gate)

    end_border_output_gates = []
    self.encoding.append(['# End boarder clauses : '])
    # Specifying the end borders:
    for pos in self.parsed.end_boarder:
      binary_format_clause = self.generate_binary_format(self.end_path_varaibles,pos)
      self.gates_generator.and_gate(binary_format_clause)
      end_border_output_gates.append(self.gates_generator.output_gate)

    self.encoding.append(['# disjunction of all end boarder positions : '])
    self.gates_generator.or_gate(end_border_output_gates)

    goal_step_output_gates.append(self.gates_generator.output_gate)

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
        #lsc.add_circuit(self.gates_generator, self.move_variables[i], self.parsed.num_positions)
        # restricting more moves:
        lsc.add_circuit(self.gates_generator, self.move_variables[i], self.parsed.num_available_moves)
        step_restricted_black_output_gates.append(self.gates_generator.output_gate)

    self.encoding.append(['# And gate for all restricted black move clauses: '])
    self.gates_generator.and_gate(step_restricted_black_output_gates)
    self.restricted_black_gate = self.gates_generator.output_gate


  def generate_restricted_white_moves(self):

    step_restricted_white_output_gates = []

    self.encoding.append(["# ------------------------------------------------------------------------"])
    self.encoding.append(['# Restricted white moves: '])

    for i in range(self.parsed.depth):
      if (i%2 == 1):
        #lsc.add_circuit(self.gates_generator, self.move_variables[i], self.parsed.num_positions)
        # restricting more moves:
        lsc.add_circuit(self.gates_generator, self.move_variables[i], self.parsed.num_available_moves)
        step_restricted_white_output_gates.append(self.gates_generator.output_gate)

    self.encoding.append(['# And gate for all restricted white move clauses: '])
    self.gates_generator.and_gate(step_restricted_white_output_gates)
    self.restricted_white_gate = self.gates_generator.output_gate


  # Final output gate is an and-gate with inital, goal and transition gates:
  def generate_final_gate(self):
    self.encoding.append(["# ------------------------------------------------------------------------"])
    self.encoding.append(['# Final gate: '])

    self.encoding.append(['# Conjunction of Initial gate and Transition gate and Goal gate: '])
    # Restrictions on black moves are invalid if not powers of 2:
    if (self.parsed.num_available_moves != int(math.pow(2, self.num_move_variables))):
      self.gates_generator.and_gate([self.restricted_black_gate, self.initial_output_gate, self.transition_output_gate, self.goal_output_gate])
    else:
      self.gates_generator.and_gate([self.initial_output_gate, self.transition_output_gate, self.goal_output_gate])
    temp_and_output_gate = self.gates_generator.output_gate

    temp_if_condition_gates = []

    # Adding restriction position gate to if condition if enabled:
    if (self.parsed.num_positions != int(math.pow(2, self.num_position_variables)) and self.parsed.args.restricted_position_constraints == 1):
      temp_if_condition_gates.append(self.restricted_positions_gate)

    # Adding restriction white gate to if condition if enabled:
    if (self.parsed.num_available_moves != int(math.pow(2, self.num_move_variables)) and self.parsed.args.forall_move_restrictions == 'out'):
      temp_if_condition_gates.append(self.restricted_white_gate)

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
    # Handling single move, log 1 is 0:
    if (parsed.num_available_moves == 1):
      self.num_move_variables = 1
    else:
      self.num_move_variables = math.ceil(math.log2(parsed.num_available_moves))
    self.move_variables = []
    for i in range(parsed.depth):
      self.move_variables.append(self.encoding_variables.get_vars(self.num_move_variables))

    if (parsed.args.debug == 1):
      print("Number of (log) move variables: ", self.num_move_variables)
      print("Move variables: ",self.move_variables)

    # Moves are same as the vertexs/positions on the board:
    self.num_position_variables = math.ceil(math.log2(parsed.num_positions))


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


    # Depth for flat path based representation:
    self.safe_max_path_length = len(self.parsed.black_initial_positions) + int((self.parsed.depth + 1)/2)
    self.path_depth = math.ceil(math.log2(self.safe_max_path_length))

    assert(self.safe_max_path_length >= 2)

    # Generating forall vars for path based quanitfier alterations:
    self.forall_path_variables = self.encoding_variables.get_vars(self.path_depth)

    # Start and End path variables:
    self.start_path_variables = self.encoding_variables.get_vars(self.num_position_variables)
    self.end_path_varaibles = self.encoding_variables.get_vars(self.num_position_variables)

    # Goal path variables:
    self.goal_path_variables = []
    for i in range(3*(self.path_depth)):
      self.goal_path_variables.append(self.encoding_variables.get_vars(self.num_position_variables))

    if (parsed.args.debug == 1):
      print("Goal forall path variables: ",self.forall_path_variables)


    # Generating quantifer blocks:
    self.generate_quantifier_blocks()

    self.gates_generator = ggen(self.encoding_variables, self.encoding)

    # Generating d steps i.e., which includes black and white constraints:
    self.generate_d_transitions()

    self.generate_initial_gate()

    self.generate_goal_gate()

    # Note: Improved version needs to change this with only open positions:
    if (self.parsed.num_available_moves != int(math.pow(2, self.num_move_variables))):
      self.generate_restricted_black_moves()

      # we only generate restricted constraints outside the transitions if specified explicitly:
      if (self.parsed.args.forall_move_restrictions == 'out'):
        self.generate_restricted_white_moves()

    if (self.parsed.num_positions != int(math.pow(2, self.num_position_variables)) and self.parsed.args.restricted_position_constraints == 1):
      self.restricted_positions_gate = 0 # Can never be 0
      # positions combinations to be restricted:
      self.encoding.append(['#Position combinations restricted :'])
      lsc.add_circuit(self.gates_generator, self.forall_position_variables, self.parsed.num_positions)
      self.restricted_positions_gate = self.gates_generator.output_gate

    self.generate_final_gate()
