# Irfansha Shaik, 14.12.2022, Aarhus.

import math

import utils.lessthen_cir as lsc
from utils.gates import GatesGen as ggen
from utils.unique_gates import GatesGen as uggen
from utils.variables_dispatcher import VarDispatcher as vd


class NestedTraversal:

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
        # also adding exists legal variable:
        self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in self.indicator_variables[i]) +')'])

    # Grounded reachable variables before forall position variables:
    self.quantifier_block.append(['# reachable variables: '])
    self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in self.reachable_variables) + ')'])

    # Forall position variables:
    self.quantifier_block.append(['# Forall position variables: '])
    self.quantifier_block.append(['forall(' + ', '.join(str(x) for x in self.forall_position_variables) + ')'])

    # Finally predicate variables for each time step:
    self.quantifier_block.append(['# Predicate variables: '])
    for i in range(self.parsed.depth+1):
      self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in self.predicate_variables[i]) + ')'])



  def generate_black_transition(self, time_step):
    cur_transition_step_output_gates = []
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
    cur_transition_step_output_gates.append(self.gates_generator.output_gate)

    # Finally propogation constraints:
    self.encoding.append(['# propagation constraints:'])
    self.gates_generator.complete_equality_gate(self.predicate_variables[time_step], self.predicate_variables[time_step+1])
    self.encoding.append(['# If the time and equality constraints does not hold predicates are propagated:'])
    self.gates_generator.or_gate([conditional_and_output_gate, self.gates_generator.output_gate])
    cur_transition_step_output_gates.append(self.gates_generator.output_gate)

    # making a conjunction here directly:
    self.gates_generator.and_gate(cur_transition_step_output_gates)
    self.transition_step_output_gates.append(self.gates_generator.output_gate)


  def generate_white_transition(self, time_step):
    cur_transition_step_output_gates = []
    self.encoding.append(['# Player 2 (white) transition function for time step ' + str(time_step)+ ': '])

    # Generating move restriction clauses inside if condition if enabled:
    if (self.parsed.num_available_moves != int(math.pow(2, self.num_move_variables))):
      # White move restriction:
      self.encoding.append(['# Move constraints (if not powers of 2 or simply restricting moves) :'])
      #lsc.add_circuit(self.gates_generator, self.move_variables[time_step], self.parsed.num_positions)
      # using new open moves, further restricting search space:
      lsc.add_circuit(self.gates_generator, self.move_variables[time_step], self.parsed.num_available_moves)

      # equality with first legal indicator variable:
      self.gates_generator.single_equality_gate(self.gates_generator.output_gate, self.indicator_variables[time_step][0])
      cur_transition_step_output_gates.append(self.gates_generator.output_gate)
    else:
      cur_transition_step_output_gates.append(self.indicator_variables[time_step][0])

    # Move equality constraint with position variables:
    self.encoding.append(['# Equality gate for move and forall positional variables:'])
    self.gates_generator.complete_equality_gate(self.move_variables[time_step], self.forall_position_variables)
    equality_output_gate = self.gates_generator.output_gate

    # in the right branch the indicator variables contain the legal information where the position is open:
    self.gates_generator.single_equality_gate(-self.predicate_variables[time_step][0],self.indicator_variables[time_step][1])
    self.gates_generator.if_then_gate(equality_output_gate,self.gates_generator.output_gate)
    cur_transition_step_output_gates.append(self.gates_generator.output_gate)

    # constraints choosing white position:
    self.encoding.append(['# Choosing white position constraints:'])
    self.encoding.append(['# In time step i+1, occupied must be true and color must be white (i.e., 1):'])
    self.gates_generator.and_gate([self.predicate_variables[time_step + 1][0], self.predicate_variables[time_step + 1][1]])
    # Now if condition:
    self.encoding.append(['# If equality constraints and legal variable hold then choosing white constraints must be true:'])
    self.gates_generator.or_gate([-equality_output_gate, -self.indicator_variables[time_step][0], -self.indicator_variables[time_step][1], self.gates_generator.output_gate])
    cur_transition_step_output_gates.append(self.gates_generator.output_gate)

    # Finally propogation constraints:
    self.encoding.append(['# propagation constraints:'])
    self.gates_generator.complete_equality_gate(self.predicate_variables[time_step], self.predicate_variables[time_step+1])
    self.encoding.append(['# If the time and equality constraints does not hold predicates are propagated:'])
    self.gates_generator.or_gate([equality_output_gate, -self.indicator_variables[time_step][0], -self.indicator_variables[time_step][1], self.gates_generator.output_gate])
    cur_transition_step_output_gates.append(self.gates_generator.output_gate)

    # current transition conjunction:
    self.gates_generator.and_gate(cur_transition_step_output_gates)
    self.transition_step_output_gates.append(self.gates_generator.output_gate)

  def generate_d_transitions(self):
    self.encoding.append(["# ------------------------------------------------------------------------"])
    self.encoding.append(['# Transitions: '])
    for i in range(self.parsed.depth):
      if (i%2 == 0):
        self.generate_black_transition(i)
      else:
        self.generate_white_transition(i)


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

    # first black position constraints:
    self.encoding.append(['# black position gate: '])
    self.gates_generator.and_gate([self.predicate_variables[-1][0], -self.predicate_variables[-1][1]])
    black_gate = self.gates_generator.output_gate

    # start boarder reachable clauses:
    self.encoding.append(['# start boarder vars reachable: '])
    for pos in self.parsed.start_boarder:
      cur_binary_format_clause = self.generate_binary_format(self.forall_position_variables,pos)
      self.gates_generator.and_gate(cur_binary_format_clause)
      cur_binary_output_gate = self.gates_generator.output_gate
      # in the right forall branch, the reachability var is implied with non-black:
      # if then gate reachable var with non-black gate:
      #self.gates_generator.if_then_gate(-black_gate,self.reachable_variables[pos])
      self.gates_generator.single_equality_gate(-black_gate,self.reachable_variables[pos])
      # in the corresponding branch:
      self.gates_generator.if_then_gate(cur_binary_output_gate,self.gates_generator.output_gate)
      goal_step_output_gates.append(self.gates_generator.output_gate)
    self.encoding.append(['# connecting neighbours: '])
    # connect neighbour and reachability:
    for i in range(self.parsed.num_positions):
      # if any of the neighbours are reachable then we imply reachability with non-black position:
      neighbour_reachable = []
      for cur_neighbour in self.parsed.neighbour_dict[i]:
        neighbour_reachable.append(self.reachable_variables[cur_neighbour])
      # disjunction of reachability:
      self.gates_generator.or_gate(neighbour_reachable)
      disjunct_reachable_output_gate = self.gates_generator.output_gate
      # generating the corresponding forall branch:
      cur_binary_format_clause = self.generate_binary_format(self.forall_position_variables,i)
      self.gates_generator.and_gate(cur_binary_format_clause)
      cur_binary_output_gate = self.gates_generator.output_gate

      # if condition conjunction:
      self.gates_generator.and_gate([disjunct_reachable_output_gate, cur_binary_output_gate])
      final_if_condition_output_gate = self.gates_generator.output_gate

      # first implication with non-black:
      #self.gates_generator.if_then_gate(-black_gate,self.reachable_variables[i])
      self.gates_generator.single_equality_gate(-black_gate,self.reachable_variables[i])
      implication_output_gate = self.gates_generator.output_gate
      # if both disjunct and branch are true, we do the implication:
      self.gates_generator.if_then_gate(final_if_condition_output_gate,implication_output_gate)
      goal_step_output_gates.append(self.gates_generator.output_gate)
    self.encoding.append(['# constraining end vars unreachable: '])
    # clauses for end board unreachability:
    end_unreachable_clauses = []
    # for each end board, we constraint it to unreachable:
    for pos in self.parsed.end_boarder:
      end_unreachable_clauses.append(-self.reachable_variables[pos])
    # conjunction of all the clauses:
    self.gates_generator.and_gate(end_unreachable_clauses)
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


    # if atleast one restriction is enabled, we generate if condition:
    if (len(temp_if_condition_gates) != 0):
      self.encoding.append(['# If condition with position and/or white moves restriction : '])
      self.gates_generator.and_gate(temp_if_condition_gates)
      self.gates_generator.if_then_gate(self.gates_generator.output_gate, temp_and_output_gate)
      self.final_output_gate = self.gates_generator.output_gate
    else:
      self.final_output_gate = temp_and_output_gate

