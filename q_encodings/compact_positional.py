# Irfansha Shaik, 11.01.2022, Aarhus.


import math

import utils.lessthen_cir as lsc
from utils.gates import GatesGen as ggen
from utils.variables_dispatcher import VarDispatcher as vd


class CompactPositonal:

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

    # witness variables:
    self.quantifier_block.append(['# witness variables: '])
    all_goal_vars = []
    for vars in self.witness_variables:
      all_goal_vars.extend(vars)
    self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in all_goal_vars) + ')'])


  def __init__(self, parsed):
    self.parsed = parsed
    self.encoding_variables = vd()
    self.quantifier_block = []
    self.encoding = []
    self.step_output_gates = []
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


    # Allocating path variables for the goal,
    # For now assuming the empty board:
    self.witness_variables = []
    self.safe_max_path_length = int((self.parsed.depth + 1)/2)

    for i in range(self.safe_max_path_length):
      self.witness_variables.append(self.encoding_variables.get_vars(self.num_move_variables))



    if (parsed.args.debug == 1):
      print("Goal state variables: ",self.witness_variables)


    # Generating quantifer blocks:
    self.generate_quantifier_blocks()

    self.gates_generator = ggen(self.encoding_variables, self.encoding)


    # Black cannot overwrite white moves:

    # Iterating through all the black moves:
    self.encoding.append(['# Black does not overwrite the white moves : '])
    for i in range(self.parsed.depth):
      if (i%2 == 0):
        # Iterating through all the white moves:
        for j in range(i):
          if (j%2 == 1):
            self.gates_generator.complete_equality_gate(self.move_variables[i], self.move_variables[j])
            # Black moves cannot be equal to white, so negative:
            self.step_output_gates.append(-self.gates_generator.output_gate)

    # Positions in the witness must be among the black moves:

    # Iterating through each witness position:
    self.encoding.append(['# Witness positions can only have the black moves : '])
    for i in range(self.safe_max_path_length):
      step_disjunction_output_gates = []
      # Iterating through the black moves:
      for j in range(self.parsed.depth):
        if (j%2 == 0):
          self.gates_generator.complete_equality_gate(self.witness_variables[i], self.move_variables[j])
          step_disjunction_output_gates.append(self.gates_generator.output_gate)
      # One of the equality must be true:
      self.gates_generator.or_gate(step_disjunction_output_gates)
      self.step_output_gates.append(self.gates_generator.output_gate)

    # The witness must make a path:
    # Start boarder:
    start_border_output_gates = []
    for pos in self.parsed.start_boarder:
      binary_format_clause = self.generate_binary_format(self.witness_variables[0],pos)
      self.gates_generator.and_gate(binary_format_clause)
      start_border_output_gates.append(self.gates_generator.output_gate)

    self.encoding.append(['# disjunction of all start boarder positions : '])
    self.gates_generator.or_gate(start_border_output_gates)
    self.step_output_gates.append(self.gates_generator.output_gate)

    # Connections with nieghbour information:
    # Iterate through witness positions:
    for index in range(self.safe_max_path_length-1):
      cur_position = self.witness_variables[index]
      next_position = self.witness_variables[index+1]

      # Now specifying the implication for each pair:
      # iterating through each possible position value:
      for i in range(self.parsed.num_available_moves):
        self.encoding.append(['# position clauses: '])
        binary_format_clause = self.generate_binary_format(cur_position,i)
        self.gates_generator.and_gate(binary_format_clause)
        if_condition_output_gate = self.gates_generator.output_gate
        neighbour_output_gates = []
        self.encoding.append(['# neighbour clauses: '])

        # we only need to generate if the position is not an end boader node:
        if (i not in self.parsed.end_boarder):
          # For each neighbour we generate a clause:
          for cur_neighbour in self.parsed.neighbour_dict[i]:
            # We only generate the neighbour clauses if there are tight neighbours when the pruning is on:
            if (self.parsed.args.tight_neighbour_pruning == 1 and (i,cur_neighbour) not in self.parsed.tight_neighbour_pairs_list[index]):
              continue
            else:
              temp_binary_format_clause = self.generate_binary_format(next_position,cur_neighbour)
              self.gates_generator.and_gate(temp_binary_format_clause)
              neighbour_output_gates.append(self.gates_generator.output_gate)


        # We only add stuttering for end border nodes, or when the current node has no nieghbours and pruning is level 1:
        if (i in self.parsed.end_boarder or (self.parsed.args.tight_neighbour_pruning == 1 and len(neighbour_output_gates) == 0)):
          # For allowing shorter paths, we say the position is also its neighbour:
          temp_binary_format_clause = self.generate_binary_format(next_position,i)
          self.gates_generator.and_gate(temp_binary_format_clause)
          neighbour_output_gates.append(self.gates_generator.output_gate)

        # One of the values must be true, so a disjunction:
        self.gates_generator.or_gate(neighbour_output_gates)

        # If then clause for the neighbour implication:
        self.encoding.append(['# if then clause : '])
        self.gates_generator.if_then_gate(if_condition_output_gate,self.gates_generator.output_gate)
        self.step_output_gates.append(self.gates_generator.output_gate)

    # Allowing stuttering, if P_i = P_{i+1} then P_{i+1} = P_{i+2}:
    # if using tight pruning the stuttering starts from the beginning:
    if (self.parsed.args.tight_neighbour_pruning == 1):
      for i in range(self.safe_max_path_length-2):
        #for i in range(self.safe_max_path_length-2):
        # First equality:
        self.gates_generator.complete_equality_gate(self.witness_variables[i], self.witness_variables[i+1])
        first_equality_output_gate = self.gates_generator.output_gate

        # Second equality:
        self.gates_generator.complete_equality_gate(self.witness_variables[i+1], self.witness_variables[i+2])
        second_equality_output_gate = self.gates_generator.output_gate

        # Now the implication:
        self.gates_generator.if_then_gate(first_equality_output_gate, second_equality_output_gate)
        self.step_output_gates.append(self.gates_generator.output_gate)

    # End boarder:
    end_border_output_gates = []
    self.encoding.append(['# End boarder clauses : '])
    # Specifying the end borders:
    for pos in self.parsed.end_boarder:
      binary_format_clause = self.generate_binary_format(self.witness_variables[-1],pos)
      self.gates_generator.and_gate(binary_format_clause)
      end_border_output_gates.append(self.gates_generator.output_gate)

    self.encoding.append(['# disjunction of all end boarder positions : '])
    self.gates_generator.or_gate(end_border_output_gates)
    self.step_output_gates.append(self.gates_generator.output_gate)


    # Black restrictions as option:
    if (self.parsed.num_available_moves != int(math.pow(2, self.num_move_variables)) and self.parsed.args.black_move_restrictions == 1):
      self.encoding.append(['# Restricted black moves: '])
      for i in range(self.parsed.depth):
        if (i%2 == 0):
          # restricting more moves:
          lsc.add_circuit(self.gates_generator, self.move_variables[i], self.parsed.num_available_moves)
          # Can be added directly to the step output gates:
          self.step_output_gates.append(self.gates_generator.output_gate)

    # Final conjunction:
    self.encoding.append(['# Final conjunction gate : '])
    self.gates_generator.and_gate(self.step_output_gates)
    self.final_output_gate = self.gates_generator.output_gate
