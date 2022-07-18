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

    # black cannot overwrite as black option, if disabled:
    if (parsed.args.black_overwriting_black_enable == 0):
      self.encoding.append(['# Black does not overwrite the black moves : '])
      for i in range(self.parsed.depth):
        if (i%2 == 0):
          # Iterating through all the black moves:
          for j in range(i):
            if (j%2 == 0):
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
    if (self.parsed.args.tight_neighbour_pruning == 0):
      # Start boarder:
      # if no tight neighbour pruning, we add disjunction of all the start boarder nodes:
      start_border_output_gates = []
      for pos in self.parsed.start_boarder:
        binary_format_clause = self.generate_binary_format(self.witness_variables[0],pos)
        self.gates_generator.and_gate(binary_format_clause)
        start_border_output_gates.append(self.gates_generator.output_gate)

      self.encoding.append(['# disjunction of all start boarder positions : '])
      self.gates_generator.or_gate(start_border_output_gates)
      self.step_output_gates.append(self.gates_generator.output_gate)

    else:
      # If unreachability is not computed then some of the start boarder nodes can be unreachable,
      # so we add the disjunction only for the reachable start nodes:
      reachable_start_nodes = []
      for pos in self.parsed.start_boarder:
       connected_neighbours = []
       for cur_neighbour in self.parsed.neighbour_dict[pos]:
        # We check if the start boarder node have any edges:
        if ((pos,cur_neighbour) not in self.parsed.tight_neighbour_pairs_list[0]):
          continue
        else:
          connected_neighbours.append(cur_neighbour)
        if (len(connected_neighbours) != 0):
          reachable_start_nodes.append(pos)
      # only using reachable start nodes:
      start_border_output_gates = []
      for pos in reachable_start_nodes:
        binary_format_clause = self.generate_binary_format(self.witness_variables[0],pos)
        self.gates_generator.and_gate(binary_format_clause)
        if (self.gates_generator.output_gate not in start_border_output_gates):
          start_border_output_gates.append(self.gates_generator.output_gate)

      self.encoding.append(['# disjunction of all reachable start boarder positions : '])
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

        # when no tight neighbour pruning:
        #====================================================================================================

        if (self.parsed.args.tight_neighbour_pruning == 0):
          # if the position is end border we add a self loop and stop:
          if (i in self.parsed.end_boarder):
            # For allowing shorter paths, we say the position is also its neighbour:
            temp_binary_format_clause = self.generate_binary_format(next_position,i)
            self.gates_generator.and_gate(temp_binary_format_clause)
            neighbour_output_gates.append(self.gates_generator.output_gate)
          # if the position is not an end boarder node, we add all its nieghbours:
          else:
            # For each neighbour we generate a clause:
            for cur_neighbour in self.parsed.neighbour_dict[i]:
              temp_binary_format_clause = self.generate_binary_format(next_position,cur_neighbour)
              self.gates_generator.and_gate(temp_binary_format_clause)
              neighbour_output_gates.append(self.gates_generator.output_gate)

        #====================================================================================================
        # when tight neighbour pruning:
        #====================================================================================================
        else:
          # if end boarder node we do not do anything:
          if (i in self.parsed.end_boarder):
            continue
          else:
            # For each neighbour we generate a clause:
            for cur_neighbour in self.parsed.neighbour_dict[i]:
              # We only generate the neighbour clauses if there are tight neighbours when the pruning is on:
              if ((i,cur_neighbour) not in self.parsed.tight_neighbour_pairs_list[index]):
                continue
              else:
                # if the neighbour is an end boarder node then we connect to the last witness position:
                if (cur_neighbour in self.parsed.end_boarder):
                  # if the neighbour is not an end boarder node then we connect to the next witness position:
                  temp_binary_format_clause = self.generate_binary_format(self.witness_variables[-1],cur_neighbour)
                  self.gates_generator.and_gate(temp_binary_format_clause)
                  neighbour_output_gates.append(self.gates_generator.output_gate)
                else:
                  # if the neighbour is not an end boarder node then we connect to the next witness position:
                  temp_binary_format_clause = self.generate_binary_format(next_position,cur_neighbour)
                  self.gates_generator.and_gate(temp_binary_format_clause)
                  neighbour_output_gates.append(self.gates_generator.output_gate)
        #====================================================================================================

        # if the neighbour output gates are empty, we do not need an implication
        if (len(neighbour_output_gates) == 0):
          continue

        # One of the values must be true, so a disjunction:
        if (len(neighbour_output_gates) > 1):
          self.gates_generator.or_gate(neighbour_output_gates)


        # If then clause for the neighbour implication:
        self.encoding.append(['# if then clause : '])
        self.gates_generator.if_then_gate(if_condition_output_gate,self.gates_generator.output_gate)
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

    # Adding unreachable start end clauses when tight neighbour pruning is computed:
    if (self.parsed.args.e == 'cp' and self.parsed.args.tight_neighbour_pruning == 1):
      self.encoding.append(['# unreachable start and end pairs : '])
      for pair in self.parsed.unreachable_start_end_pairs:
        assert(len(pair) == 2)
        start_binary_format_clause = self.generate_binary_format(self.witness_variables[0],pair[0])
        self.gates_generator.and_gate(start_binary_format_clause)
        start_gate = self.gates_generator.output_gate

        end_binary_format_clause = self.generate_binary_format(self.witness_variables[-1],pair[1])
        self.gates_generator.and_gate(end_binary_format_clause)
        end_gate = self.gates_generator.output_gate

        # exclusive clause with unreachable start and end pairs:
        self.gates_generator.or_gate([-start_gate, -end_gate])
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