# Final output gate is an nested-gate with inital, goal and transition gates:
  def generate_nested_final_gate(self):

    self.encoding.append(["# ------------------------------------------------------------------------"])
    self.encoding.append(['# Nested gates: '])

    #'''
    # starting with goal gate and last black gate:
    self.gates_generator.and_gate([self.transition_step_output_gates[-1], self.goal_output_gate])
    cur_outgate = self.gates_generator.output_gate
    #print("and", cur_outgate)

    #print(self.parsed.depth)

    for i in range(self.parsed.depth-1):
      reverse_index = self.parsed.depth-i-2
      # for white we imply with white legal condition:
      if (reverse_index%2==1):
        # gathering legal boolen variables:
        self.encoding.append(['# white valid implication constraints at reverse index: ' + str(reverse_index)])
        # first implying the cur_outgate with valid move gate:
        self.gates_generator.or_gate([-self.indicator_variables[reverse_index][0], -self.indicator_variables[reverse_index][1], cur_outgate])

        # conjunction with this round of constraints:
        self.gates_generator.and_gate([self.transition_step_output_gates[reverse_index], self.gates_generator.output_gate])

        cur_outgate = self.gates_generator.output_gate
      # for black we imply with game stop condition:
      else:
        self.encoding.append(['# black constraint conjunction gate at : ' + str(reverse_index)])
        self.gates_generator.and_gate([self.transition_step_output_gates[reverse_index], cur_outgate])
        cur_outgate = self.gates_generator.output_gate



    self.encoding.append(["# ------------------------------------------------------------------------"])
    self.encoding.append(['# Final gate: '])


    # Restrictions on black moves are invalid if not powers of 2:
    if (self.parsed.num_available_moves != int(math.pow(2, self.num_move_variables))):
      self.gates_generator.and_gate([self.restricted_black_gate, self.initial_output_gate, cur_outgate])
    else:
      self.gates_generator.and_gate([self.initial_output_gate, cur_outgate])
    temp_and_output_gate = self.gates_generator.output_gate

    # Adding restriction position gate to if condition if enabled:
    if (self.parsed.num_positions != int(math.pow(2, self.num_position_variables)) and self.parsed.args.restricted_position_constraints == 1):
      self.encoding.append(['# If condition with position restriction : '])
      self.gates_generator.if_then_gate(self.restricted_positions_gate, temp_and_output_gate)
      self.final_output_gate = self.gates_generator.output_gate
    else:
      self.final_output_gate = temp_and_output_gate


  def __init__(self, parsed):
    self.parsed = parsed
    self.encoding_variables = vd()
    self.quantifier_block = []
    self.dqdimacs_prefix = []
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
    self.indicator_variables = []
    for i in range(parsed.depth):
      self.move_variables.append(self.encoding_variables.get_vars(self.num_move_variables))
      # we use indicator variables for white illegal moves:
      if i%2 == 0:
        self.indicator_variables.append([])
      else:
        self.indicator_variables.append(self.encoding_variables.get_vars(2))

    if (parsed.args.debug == 1):
      print("Number of (log) move variables: ", self.num_move_variables)
      print("Move variables: ",self.move_variables)
      print("Indicator variables: ", self.indicator_variables)


    # Allocating reachable variables for the goal:
    self.reachable_variables = self.encoding_variables.get_vars(parsed.num_positions)

    if (parsed.args.debug == 1):
      print("reachable variables: ",self.reachable_variables)
      #print("Neighbour variables: ", self.neighbour_variables)


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


    # One neighbour is sufficeint for path based:
    #self.neighbour = self.encoding_variables.get_vars(self.num_position_variables)



    # Generating quantifer blocks:
    self.generate_quantifier_blocks()


    #self.gates_generator = ggen(self.encoding_variables, self.encoding)

    if (self.parsed.args.sort_internal_gates == 0):
      self.gates_generator = ggen(self.encoding_variables, self.encoding)
    else:
      self.gates_generator = uggen(self.encoding_variables, self.encoding)

    # Generating d steps i.e., which includes black and white constraints:
    self.generate_d_transitions()

    self.generate_initial_gate()

    self.generate_goal_gate()

    # Note: Improved version needs to change this with only open positions:
    self.generate_restricted_black_moves()

    if (self.parsed.num_positions != int(math.pow(2, self.num_position_variables)) and self.parsed.args.restricted_position_constraints == 1):
      self.restricted_positions_gate = 0 # Can never be 0
      # positions combinations to be restricted:
      self.encoding.append(['#Position combinations restricted :'])
      lsc.add_circuit(self.gates_generator, self.forall_position_variables, self.parsed.num_positions)
      self.restricted_positions_gate = self.gates_generator.output_gate

    self.generate_nested_final_gate()
