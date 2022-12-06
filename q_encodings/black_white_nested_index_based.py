# Irfansha Shaik, 16.11.2022, Aarhus.

import math

import utils.adder_cir as addc
import utils.lessthen_cir as lsc
from utils.gates import GatesGen as ggen
from utils.unique_gates import GatesGen as uggen
from utils.variables_dispatcher import VarDispatcher as vd


class BlackWhiteNestedIndexBased:

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
    f.close()

  # takes a list of ints and returns string from of list for printing:
  def make_string(self,lst):
    return "[" + ",".join(str(x) for x in lst) + "]"


  # for visual testing, we need bounds, actions and necessary variables
  # prints to a file:
  def print_meta_data_tofile(self):
    # remembering required certificate output variables:
    sat_cert_vars = []
    unsat_cert_vars = []
    f_meta = open(self.parsed.args.viz_meta_data_out,"w")
    # input information:
    f_meta.write("#boardsize\n")
    f_meta.write(str(self.parsed.xmax) + " " + str(self.parsed.ymax) + "\n")
    f_meta.write("#depth\n")
    f_meta.write(str(self.parsed.depth) + "\n")
    # we need action names to choose for testing:
    f_meta.write("#blackactions\n")
    for action in self.parsed.black_action_list:
      f_meta.write(action.action_name + "("+ ",".join(action.parameters)+")\n")
    f_meta.write("#whiteactions\n")
    for action in self.parsed.white_action_list:
      f_meta.write(action.action_name + "("+ ",".join(action.parameters)+")\n")
    # variables:
    f_meta.write("#actionvars\n")
    # writing the move variables, action and parameter variables (separating accordingly):
    for i in range(self.parsed.depth):
      f_meta.write(self.make_string(self.move_variables[i][0]) + " " + self.make_string(self.move_variables[i][1]) + " " + self.make_string(self.move_variables[i][2]) + "\n")
      # appending vars:
      if (i % 2 == 0):
        sat_cert_vars.extend(self.move_variables[i][0])
        sat_cert_vars.extend(self.move_variables[i][1])
        sat_cert_vars.extend(self.move_variables[i][2])
      else:
        unsat_cert_vars.extend(self.move_variables[i][0])
        unsat_cert_vars.extend(self.move_variables[i][1])
        unsat_cert_vars.extend(self.move_variables[i][2])
    # symbolic position vars:
    f_meta.write("#symbolicpos\n")
    f_meta.write(self.make_string(self.forall_position_variables[0]) + " " + self.make_string(self.forall_position_variables[1]) + "\n")
    # state vars:
    f_meta.write("#statevars\n")
    for i in range(self.parsed.depth+1):
      f_meta.write(" ".join(str(x) for x in self.predicate_variables[i]) + "\n")
      sat_cert_vars.extend(self.predicate_variables[i])
    # state vars:
    f_meta.write("#goalvar\n")
    f_meta.write(str(self.goal_output_gate) + "\n")
    f_meta.close()

    # generating string:
    self.output_sat_index_string += ",".join(str(x) for x in sat_cert_vars)
    #print(self.output_index_string)
    self.output_unsat_index_string += ",".join(str(x) for x in unsat_cert_vars)

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

  def generate_index_constraint(self, x_variables, y_variables, index_constraint):
    bound = int(index_constraint.split(",")[-1].strip(")"))
    if ('?x' in index_constraint):
      #print(bound, self.upperlimit_xmax)
      # we do not need explicit bound for the upperlimit_xmax bounds:
      if (bound != self.upperlimit_xmax):
        lsc.add_circuit(self.gates_generator, x_variables, bound)
        return self.gates_generator.output_gate
      else:
        # sending "None" to handle the bounds properly:
        return "None"
    else:
      #print(bound, self.upperlimit_ymax)
      assert('?y' in index_constraint)
      assert('?x' not in index_constraint)
      if (bound != self.upperlimit_ymax):
        lsc.add_circuit(self.gates_generator, y_variables, bound)
        return self.gates_generator.output_gate
      else:
        # sending "None" to handle the bounds properly:
        return "None"

  def generate_counter_index_constraint(self, variables, constraint_pair):
    self.encoding.append(['# computing counter bounds for constraints,' + str(constraint_pair) +' :'])
    assert("?c" in constraint_pair[0])
    # if lessthan bound is max counter and powers of 2, we use lessthan-and-equal to:
    if (self.parsed.counter_bound == int(constraint_pair[1]) and int(constraint_pair[1]) == math.pow(self.num_counter_vars,2)):
      lsc.add_circuit(self.gates_generator, variables, int(constraint_pair[1])-1)
      lessthan_output_gate = self.gates_generator.output_gate
      # equal-to gate with num-1:
      binary_format_gates = self.generate_binary_format(variables,int(constraint_pair[1])-1)
      self.gates_generator.and_gate(binary_format_gates)
      binary_output_gate = self.gates_generator.output_gate
      # disjunction will be lessthan-or-equal circuit:
      self.gates_generator.or_gate([lessthan_output_gate,binary_output_gate])
    else:
      lsc.add_circuit(self.gates_generator, variables, int(constraint_pair[1]))
    return self.gates_generator.output_gate

  # returns, equality gates with forall variables for both x and y indexes (after computing addition and subtraciton where necessary):
  # we reduces both indexes by 1, so that indexes are consistent:
  def generate_position_equalities_with_adder_and_subtractors(self, x_variables, y_variables, constraint):
    #assert("?x" in constraint[0])
    #assert("?y" in constraint[1])
    # after add/sub we use these lists for remembering:
    result_x_variables = []
    result_y_variables = []
    self.encoding.append(['# computing x variables for constraints,' + str(constraint) +' add/sub/none:'])
    # first computing x variables:
    if ('+' in constraint[0]):
      split_x_constraint = constraint[0].split("+")
      assert("?x" == split_x_constraint[0])
      num_to_add = int(split_x_constraint[1])
      self.encoding.append(['# adder circuit'])
      result_x_variables = addc.adder_circuit(self.gates_generator,x_variables,num_to_add)
    elif ('-' in constraint[0]):
      split_x_constraint = constraint[0].split("-")
      assert("?x" == split_x_constraint[0])
      num_to_sub = int(split_x_constraint[1])
      self.encoding.append(['# subtractor circuit'])
      result_x_variables = addc.subtractor_circuit(self.gates_generator,x_variables,num_to_sub)
    elif ('?x' in constraint[0]):
      result_x_variables = x_variables
    # we allow counter to be an index, assuming that x_variables are simply counter variables:
    elif('?c' in constraint[1]):
      result_x_variables = x_variables
    else:
      x_value = int(constraint[0]) - 1
    self.encoding.append(['# computing y variables for constraints,' + str(constraint) +' add/sub/none:'])
    # now computing y variables:
    if ('+' in constraint[1]):
      split_y_constraint = constraint[1].split("+")
      assert("?y" == split_y_constraint[0])
      num_to_add = int(split_y_constraint[1])
      self.encoding.append(['# adder circuit'])
      result_y_variables = addc.adder_circuit(self.gates_generator,y_variables,num_to_add)
    elif ('-' in constraint[1]):
      split_y_constraint = constraint[1].split("-")
      assert("?y" == split_y_constraint[0])
      num_to_sub = int(split_y_constraint[1])
      self.encoding.append(['# subtractor circuit'])
      result_y_variables = addc.subtractor_circuit(self.gates_generator,y_variables,num_to_sub)
    elif('?y' in constraint[1]):
      result_y_variables = y_variables
    # we allow counter to be an index, assuming that y_variables are simply counter variables:
    elif('?c' in constraint[1]):
      result_y_variables = y_variables
    else:
      y_value = int(constraint[1]) - 1

    # we also handle if the parameter is a constant:
    if ("?x" in constraint[0] or "?c" in constraint[0]):
      # computing equality constraints with forall variables:
      # generating constraint for new x, which is equality with x parameter of forall variables:
      self.encoding.append(['# new x constraint equality gate with forall x variables: '])
      self.gates_generator.complete_equality_gate(result_x_variables,self.forall_position_variables[0])
      x_output_gate = self.gates_generator.output_gate
    else:
      # generating binary format for the x constraint:
      self.encoding.append(['# x constraint binary format with forall x variables: '])
      x_constraint_binary_format = self.generate_binary_format(self.forall_position_variables[0], x_value)
      self.gates_generator.and_gate(x_constraint_binary_format)
      x_output_gate = self.gates_generator.output_gate

    if ("?y" in constraint[1] or "?c" in constraint[1]):
      # generating constraint for new y, which is equality with y parameter of forall variables:
      self.encoding.append(['# new y constraint equality gate with forall y variables: '])
      self.gates_generator.complete_equality_gate(result_y_variables,self.forall_position_variables[1])
      y_output_gate = self.gates_generator.output_gate
    else:
      # generating binary format for the y constraint:
      self.encoding.append(['# y constraint binary format with forall y variables: '])
      y_constraint_binary_format = self.generate_binary_format(self.forall_position_variables[1],y_value)
      self.gates_generator.and_gate(y_constraint_binary_format)
      y_output_gate = self.gates_generator.output_gate

    # conjunction of both equallity gates:
    self.gates_generator.and_gate([x_output_gate, y_output_gate])
    return self.gates_generator.output_gate

  # takes time step and generates equalities with forall variables only for ?x and ?y variables if available,
  # returns equality output gate:
  def generate_counter_forall_equality_gate(self,time_step):
    # computing equality output gates:
    counter_equality_gates = []
    if (self.parsed.x_flag == 1):
      self.gates_generator.complete_equality_gate(self.move_variables[time_step][1], self.forall_position_variables[0])
      counter_equality_gates.append(self.gates_generator.output_gate)
    else:
      assert(len(self.move_variables[time_step][1]) == 0)
    if (self.parsed.y_flag == 1):
      self.gates_generator.complete_equality_gate(self.move_variables[time_step][2], self.forall_position_variables[1])
      counter_equality_gates.append(self.gates_generator.output_gate)
    else:
      assert(len(self.move_variables[time_step][2]) == 0)
    # if there is counter then atleast one of the variables are presented:
    assert(len(counter_equality_gates) != 0)
    self.gates_generator.and_gate(counter_equality_gates)
    return self.gates_generator.output_gate

  # takes equality output gate with forall variables and a predicate to generate if-then constraint depending on the sign:
  def generate_if_then_predicate_constraint(self, if_condition_gate, predicate, time_step, constraint_sign):
    if (predicate == 'black'):
      # if the predicate is black then we set the cur predicate variable to black:
      self.gates_generator.and_gate([self.predicate_variables[time_step][0], -self.predicate_variables[time_step][1]])
      # if then constraint:
      self.encoding.append(['# if then constraint for black predicate:'])
    elif (predicate == 'white'):
      # if the predicate is white then we set the cur predicate variable to white:
      self.gates_generator.and_gate([self.predicate_variables[time_step][0], self.predicate_variables[time_step][1]])
      # if then constraint:
      self.encoding.append(['# if then constraint for white predicate:'])
    else:
      assert(predicate == 'open')
      # if the predicate is open then we set the cur predicate variable to open:
      self.gates_generator.and_gate([-self.predicate_variables[time_step][0]])

    # if positive constraint we generate if then, else we generate if not then gate:
    if (constraint_sign == 'pos'):
      self.gates_generator.if_then_gate(if_condition_gate, self.gates_generator.output_gate)
    else:
      assert(constraint_sign == "neg")
      self.gates_generator.if_then_gate(if_condition_gate, -self.gates_generator.output_gate)

    return self.gates_generator.output_gate

  # takes a predicate to generate then constraint depending on the sign:
  def generate_then_predicate_constraint(self, predicate, time_step, constraint_sign):
    if (predicate == 'black'):
      # if the predicate is black then we set the cur predicate variable to black:
      self.gates_generator.and_gate([self.predicate_variables[time_step][0], -self.predicate_variables[time_step][1]])
      # if then constraint:
      self.encoding.append(['# if then constraint for black predicate:'])
    elif (predicate == 'white'):
      # if the predicate is white then we set the cur predicate variable to white:
      self.gates_generator.and_gate([self.predicate_variables[time_step][0], self.predicate_variables[time_step][1]])
      # if then constraint:
      self.encoding.append(['# if then constraint for white predicate:'])
    else:
      assert(predicate == 'open')
      # if the predicate is open then we set the cur predicate variable to open:
      self.gates_generator.and_gate([-self.predicate_variables[time_step][0]])

    # if positive constraint we generate if then, else we generate if not then gate:
    if (constraint_sign == 'pos'):
      return self.gates_generator.output_gate
    else:
      assert(constraint_sign == "neg")
      return -self.gates_generator.output_gate


  # Generates quanifier blocks:
  def generate_quantifier_blocks(self):

    # Move variables following time variables:
    self.quantifier_block.append(['# ' + str(self.num_black_action_variables) + '/' + str(self.num_white_action_variables) + ' (black/white) Action variables, ' + str(self.num_x_index_variables) + ' and ' + str(self.num_y_index_variables) +  ' (action parameter) index variables (x, y), and game stop variables : '])
    for i in range(self.parsed.depth):
      # starts with 0 and even is black (i.e., existential moves):
      if (i % 2 == 0):
        cur_all_action_vars = []
        # adding action variables:
        cur_all_action_vars.extend(self.move_variables[i][0])
        # adding parameter variables:
        cur_all_action_vars.extend(self.move_variables[i][1])
        cur_all_action_vars.extend(self.move_variables[i][2])

        # adding game stop variable if present:
        cur_all_action_vars.extend(self.move_variables[i][3])
        self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in cur_all_action_vars) + ')'])
      else:

        cur_all_action_vars = []
        # adding action variables:
        exists_action_vars = []
        # if number of actions/moves are only 1, we make it existential:
        if (self.num_white_actions == 1):
          exists_action_vars.extend(self.move_variables[i][0])

        else:
          cur_all_action_vars.extend(self.move_variables[i][0])
        # adding parameter variables:
        if (self.xmax == 1):
          exists_action_vars.extend(self.move_variables[i][1])
        else:
          cur_all_action_vars.extend(self.move_variables[i][1])

        if (self.ymax == 1):
          exists_action_vars.extend(self.move_variables[i][2])
        else:
          cur_all_action_vars.extend(self.move_variables[i][2])

        # if maker-maker, we include white-gamestop in universal variables:
        if(self.makermaker_game == 1):
          cur_all_action_vars.extend(self.move_variables[i][5])


        if(len(exists_action_vars) !=0):
          self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in exists_action_vars) + ')'])
        assert(len(cur_all_action_vars) !=0)
        self.quantifier_block.append(['forall(' + ', '.join(str(x) for x in cur_all_action_vars) + ')'])
        # if illegal move is present, then it is existential:
        if (len(self.move_variables[i][3]) != 0):
          self.quantifier_block.append(['# white illegal variable: '])
          self.quantifier_block.append(['exists(' + str(self.move_variables[i][3][0]) + ')'])
        # the extra boolean variables are also existential:
        self.quantifier_block.append(['# indicator variables, specifying which position is voilated in illegal move: '])
        self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in self.move_variables[i][4]) + ')'])


    if (self.num_black_goal_constraints > 1):
      self.quantifier_block.append(['# black goal choice variables: '])
      self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in self.disjunction_goal_boolean_variables) + ')'])


    # black goal variables:
    self.quantifier_block.append(['# black goal index variables: '])
    all_black_goal_vars = []
    all_black_goal_vars.extend(self.black_goal_index_variables[0])
    all_black_goal_vars.extend(self.black_goal_index_variables[1])
    if (len(all_black_goal_vars) > 0):
      self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in all_black_goal_vars) + ')'])

    # white goal variables, first forall variables from x,y and conjunction choosing variables:
    all_forall_white_goal_vars = []
    self.quantifier_block.append(['# white goal index and conjunction variables: '])
    # index variables:
    all_forall_white_goal_vars.extend(self.white_goal_index_variables[0])
    all_forall_white_goal_vars.extend(self.white_goal_index_variables[1])
    # choosing conjunction variables:
    if (self.num_white_goal_constraints > 1):
      all_forall_white_goal_vars.extend(self.forall_conjunction_white_goal_boolean_variables)
    if (len(all_forall_white_goal_vars) > 0):
      self.quantifier_block.append(['forall(' + ', '.join(str(x) for x in all_forall_white_goal_vars) + ')'])

    # existential choosing variables,
    # if we have a quantifier alternation, then there must be the disjunct variables:
    if (self.extra_white_quantifier_alternation == 1):
      self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in self.single_white_goal_disjunct_boolean_variables) + ')'])


    # Forall position variables:
    # if forced to single then existential:
    exists_index_variables = []

    forall_index_variables = []
    if (self.xmax == 1):
      exists_index_variables.extend(self.forall_position_variables[0])
    else:
      forall_index_variables.extend(self.forall_position_variables[0])

    if(self.ymax == 1):
      exists_index_variables.extend(self.forall_position_variables[1])
    else:
      forall_index_variables.extend(self.forall_position_variables[1])

    if(len(exists_index_variables) !=0):
      self.quantifier_block.append(['# exists symbolic index variables: '])
      self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in exists_index_variables) + ')'])
    assert(len(forall_index_variables)!=0)
    self.quantifier_block.append(['# Forall index variables: '])
    self.quantifier_block.append(['forall(' + ', '.join(str(x) for x in forall_index_variables) + ')'])


    # if counter is available:
    # TODO: can be moved to one level up, might be efficient:
    if (self.parsed.counter_flag == 1):
      self.quantifier_block.append(['# Counter variables: '])
      for i in range(self.parsed.depth+1):
        self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in self.counter_variables[i]) + ')'])


    # Finally predicate variables for each time step:
    self.quantifier_block.append(['# Predicate variables: '])
    for i in range(self.parsed.depth+1):
      self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in self.predicate_variables[i]) + ')'])

  def generate_black_transition(self, time_step):

    # Allowing local conjunction transition step gates for nested implications later:
    current_transition_step_output_gates = []

    self.encoding.append(['# Player 1 (black) transition function for time step ' + str(time_step)+ ': '])

    # If the number actions are not powers of 2, then we need a less than circuit:
    if (self.upperlimit_black_actions != self.num_black_actions):
      self.encoding.append(['# less than constraints for black moves:'])
      lsc.add_circuit(self.gates_generator, self.move_variables[time_step][0], self.num_black_actions)
      self.black_lessthan_circuit_output_gate = self.gates_generator.output_gate
      #self.transition_step_output_gates.append(self.gates_generator.output_gate)
      current_transition_step_output_gates.append(self.gates_generator.output_gate)


    # Propogation constraints:
    self.encoding.append(['# propagation constraints:'])
    self.gates_generator.complete_equality_gate(self.predicate_variables[time_step], self.predicate_variables[time_step+1])
    propagation_output_gate = self.gates_generator.output_gate

    '''
    # if game stop variable is true in previous black turn, then the state is simply propagated:
    if (time_step > 0):
      self.encoding.append(['# if then constraints for the propagation:'])
      # even single boolean for game stop variable is a list in our data structure:
      self.gates_generator.if_then_gate(self.move_variables[time_step - 2][3][0], propagation_output_gate)
      #self.transition_step_output_gates.append(self.gates_generator.output_gate)
      current_transition_step_output_gates.append(self.gates_generator.output_gate)
    '''

    # for each action we generate constraints:
    for i in range(self.num_black_actions):
      temp_if_condition_output_gates = []
      # generate binary constraint for current action index:
      binary_format_clause = self.generate_binary_format(self.move_variables[time_step][0],i)
      self.gates_generator.and_gate(binary_format_clause)
      '''
      # apparently just removing this redundant gates makes a huge difference:
      # XXX testcase for bloqqer preprocessing, huge difference in file sizes:
      temp_if_condition_output_gates.append(self.gates_generator.output_gate)
      # final if condition for current action:
      self.gates_generator.and_gate(temp_if_condition_output_gates)
      '''
      final_if_condition_output_gate = self.gates_generator.output_gate
      temp_then_constraint_output_gates = []
      # generate positive index bound constraints:
      for index_constraint in self.parsed.black_action_list[i].positive_indexbounds:
        # we only add bounds if variables are allocated:
        if (self.parsed.x_flag != 1 and "?x" in index_constraint):
          continue
        if (self.parsed.y_flag != 1 and "?y" in index_constraint):
          continue
        self.encoding.append(['# less than constraints for positive index bounds:'])
        # generating constraints for corresponding index variables:
        # no spaces for sake of correct parsing:
        assert(" " not in index_constraint)
        # passing x variables and y variables along with index constraint:
        bound_result = self.generate_index_constraint(self.move_variables[time_step][1], self.move_variables[time_step][2], index_constraint)
        #print(bound_result)
        if (bound_result != 'None'):
          temp_then_constraint_output_gates.append(bound_result)
        #print(self.parsed.black_action_list[i],index_constraint, bound)
      # generate negative index bound constraints:
      for index_constraint in self.parsed.black_action_list[i].negative_indexbounds:
        # we only add bounds if variables are allocated:
        if (self.parsed.x_flag != 1 and "?x" in index_constraint):
          continue
        if (self.parsed.y_flag != 1 and "?y" in index_constraint):
          continue
        self.encoding.append(['# less than constraints for negative index bounds:'])
        # generating constraints for corresponding index variables:
        # no spaces for sake of correct parsing:
        assert(" " not in index_constraint)
        # adding the negative output gate since we have negative index constraints:
        bound_result = self.generate_index_constraint(self.move_variables[time_step][1], self.move_variables[time_step][2], index_constraint)
        #print(bound_result)
        if (bound_result != 'None'):
          temp_then_constraint_output_gates.append(-bound_result)


      #print("not", index_constraint, bound)
      # gather positions used in precondition and effect constraints and generate equality gates with forall variables:
      # constraints for postive precondition:
      for precondition in self.parsed.black_action_list[i].positive_preconditions:
        # no spaces for sake of correct parsing:
        assert(" " not in precondition)
        split_precondition = precondition.strip(")").split("(")
        predicate = split_precondition[0]
        constraint_pair = split_precondition[1].split(",")
        # if we have counter bound index, we compute it directly:
        if ("lt" in predicate and "?c" in constraint_pair):
          self.encoding.append(['# counter bound constraints with ' + str(constraint_pair[1]) + ":"])
          bound_result = self.generate_counter_index_constraint(self.counter_variables[time_step], constraint_pair)

          # only when the x parameters are true then we imply the bound result:
          bound_branch_condition_gate = self.generate_counter_forall_equality_gate(time_step)
          self.gates_generator.if_then_gate(bound_branch_condition_gate,bound_result)
          temp_then_constraint_output_gates.append(self.gates_generator.output_gate)
        else:
          cur_equality_output_gate = self.generate_position_equalities_with_adder_and_subtractors(self.move_variables[time_step][1], self.move_variables[time_step][2], constraint_pair)
          temp_then_constraint_output_gates.append(self.generate_if_then_predicate_constraint(cur_equality_output_gate,predicate, time_step,"pos"))
      # constraints for negative precondition:
      for precondition in self.parsed.black_action_list[i].negative_preconditions:
        # no spaces for sake of correct parsing:
        assert(" " not in precondition)
        split_precondition = precondition.strip(")").split("(")
        predicate = split_precondition[0]
        constraint_pair = split_precondition[1].split(",")
        cur_equality_output_gate = self.generate_position_equalities_with_adder_and_subtractors(self.move_variables[time_step][1], self.move_variables[time_step][2], constraint_pair)
        temp_then_constraint_output_gates.append(self.generate_if_then_predicate_constraint(cur_equality_output_gate,predicate, time_step,"neg"))

      # remember effect positions, later for frame axioms:
      touched_position_output_gates = []

      # constraints for postive effects:
      for effect in self.parsed.black_action_list[i].positive_effects:
        # no spaces for sake of correct parsing:
        assert(" " not in effect)
        split_effect = effect.strip(")").split("(")
        predicate = split_effect[0]
        constraint_pair = split_effect[1].split(",")
        #print(predicate, constraint_pair)
        # for now we assume only increment exists:
        # we handle the increment function separately:
        if ("inc" == predicate):
          #print(predicate,constraint_pair)
          # if parameters are equal to forall variables, then we increment the counter in those branches:
          counter_forall_equality_gate = self.generate_counter_forall_equality_gate(time_step)
          # first incrementing current counter:
          self.encoding.append(['# adder circuit for counter increment:'])
          increased_counter_variables = addc.adder_circuit(self.gates_generator,self.counter_variables[time_step],int(constraint_pair[1]))
          # complete equality with next time step counter variables, i.e., increasing counter:
          self.gates_generator.complete_equality_gate(self.counter_variables[time_step+1], increased_counter_variables)
          counter_increased_equality_gate = self.gates_generator.output_gate
          # implying the counter increased gate with counter forall equality gate:
          self.gates_generator.if_then_gate(counter_forall_equality_gate,counter_increased_equality_gate)
          temp_then_constraint_output_gates.append(self.gates_generator.output_gate)

          # we also propagate for all the other branches,
          # since we only have function once, it is easier to do it:
          # first equality gate for counter variables:
          self.gates_generator.complete_equality_gate(self.counter_variables[time_step],self.counter_variables[time_step+1])
          self.gates_generator.if_then_gate(-counter_forall_equality_gate, self.gates_generator.output_gate)
          temp_then_constraint_output_gates.append(self.gates_generator.output_gate)
        else:
          if ("?c" == constraint_pair[0]):
            cur_equality_output_gate = self.generate_position_equalities_with_adder_and_subtractors(self.counter_variables[time_step], self.move_variables[time_step][2], constraint_pair)
          elif ("?c" == constraint_pair[1]):
            cur_equality_output_gate = self.generate_position_equalities_with_adder_and_subtractors(self.move_variables[time_step][1], self.counter_variables[time_step], constraint_pair)
          else:
            cur_equality_output_gate = self.generate_position_equalities_with_adder_and_subtractors(self.move_variables[time_step][1], self.move_variables[time_step][2], constraint_pair)
          touched_position_output_gates.append(cur_equality_output_gate)
          # time step + 1 because these are effects:
          temp_then_constraint_output_gates.append(self.generate_if_then_predicate_constraint(cur_equality_output_gate,predicate, time_step + 1,"pos"))
      # constraints for postive effects:
      for effect in self.parsed.black_action_list[i].negative_effects:
        # no spaces for sake of correct parsing:
        assert(" " not in effect)
        split_effect = effect.strip(")").split("(")
        predicate = split_effect[0]
        constraint_pair = split_effect[1].split(",")
        cur_equality_output_gate = self.generate_position_equalities_with_adder_and_subtractors(self.move_variables[time_step][1], self.move_variables[time_step][2], constraint_pair)
        touched_position_output_gates.append(cur_equality_output_gate)
        # time step + 1 because these are effects:
        temp_then_constraint_output_gates.append(self.generate_if_then_predicate_constraint(cur_equality_output_gate,predicate, time_step + 1,"neg"))

      # for the positions that are not in effects, the state is propogated:
      self.encoding.append(['# disjunction for all touched positions:'])
      self.gates_generator.or_gate(touched_position_output_gates)
      self.encoding.append(['# frame axiom; if not touched position, then it is propagated:'])
      # if not these positions we propogate:
      self.gates_generator.or_gate([self.gates_generator.output_gate,propagation_output_gate])
      temp_then_constraint_output_gates.append(self.gates_generator.output_gate)

      assert(len(temp_then_constraint_output_gates) != 0)
      # conjunction of all the then constraints:
      self.encoding.append(['# conjunction for all the then constraints:'])
      self.gates_generator.and_gate(temp_then_constraint_output_gates)
      # final if then condition for each action:
      self.encoding.append(['# final if then constraint for current action:'])
      self.gates_generator.if_then_gate(final_if_condition_output_gate, self.gates_generator.output_gate)
      #self.transition_step_output_gates.append(self.gates_generator.output_gate)
      current_transition_step_output_gates.append(self.gates_generator.output_gate)

    # only at the end, we set the conjunction to step output gate:
    self.gates_generator.and_gate(current_transition_step_output_gates)
    self.transition_step_output_gates.append(self.gates_generator.output_gate)

  def generate_white_transition(self, time_step):

    # Allowing local conjunction transition step gates for nested implications later:
    current_transition_step_output_gates = []

    self.encoding.append(['# Player 2 (white) transition function for time step ' + str(time_step)+ ': '])


    # bound boolean variable for the current move:
    # asserting there is only one variable:
    assert(len(self.move_variables[time_step][3]) == 1)
    cur_bound_boolean_var = self.move_variables[time_step][3][0]

    # current booelan variables for preconditions:
    # asserting the number of boolean variables are same as the maximum number of preconditions:
    assert(len(self.move_variables[time_step][4]) == self.parsed.max_white_preconditions)
    cur_precondition_boolean_variables = self.move_variables[time_step][4]


    # Propogation constraints:
    self.encoding.append(['# propagation constraints:'])
    self.gates_generator.complete_equality_gate(self.predicate_variables[time_step], self.predicate_variables[time_step+1])
    propagation_output_gate = self.gates_generator.output_gate

    #================================================================================================
    # less than action constraints:
    #================================================================================================

    bound_variable_output_gates = []

    # If the number actions are not powers of 2, then we need a less than circuit:
    if (self.upperlimit_white_actions != self.num_white_actions):
      self.encoding.append(['# less than constraints for white moves:'])
      lsc.add_circuit(self.gates_generator, self.move_variables[time_step][0], self.num_white_actions)
      self.white_lessthan_circuit_output_gate = self.gates_generator.output_gate
      bound_variable_output_gates.append(self.white_lessthan_circuit_output_gate)


    #================================================================================================
    # computing less than bounds for each action:
    #================================================================================================
    # compute the less than bounds, with aciton specific implication:
    # for each action we generate constraints:
    self.encoding.append(['# generating less than bounds for indexes:'])
    for i in range(self.num_white_actions):
      # generate binary constraint for current action index:
      binary_format_clause = self.generate_binary_format(self.move_variables[time_step][0],i)
      self.gates_generator.and_gate(binary_format_clause)
      cur_action_binary_output_gate = self.gates_generator.output_gate
      lessthan_constraint_output_gates = []
      # generate positive index bound constraints:
      for index_constraint in self.parsed.white_action_list[i].positive_indexbounds:
        # we only add bounds if variables are allocated:
        if (self.parsed.x_flag != 1 and "?x" in index_constraint):
          continue
        if (self.parsed.y_flag != 1 and "?y" in index_constraint):
          continue
        self.encoding.append(['# less than constraints for positive index bounds:'])
        # generating constraints for corresponding index variables:
        # no spaces for sake of correct parsing:
        assert(" " not in index_constraint)
        # passing x variables and y variables along with index constraint:
        bound_result = self.generate_index_constraint(self.move_variables[time_step][1], self.move_variables[time_step][2], index_constraint)
        #print(bound_result)
        if (bound_result != 'None'):
          lessthan_constraint_output_gates.append(bound_result)
      # generate negative index bound constraints:
      for index_constraint in self.parsed.white_action_list[i].negative_indexbounds:
        # we only add bounds if variables are allocated:
        if (self.parsed.x_flag != 1 and "?x" in index_constraint):
          continue
        if (self.parsed.y_flag != 1 and "?y" in index_constraint):
          continue
        self.encoding.append(['# less than constraints for negative index bounds:'])
        # generating constraints for corresponding index variables:
        # no spaces for sake of correct parsing:
        assert(" " not in index_constraint)
        # adding the negative output gate since we have negative index constraints:
        bound_result = self.generate_index_constraint(self.move_variables[time_step][1], self.move_variables[time_step][2], index_constraint)
        #print(bound_result)
        if (bound_result != 'None'):
          lessthan_constraint_output_gates.append(-bound_result)
      # conjunction of the less than constraints:
      self.gates_generator.and_gate(lessthan_constraint_output_gates)
      # only if there are any constraints, we make a implication:
      if (len(lessthan_constraint_output_gates) != 0):
        # if then constraint for the action and index bounds:
        self.gates_generator.if_then_gate(cur_action_binary_output_gate, self.gates_generator.output_gate)
        bound_variable_output_gates.append(self.gates_generator.output_gate)

    self.encoding.append(['# conjunction for all the bound constraints:'])
    # conjunction of the bound constraint output gates:
    assert(len(bound_variable_output_gates) != 0)
    self.gates_generator.and_gate(bound_variable_output_gates)
    final_bound_output_gate = self.gates_generator.output_gate

    #================================================================================================
    # connecting the index bounds with specific boolean variables:
    #================================================================================================
    self.encoding.append(['# single equality gate for the bound boolean variale and the final bound conjuction gate:'])
    # connect the bound variable with the index and action binary bound:
    self.gates_generator.single_equality_gate(cur_bound_boolean_var, final_bound_output_gate)
    #self.transition_step_output_gates.append(self.gates_generator.output_gate)
    current_transition_step_output_gates.append(self.gates_generator.output_gate)

    #'''
    #================================================================================================
    # computing and connecting the preconditions with boolean variables for each action:
    #================================================================================================

    self.encoding.append(['# generating precondition equalities with boolean variables:'])
    for i in range(self.num_white_actions):
      # generate binary constraint for current action index:
      binary_format_clause = self.generate_binary_format(self.move_variables[time_step][0],i)
      self.gates_generator.and_gate(binary_format_clause)
      cur_action_binary_output_gate = self.gates_generator.output_gate

      # asserting that current precondition boolean variables are present:
      assert(len(cur_precondition_boolean_variables) == self.parsed.max_white_preconditions)
      temp_precondition_boolean_variables = list(cur_precondition_boolean_variables)

      # constraints for postive precondition:
      for precondition in self.parsed.white_action_list[i].positive_preconditions:
        # no spaces for sake of correct parsing:
        assert(" " not in precondition)
        split_precondition = precondition.strip(")").split("(")
        predicate = split_precondition[0]
        constraint_pair = split_precondition[1].split(",")
        # if we have counter bound index, we compute it directly:
        if ("lt" in predicate and "?c" in constraint_pair):
          self.encoding.append(['# counter bound constraints:'])
          bound_result = self.generate_counter_index_constraint(self.counter_variables[time_step], constraint_pair)
          # if the branch is equality branch, then boolean variables must be same as then gate:
          # generate if then constraint with the precondition boolean variable:
          temp_cur_precondition_bool =  temp_precondition_boolean_variables.pop(0)
          # single equality gate between precondition var and bound:
          self.gates_generator.single_equality_gate(bound_result, temp_cur_precondition_bool)
          bool_equality_gate_counter = self.gates_generator.output_gate

          # computing equality output gates:
          cur_equality_output_gate = self.generate_counter_forall_equality_gate(time_step)
          # if then constraints, in the specific branch:
          self.gates_generator.or_gate([-cur_action_binary_output_gate,-cur_equality_output_gate, bool_equality_gate_counter])
          #self.transition_step_output_gates.append(self.gates_generator.output_gate)
          current_transition_step_output_gates.append(self.gates_generator.output_gate)
        else:
          cur_equality_output_gate = self.generate_position_equalities_with_adder_and_subtractors(self.move_variables[time_step][1], self.move_variables[time_step][2], constraint_pair)
          cur_precondition_pos_then_gate = self.generate_then_predicate_constraint(predicate, time_step,"pos")
          # if the branch is equality branch, then boolean variables must be same as then gate:
          # generate if then constraint with the precondition boolean variable:
          temp_cur_precondition_bool =  temp_precondition_boolean_variables.pop(0)
          # single equality gate between the bool and the output gate:
          self.gates_generator.single_equality_gate(cur_precondition_pos_then_gate, temp_cur_precondition_bool)
          # if then constraints, in the specific branch:
          self.gates_generator.or_gate([-cur_action_binary_output_gate,-cur_equality_output_gate, self.gates_generator.output_gate])
          #self.transition_step_output_gates.append(self.gates_generator.output_gate)
          current_transition_step_output_gates.append(self.gates_generator.output_gate)
      # constraints for negative precondition:
      for precondition in self.parsed.white_action_list[i].negative_preconditions:
        # no spaces for sake of correct parsing:
        assert(" " not in precondition)
        split_precondition = precondition.strip(")").split("(")
        predicate = split_precondition[0]
        constraint_pair = split_precondition[1].split(",")
        cur_equality_output_gate = self.generate_position_equalities_with_adder_and_subtractors(self.move_variables[time_step][1], self.move_variables[time_step][2], constraint_pair)
        cur_precondition_neg_then_gate = self.generate_then_predicate_constraint(predicate, time_step,"neg")
        # if the branch is equality branch, then boolean variables must be same as then gate:
        # generate if then constraint with the precondition boolean variable:
        temp_cur_precondition_bool =  temp_precondition_boolean_variables.pop(0)
        # single equality gate between the bool and the output gate:
        self.gates_generator.single_equality_gate(cur_precondition_neg_then_gate, temp_cur_precondition_bool)
        # if then constraints, in the specific branch:
        self.gates_generator.or_gate([-cur_action_binary_output_gate,-cur_equality_output_gate, self.gates_generator.output_gate])
        #self.transition_step_output_gates.append(self.gates_generator.output_gate)
        current_transition_step_output_gates.append(self.gates_generator.output_gate)
      # asserting that we use all the boolean vars, only for breakthrough/knightthrough:
      assert(len(temp_precondition_boolean_variables) == 0)

    #'''
    # compute the constraints for effects:
    #=================================================================================================================
    # computing and enforcing effects only when the bounds preconditions hold and game is not stopped for each action:
    #=================================================================================================================

    self.encoding.append(['# generating effects, implcation when the game is not stopped and bounds,preconditions hold:'])
    for i in range(self.num_white_actions):
      # generate binary constraint for current action index:
      binary_format_clause = self.generate_binary_format(self.move_variables[time_step][0],i)
      self.gates_generator.and_gate(binary_format_clause)
      cur_action_binary_output_gate = self.gates_generator.output_gate


      # generating conjunction of all the boolean variables to specify if the move is valid:
      all_valid_constraints = []
      all_valid_constraints.append(cur_bound_boolean_var)
      all_valid_constraints.extend(cur_precondition_boolean_variables)
      self.gates_generator.and_gate(all_valid_constraints)
      valid_move_output_gate = self.gates_generator.output_gate

      # remember effect positions, later for frame axioms:
      touched_position_output_gates = []

      then_constraint_output_gates = []

      # constraints for postive effects:
      for effect in self.parsed.white_action_list[i].positive_effects:
        # no spaces for sake of correct parsing:
        assert(" " not in effect)
        split_effect = effect.strip(")").split("(")
        predicate = split_effect[0]
        constraint_pair = split_effect[1].split(",")
        # for now we assume only increment exists:
        # we handle the increment function separately:
        if ("inc" == predicate):
          #print(predicate,constraint_pair)
          # if parameters are equal to forall variables, then we increment the counter in those branches:
          counter_forall_equality_gate = self.generate_counter_forall_equality_gate(time_step)
          # first incrementing current counter:
          self.encoding.append(['# adder circuit for counter increment:'])
          increased_counter_variables = addc.adder_circuit(self.gates_generator,self.counter_variables[time_step],int(constraint_pair[1]))
          # complete equality with next time step counter variables, i.e., increasing counter:
          self.encoding.append(['# equality gate for next counter vars and increased counter:'])
          self.gates_generator.complete_equality_gate(self.counter_variables[time_step+1], increased_counter_variables)
          counter_increased_equality_gate = self.gates_generator.output_gate
          # implying the counter increased gate with counter forall equality gate:
          self.encoding.append(['# if then gate for increased equality:'])
          self.gates_generator.if_then_gate(counter_forall_equality_gate,counter_increased_equality_gate)
          then_constraint_output_gates.append(self.gates_generator.output_gate)

          # we also propagate for all the other branches,
          # since we only have function once, it is easier to do it:
          # first equality gate for counter variables:
          self.encoding.append(['# counter propagation equality gate:'])
          self.gates_generator.complete_equality_gate(self.counter_variables[time_step],self.counter_variables[time_step+1])
          self.encoding.append(['# in all other branches we propagate counter:'])
          self.gates_generator.if_then_gate(-counter_forall_equality_gate, self.gates_generator.output_gate)
          then_constraint_output_gates.append(self.gates_generator.output_gate)
        else:
          if ("?c" == constraint_pair[0]):
            cur_equality_output_gate = self.generate_position_equalities_with_adder_and_subtractors(self.counter_variables[time_step], self.move_variables[time_step][2], constraint_pair)
          elif ("?c" == constraint_pair[1]):
            cur_equality_output_gate = self.generate_position_equalities_with_adder_and_subtractors(self.move_variables[time_step][1], self.counter_variables[time_step], constraint_pair)
          else:
            cur_equality_output_gate = self.generate_position_equalities_with_adder_and_subtractors(self.move_variables[time_step][1], self.move_variables[time_step][2], constraint_pair)
          touched_position_output_gates.append(cur_equality_output_gate)
          # time step + 1 because these are effects:
          then_constraint_output_gates.append(self.generate_if_then_predicate_constraint(cur_equality_output_gate,predicate, time_step + 1,"pos"))
      # constraints for postive effects:
      for effect in self.parsed.white_action_list[i].negative_effects:
        # no spaces for sake of correct parsing:
        assert(" " not in effect)
        split_effect = effect.strip(")").split("(")
        predicate = split_effect[0]
        constraint_pair = split_effect[1].split(",")
        cur_equality_output_gate = self.generate_position_equalities_with_adder_and_subtractors(self.move_variables[time_step][1], self.move_variables[time_step][2], constraint_pair)
        touched_position_output_gates.append(cur_equality_output_gate)
        # time step + 1 because these are effects:
        then_constraint_output_gates.append(self.generate_if_then_predicate_constraint(cur_equality_output_gate,predicate, time_step + 1,"neg"))

      # compute the touched positions for propogation:
      # for the positions that are not in effects, the state is propogated:
      self.encoding.append(['# disjunction for all touched positions:'])
      self.gates_generator.or_gate(touched_position_output_gates)
      self.encoding.append(['# frame axiom; if not touched position, then it is propagated:'])
      # if not these positions we propogate:
      self.gates_generator.or_gate([self.gates_generator.output_gate,propagation_output_gate])
      then_constraint_output_gates.append(self.gates_generator.output_gate)

      # conjunction for then constraint gates:
      self.gates_generator.and_gate(then_constraint_output_gates)
      then_constraint_final_output_gate = self.gates_generator.output_gate


      # finally the if then constraints for effects and propogation when the boolean variables hold for each action and when game is not stopped:
      self.gates_generator.and_gate([valid_move_output_gate, cur_action_binary_output_gate])
      if_condition_output_gate = self.gates_generator.output_gate

      # if then constraint:
      self.gates_generator.if_then_gate(if_condition_output_gate, then_constraint_final_output_gate)
      #self.transition_step_output_gates.append(self.gates_generator.output_gate)
      current_transition_step_output_gates.append(self.gates_generator.output_gate)

      # if not valid, we let the black player to change the state

    # if white moves are only 1, then we force the move variables to first one:
    if (self.num_white_actions == 1):
      #self.transition_step_output_gates.append(-self.move_variables[time_step][0][0])
      current_transition_step_output_gates.append(-self.move_variables[time_step][0][0])

    # only at the end, we set the conjunction to step output gate:
    self.gates_generator.and_gate(current_transition_step_output_gates)
    self.transition_step_output_gates.append(self.gates_generator.output_gate)


  def generate_first_dummy_transition(self, time_step):

    # Allowing local conjunction transition step gates for nested implications later:
    current_transition_step_output_gates = []

    self.encoding.append(['# Dummy black move at time step ' + str(time_step)+ ': '])

    # set all variables to 0, the game is not stopped either:
    cur_disjunction = []
    cur_disjunction.extend(self.move_variables[time_step][0])
    cur_disjunction.extend(self.move_variables[time_step][1])
    cur_disjunction.extend(self.move_variables[time_step][2])
    cur_disjunction.extend(self.move_variables[time_step][3])

    # disjunction first:
    self.gates_generator.or_gate(cur_disjunction)
    # negated or, none are true:
    current_transition_step_output_gates.append(-self.gates_generator.output_gate)

    # Propogation constraints:
    self.encoding.append(['# propagation constraints:'])
    self.gates_generator.complete_equality_gate(self.predicate_variables[time_step], self.predicate_variables[time_step+1])
    current_transition_step_output_gates.append(self.gates_generator.output_gate)

    # counter propagation:
    if (self.parsed.counter_flag == 1):
      self.encoding.append(['# propagation counter constraints:'])
      self.gates_generator.complete_equality_gate(self.counter_variables[time_step], self.counter_variables[time_step+1])
      current_transition_step_output_gates.append(self.gates_generator.output_gate)

    # only at the end, we set the conjunction to step output gate:
    self.gates_generator.and_gate(current_transition_step_output_gates)
    self.transition_step_output_gates.append(self.gates_generator.output_gate)


  def generate_last_dummy_transition(self, time_step):

    # Allowing local conjunction transition step gates for nested implications later:
    current_transition_step_output_gates = []

    self.encoding.append(['# Dummy black move at time step ' + str(time_step)+ ': '])

    # set all variables to 0, the game is not stopped either:
    cur_disjunction = []
    cur_disjunction.extend(self.move_variables[time_step][0])
    cur_disjunction.extend(self.move_variables[time_step][1])
    cur_disjunction.extend(self.move_variables[time_step][2])
    cur_disjunction.append(-self.move_variables[time_step][3][0])

    # disjunction first:
    self.gates_generator.or_gate(cur_disjunction)
    # negated or, none are true:
    current_transition_step_output_gates.append(-self.gates_generator.output_gate)

    # Propogation constraints:
    self.encoding.append(['# propagation constraints:'])
    self.gates_generator.complete_equality_gate(self.predicate_variables[time_step], self.predicate_variables[time_step+1])
    current_transition_step_output_gates.append(self.gates_generator.output_gate)

    # only at the end, we set the conjunction to step output gate:
    self.gates_generator.and_gate(current_transition_step_output_gates)
    self.transition_step_output_gates.append(self.gates_generator.output_gate)



  def generate_strong_linear_constraints(self):

    cur_temp_gates = []

    # if any action, x, y have only 1, then we force it to 1 to avoid search:
    for i in range(self.parsed.depth):
      if(i%2==0):
        if (self.num_black_actions == 1):
          #assert(len(self.move_variables[time_step][0])==1)
          #print("action linear")
          cur_temp_gates.append(-self.move_variables[i][0][0])
      else:
        if (self.num_white_actions == 1):
          #assert(len(self.move_variables[time_step][0])==1)
          #print("action linear")
          cur_temp_gates.append(-self.move_variables[i][0][0])

      if(self.xmax == 1):
        assert(len(self.move_variables[i][1])==1)
        #print("x linear")
        cur_temp_gates.append(-self.move_variables[i][1][0])

      if(self.ymax == 1):
        assert(len(self.move_variables[i][2])==1)
        #print("y linear")
        cur_temp_gates.append(-self.move_variables[i][2][0])

    # if the max x and y indices are 1, then we also force symbolic variables:
    if(self.xmax == 1):
      assert(len(self.forall_position_variables[0])==1)
      cur_temp_gates.append(-self.forall_position_variables[0][0])

    if(self.ymax == 1):
      assert(len(self.forall_position_variables[1])==1)
      cur_temp_gates.append(-self.forall_position_variables[1][0])

    # final and gate:
    if (len(cur_temp_gates) !=0):
      self.encoding.append(['# forcing single index maps to 1: '])
      self.gates_generator.and_gate(cur_temp_gates)
      self.forced_single_output_gate = self.gates_generator.output_gate
    else:
      self.forced_single_output_gate = 0


  def generate_d_transitions(self):
    self.encoding.append(["# ------------------------------------------------------------------------"])
    self.encoding.append(['# Transitions: '])
    if(self.parsed.blackturn == 'first'):
      self.generate_black_transition(0)
    elif(self.parsed.blackturn == 'second'):
      self.generate_first_dummy_transition(0)
    else:
      assert(1==2)
    for i in range(1,self.parsed.depth-1):
      if (i%2 == 0):
        self.generate_black_transition(i)
      else:
        self.generate_white_transition(i)

    if(self.parsed.last_turn == "black"):
      self.generate_black_transition(self.parsed.depth-1)
    else:
      self.generate_last_dummy_transition(self.parsed.depth-1)



  def generate_initial_gate(self):
    initial_step_output_gates = []

    self.encoding.append(["# ------------------------------------------------------------------------"])
    self.encoding.append(['# Initial state: '])

    # Constraints in forall branches for black positions:
    black_position_output_gates = []

    for position in self.parsed.black_initial_positions:
      # generating binary format for indexes separately:
      binary_format_clause1 = self.generate_binary_format(self.forall_position_variables[0],position[0])
      self.gates_generator.and_gate(binary_format_clause1)
      binary_output_gate1 = self.gates_generator.output_gate
      binary_format_clause2 = self.generate_binary_format(self.forall_position_variables[1],position[1])
      self.gates_generator.and_gate(binary_format_clause2)
      binary_output_gate2 = self.gates_generator.output_gate
      self.gates_generator.and_gate([binary_output_gate1,binary_output_gate2])
      black_position_output_gates.append(self.gates_generator.output_gate)


    if (len(black_position_output_gates) != 0):
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
      binary_format_clause1 = self.generate_binary_format(self.forall_position_variables[0],position[0])
      self.gates_generator.and_gate(binary_format_clause1)
      binary_output_gate1 = self.gates_generator.output_gate
      binary_format_clause2 = self.generate_binary_format(self.forall_position_variables[1],position[1])
      self.gates_generator.and_gate(binary_format_clause2)
      binary_output_gate2 = self.gates_generator.output_gate
      self.gates_generator.and_gate([binary_output_gate1,binary_output_gate2])
      white_position_output_gates.append(self.gates_generator.output_gate)

    if (len(white_position_output_gates) != 0):
      self.encoding.append(['# Or for all white forall position clauses: '])
      self.gates_generator.or_gate(white_position_output_gates)

      white_final_output_gate = self.gates_generator.output_gate

      self.encoding.append(['# if white condition is true then first time step occupied and color white (i.e. 1): '])
      self.gates_generator.and_gate([self.predicate_variables[0][0], self.predicate_variables[0][1]])
      self.gates_generator.if_then_gate(white_final_output_gate, self.gates_generator.output_gate)

      initial_step_output_gates.append(self.gates_generator.output_gate)

    # Finally for all other forall branches, the position is unoccupied:
    if (len(black_position_output_gates) != 0 or len(white_position_output_gates) != 0):
      self.encoding.append(['# for all other branches the occupied is 0: '])
      cur_condition_gates = []
      if (len(black_position_output_gates) != 0):
        cur_condition_gates.append(black_final_output_gate)
      if (len(white_position_output_gates) != 0):
        cur_condition_gates.append(white_final_output_gate)

      if (len(cur_condition_gates) != 0):
        self.gates_generator.or_gate(cur_condition_gates)
        self.gates_generator.or_gate([self.gates_generator.output_gate, -self.predicate_variables[0][0]])
        initial_step_output_gates.append(self.gates_generator.output_gate)


    if (self.parsed.counter_flag == 0):
      # Now final output gate for the initial state:
      if (len(initial_step_output_gates) != 0):
        self.gates_generator.and_gate(initial_step_output_gates)
        self.initial_output_gate = self.gates_generator.output_gate
      else:
        # we set every position to unoccupied:
        self.initial_output_gate = -self.predicate_variables[0][0]
    else:
      self.encoding.append(['# setting proper counter values: '])
      # we first set the counter to 0:
      temp_counter_zero_vars = []
      for var in self.counter_variables[0]:
        temp_counter_zero_vars.append(-var)
      self.gates_generator.and_gate(temp_counter_zero_vars)
      counter_zero_gate = self.gates_generator.output_gate

      # now implying in each branch if individual counters are available:
      if(len(self.parsed.counter_initials) == 0):
        final_counter_output_gate = counter_zero_gate
      else:
        step_counter_implication_gates = []
        touched_if_conditions = []
        for c_initial in self.parsed.counter_initials:
          # for now only assuming counters are only set for rows, can be updated later:
          assert(c_initial[1] == "?y")
          # binary gate for forall x varaibles and then implication:
          binary_format_forall_x = self.generate_binary_format(self.forall_position_variables[0],c_initial[0])
          self.gates_generator.and_gate(binary_format_forall_x)
          forall_x_output_gate = self.gates_generator.output_gate
          # adding this forall value to touched conditions:
          if (forall_x_output_gate not in touched_if_conditions):
            touched_if_conditions.append(forall_x_output_gate)
          binary_format_counter_value = self.generate_binary_format(self.counter_variables[0],c_initial[2])
          self.gates_generator.and_gate(binary_format_counter_value)
          counter_value = self.gates_generator.output_gate

          # implying the right counter value:
          self.gates_generator.if_then_gate(forall_x_output_gate,counter_value)
          step_counter_implication_gates.append(self.gates_generator.output_gate)
        # conjunction for implied counter gates:
        self.gates_generator.and_gate(step_counter_implication_gates)
        all_implied_counter_output_gate = self.gates_generator.output_gate

        # for the not-touched branches, we set to counteer to 0:
        self.gates_generator.or_gate(touched_if_conditions)
        self.gates_generator.if_then_gate(-self.gates_generator.output_gate,counter_zero_gate)
        not_implied_counter_output_gate = self.gates_generator.output_gate

        # conjunction of both gives us, the final counter gate:
        self.gates_generator.and_gate([all_implied_counter_output_gate,not_implied_counter_output_gate])
        final_counter_output_gate = self.gates_generator.output_gate

      if (len(initial_step_output_gates) != 0):
        self.gates_generator.and_gate(initial_step_output_gates)
        # conjunction with counter zero gate:
        self.gates_generator.and_gate([final_counter_output_gate,self.gates_generator.output_gate])
        self.initial_output_gate = self.gates_generator.output_gate
      else:
        # conjunction with counter zero gate:
        self.gates_generator.and_gate([final_counter_output_gate,-self.predicate_variables[0][0]])
        # we set every position to unoccupied:
        self.initial_output_gate = self.gates_generator.output_gate



  # Generating goal constraints:
  # TODO negations in white:
  def generate_black_goal_gate(self):
    black_goal_step_output_gates = []
    self.encoding.append(["# ------------------------------------------------------------------------"])
    self.encoding.append(['# Goal state: '])
    #================================================================================================================================================================================
    # generating black goal constraints:
    self.encoding.append(['# Black goal constraints: '])
    for single_conjunction_index in range(self.num_black_goal_constraints):
      single_conjunction = self.parsed.black_goal_constraints[single_conjunction_index]
      if (self.num_black_goal_constraints > 1):
        # if condition using the boolean variables to chose one of the disjunction constraints:
        temp_binary_variables = self.generate_binary_format(self.disjunction_goal_boolean_variables, single_conjunction_index)
        self.gates_generator.and_gate(temp_binary_variables)
        if_disjunction_output_gate = self.gates_generator.output_gate
      single_constraint_output_gates = []
      # for each constraint in the goal:
      for constraint in single_conjunction:
        if ("False" in constraint):
          #print(constraint)
          # empty or gate is false:
          self.gates_generator.or_gate([])
          single_constraint_output_gates.append(self.gates_generator.output_gate)
        elif ("nlt" in constraint):
          assert(" " not in constraint)
          # passing x variables and y variables along with index constraint:
          bound_result = self.generate_index_constraint(self.black_goal_index_variables[0], self.black_goal_index_variables[1], constraint)

          if (bound_result != 'None'):
            # negative bound so negation:
            single_constraint_output_gates.append(-bound_result)
        elif ("lt" in constraint):
          assert(" " not in constraint)
          # passing x variables and y variables along with index constraint:
          bound_result = self.generate_index_constraint(self.black_goal_index_variables[0], self.black_goal_index_variables[1], constraint)

          if (bound_result != 'None'):
            single_constraint_output_gates.append(bound_result)
        else:
          if("NOT" in constraint):
            negated = True
            trimmed_constraint = constraint[5:-2]
          else:
            negated = False
            trimmed_constraint = constraint
          split_condition = trimmed_constraint.strip(")").split("(")
          predicate = split_condition[0]
          constraint_pair = split_condition[1].split(",")
          #print(constraint_pair, constraint, trimmed_constraint)
          # we need to handle any adders and subtractors if both variables are present:
          cur_equality_gate = self.generate_position_equalities_with_adder_and_subtractors(self.black_goal_index_variables[0],self.black_goal_index_variables[1], constraint_pair)
          # for now no negations in goal condition:
          if (negated==True):
            cur_constraint_gate = self.generate_if_then_predicate_constraint(cur_equality_gate, predicate, self.parsed.depth ,"neg")
            #print("negated")
          else:
            cur_constraint_gate = self.generate_if_then_predicate_constraint(cur_equality_gate, predicate, self.parsed.depth ,"pos")
          single_constraint_output_gates.append(cur_constraint_gate)

      # conjunction for single constraint output gates:
      self.gates_generator.and_gate(single_constraint_output_gates)
      # if then gate with the choosing variables and conjunction of the single goal constraint variables:
      if (self.num_black_goal_constraints > 1):
        self.gates_generator.if_then_gate(if_disjunction_output_gate, self.gates_generator.output_gate)
      # if variables are not present due to single goal constraint, we simply add the conjunction:
      black_goal_step_output_gates.append(self.gates_generator.output_gate)

    # if the number of disjunction is not the max upper limit, we need less than constraint:
    if (self.num_black_goal_constraints > 1):
      if (self.disjunction_goal_upper_limit != self.num_black_goal_constraints):
        lsc.add_circuit(self.gates_generator, self.disjunction_goal_boolean_variables, self.num_black_goal_constraints)
        black_goal_step_output_gates.append(self.gates_generator.output_gate)

    #----------------------------------------------------------------------------------------------------------------
    # Final goal gate:
    self.encoding.append(['# And gate for black goal constraints, at index '+ str(self.parsed.depth)])
    self.gates_generator.and_gate(black_goal_step_output_gates)
    self.black_goal_output_gate = self.gates_generator.output_gate

  #================================================================================================================================================================================
  def generate_white_goal_gate(self):
    white_goal_step_output_gates = []
    # generating white goal constraints if maker-maker game:
    if (self.makermaker_game == 1):
      self.encoding.append(['# White goal constraints: '])
      # if only one constraint and one goal in white, we consider as a seperate case, we do not need to allocate new variables:
      if (self.num_white_goal_constraints == 1 and self.white_single_goal_num_constraints == 1):
        split_condition = self.parsed.white_goal_constraints[0][0].strip(")").split("(")
        predicate = split_condition[0]
        # asserting the predicate is always white, for now:
        assert(predicate == "white")
        constraint_pair = split_condition[1].split(",")
        # we need to handle any adders and subtractors if both variables are present:
        # instead of white variables we use the forall variables:
        cur_equality_gate = self.generate_position_equalities_with_adder_and_subtractors(self.forall_position_variables[0],self.forall_position_variables[1], constraint_pair)
        # if the if_condition is true then the predicate must not be white:
        cur_constraint_gate = self.generate_if_then_predicate_constraint(cur_equality_gate, predicate, self.parsed.depth ,"neg")
        white_goal_step_output_gates.append(cur_constraint_gate)
      else:
        # for now, we look at the grounded httt instances:
        # We specify each branch i.e., specific white conjunction forall variable branch, and disjunction choosing branch and specific forall positions variables (if present)
        # if the solver is in any of the branches then the final state must be non-white, for now assuming all the constraints are simply white in white goal:
        # constraints for each white goal constraints branch:
        #print("white===================================================================================")
        for white_goal_conjunction_index in range(self.num_white_goal_constraints):
          # generate binary constraint for the white goal index:
          self.encoding.append(['# computing white goal forall index: '])
          # if there is only one constraint, then we do not need the universal variables:
          if (self.num_white_goal_constraints > 1):
            temp_binary_variables = self.generate_binary_format(self.forall_conjunction_white_goal_boolean_variables, white_goal_conjunction_index)
            self.gates_generator.and_gate(temp_binary_variables)
            white_goal_conjunction_index_binary_gate = self.gates_generator.output_gate
          # constraint for each disjunct in the current single white goal branch:
          for single_white_goal_disjunction_index in range(self.white_single_goal_num_constraints):
            self.encoding.append(['# computing single white goal disjunct index: '])
            temp_binary_variables = self.generate_binary_format(self.single_white_goal_disjunct_boolean_variables, single_white_goal_disjunction_index)
            self.gates_generator.and_gate(temp_binary_variables)
            single_white_goal_disjunction_index_binary_gate = self.gates_generator.output_gate

            # using the both above indexes, we chose the forall position branch to look at:
            cur_constraint = self.parsed.white_goal_constraints[white_goal_conjunction_index][single_white_goal_disjunction_index]
            #==========================================================================================================================
            # bounds to be handled properly later:
            #'''
            # current if conditions for bound constraints:
            cur_if_bound_gates = []
            if ("nlt" in cur_constraint):
              assert(" " not in cur_constraint)
              if (self.num_white_goal_constraints > 1):
                cur_if_bound_gates.append(white_goal_conjunction_index_binary_gate)

              # passing x variables and y variables along with index constraint:
              bound_result = self.generate_index_constraint(self.white_goal_index_variables[0], self.white_goal_index_variables[1], cur_constraint)

              if (bound_result != 'None'):
                # negative bound so negation:
                cur_if_bound_gates.append(-bound_result)

              # if there is no bound and no conjunctive if condition, then we do not need the following constraints:
              if (self.num_white_goal_constraints > 1):
                # if there is a valid bound constraint then it can not be the counter example:
                self.gates_generator.and_gate(cur_if_bound_gates)
                cur_if_bound_final_gate = self.gates_generator.output_gate

                self.gates_generator.if_then_gate(cur_if_bound_final_gate, -single_white_goal_disjunction_index_binary_gate)
                if self.gates_generator.output_gate not in white_goal_step_output_gates:
                  white_goal_step_output_gates.append(self.gates_generator.output_gate)

            elif ("lt" in cur_constraint):
              assert(" " not in cur_constraint)

              if (self.num_white_goal_constraints > 1):
                cur_if_bound_gates.append(white_goal_conjunction_index_binary_gate)

              # passing x variables and y variables along with index constraint:
              bound_result = self.generate_index_constraint(self.white_goal_index_variables[0], self.white_goal_index_variables[1], cur_constraint)

              if (bound_result != 'None'):
                cur_if_bound_gates.append(bound_result)

              # if there is no bound and no conjunctive if condition, then we do not need the following constraints:
              if (self.num_white_goal_constraints > 1):
                # if there is a valid bound constraint then it can not be the counter example:
                self.gates_generator.and_gate(cur_if_bound_gates)
                cur_if_bound_final_gate = self.gates_generator.output_gate

                self.gates_generator.if_then_gate(cur_if_bound_final_gate, -single_white_goal_disjunction_index_binary_gate)
                if self.gates_generator.output_gate not in white_goal_step_output_gates:
                  white_goal_step_output_gates.append(self.gates_generator.output_gate)
            #'''
            #==========================================================================================================================
            # assuming there are no lt or nlt in the constraint:
            else:
              assert("nlt" not in cur_constraint)
              assert("lt" not in cur_constraint)
              split_condition = cur_constraint.strip(")").split("(")
              predicate = split_condition[0]
              # asserting the predicate is always white, for now:
              # we allow other predicates, but not negation for now:
              #assert(predicate == "white")
              self.encoding.append(['# computing white goal constraint in white_goal[' + str(white_goal_conjunction_index) + "][" + str(single_white_goal_disjunction_index) + ']' ])
              constraint_pair = split_condition[1].split(",")
              # we need to handle any adders and subtractors if both variables are present:
              cur_equality_gate = self.generate_position_equalities_with_adder_and_subtractors(self.white_goal_index_variables[0],self.white_goal_index_variables[1], constraint_pair)
              # conjunction of all the current if conditions, for now assumming there exists a quantifier alternation,
              # we can also add only the specific if conditions based on the requirement:
              # if there is only one constraint, then we do not need the universal variables:
              if (self.num_white_goal_constraints > 1):
                self.gates_generator.and_gate([white_goal_conjunction_index_binary_gate,single_white_goal_disjunction_index_binary_gate,cur_equality_gate])
                cur_final_if_condition_output_gate = self.gates_generator.output_gate
              else:
                self.gates_generator.and_gate([single_white_goal_disjunction_index_binary_gate,cur_equality_gate])
                cur_final_if_condition_output_gate = self.gates_generator.output_gate
              # if the if_condition is true then the predicate must not be white:
              cur_constraint_gate = self.generate_if_then_predicate_constraint(cur_final_if_condition_output_gate, predicate, self.parsed.depth ,"neg")
              white_goal_step_output_gates.append(cur_constraint_gate)

        # if the number of disjunction is not the max upper limit, we need less than constraint:
        if (self.white_single_goal_num_constraints > 1):
          if (self.single_white_goal_disjunct_upper_limit != self.white_single_goal_num_constraints):
            lsc.add_circuit(self.gates_generator, self.single_white_goal_disjunct_boolean_variables, self.white_single_goal_num_constraints)
            white_goal_step_output_gates.append(self.gates_generator.output_gate)



    #----------------------------------------------------------------------------------------------------------------
    # Final goal gate:
    self.encoding.append(['# And gate for white goal constraints, at index '+ str(self.parsed.depth)])
    self.gates_generator.and_gate(white_goal_step_output_gates)
    self.white_goal_output_gate = self.gates_generator.output_gate


  # propagation gates at each time step:
  def forced_propagation(self):

    self.propagated_output_gates = []
    for i in range(self.parsed.depth):
      self.gates_generator.complete_equality_gate(self.predicate_variables[i],self.predicate_variables[i+1])
      self.propagated_output_gates.append(self.gates_generator.output_gate)


# Final output gate is an nested-gate with inital, goal and transition gates:
  def generate_final_gate(self):

    self.encoding.append(["# ------------------------------------------------------------------------"])
    self.encoding.append(['# Nested gates: '])

    #'''
    # starting with goal gate and last black gate:
    self.gates_generator.and_gate([self.transition_step_output_gates[-1], self.black_goal_output_gate])
    cur_outgate = self.gates_generator.output_gate
    #print("and", cur_outgate)

    #print(self.parsed.depth)

    for i in range(self.parsed.depth-1):
      reverse_index = self.parsed.depth-i-2
      # for white we imply with white legal condition:
      if (reverse_index%2==1):
        # gathering legal boolen variables:
        self.encoding.append(['# white valid constraints at reverse index: ' + str(reverse_index)])
        all_valid_constraints = []
        all_valid_constraints.append(self.move_variables[reverse_index][3][0])
        all_valid_constraints.extend(self.move_variables[reverse_index][4])
        self.gates_generator.and_gate(all_valid_constraints)
        valid_move_output_gate = self.gates_generator.output_gate


        # if maker-maker game, only if white did not stop as well we imply next round:
        if(self.makermaker_game == 1):
          # valid not stopped, then we imply the next round:
          self.gates_generator.and_gate([valid_move_output_gate,-self.move_variables[reverse_index][5][0]])
          not_stopped_valid_gate = self.gates_generator.output_gate
          self.gates_generator.if_then_gate(not_stopped_valid_gate, cur_outgate)
        else:
          # first implying the cur_outgate with valid move gate:
          self.gates_generator.if_then_gate(valid_move_output_gate, cur_outgate)


        not_stopped_implication_gate = self.gates_generator.output_gate
        #print(valid_move_output_gate, "->", cur_outgate)

        # if maker-maker game, we also allow white to stop game:
        if(self.makermaker_game == 1):
          if (self.parsed.args.force_white_player_stop == 1):
            cur_forced_output_gates = []
            self.encoding.append(['# propagating all further predicates: '])
            for p_index in range(reverse_index+1,self.parsed.depth):
              cur_forced_output_gates.append(self.propagated_output_gates[p_index])
            # conjunction of all the gates:
            self.gates_generator.and_gate(cur_forced_output_gates)
          else:
            # we propagate to last step and check the white goal:
            self.encoding.append(['# propagating to the last: '])
            self.gates_generator.complete_equality_gate(self.predicate_variables[reverse_index+1],self.predicate_variables[self.parsed.depth])
          complete_propogation_gate = self.gates_generator.output_gate
          # only when valid and stopped we check the goal condition:
          self.gates_generator.and_gate([valid_move_output_gate,self.move_variables[reverse_index][5][0]])
          stopped_valid_gate = self.gates_generator.output_gate
          self.gates_generator.if_then_gate(stopped_valid_gate, [complete_propogation_gate, self.white_goal_output_gate])
          stopped_implication_gate = self.gates_generator.output_gate
          # conjunction with this round of constraints:
          self.gates_generator.and_gate([self.transition_step_output_gates[reverse_index], not_stopped_implication_gate, stopped_implication_gate])
        else:
          # conjunction with this round of constraints:
          self.gates_generator.and_gate([self.transition_step_output_gates[reverse_index], not_stopped_implication_gate])


        cur_outgate = self.gates_generator.output_gate
        #print("and", cur_outgate)
      # for black we imply with game stop condition:
      else:
        self.encoding.append(['# black imply constraints at reverse index: ' + str(reverse_index)])
        # first implying the cur_outgate with negated game stop gate:
        self.gates_generator.or_gate([self.move_variables[reverse_index][3][0], cur_outgate])
        negated_implication_gate = self.gates_generator.output_gate
        # propagate to the last step and imply black goal:

        if (self.parsed.args.force_black_player_stop == 1):
          cur_forced_output_gates = []
          self.encoding.append(['# propagating all further predicates: '])
          for p_index in range(reverse_index+1,self.parsed.depth):
            cur_forced_output_gates.append(self.propagated_output_gates[p_index])
          # conjunction of all the gates:
          self.gates_generator.and_gate(cur_forced_output_gates)
        else:
          self.gates_generator.complete_equality_gate(self.predicate_variables[reverse_index+1],self.predicate_variables[self.parsed.depth])
        self.gates_generator.if_then_gate(self.move_variables[reverse_index][3][0], [self.gates_generator.output_gate, self.black_goal_output_gate])
        unnegated_implication_gate = self.gates_generator.output_gate
        # conjunction with this round of constraints:
        self.gates_generator.and_gate([self.transition_step_output_gates[reverse_index], negated_implication_gate, unnegated_implication_gate])

        cur_outgate = self.gates_generator.output_gate



    self.encoding.append(["# ------------------------------------------------------------------------"])
    self.encoding.append(['# Final gate: '])

    assert(self.initial_output_gate != 0)

    # if forced is 0, normal generation:
    if(self.forced_single_output_gate == 0):
      self.encoding.append(['# Conjunction of Initial gate and nested output gate: '])
      self.gates_generator.and_gate([self.initial_output_gate, cur_outgate])
    else:
      self.encoding.append(['# Conjunction of Initial gate, forced gate and nested output gate: '])
      self.gates_generator.and_gate([self.initial_output_gate, self.forced_single_output_gate, cur_outgate])
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


    # output string index:
    self.output_sat_index_string = '-e '
    self.output_unsat_index_string = '-e '

    # We generate game stop variables and white illegal variable only for maker-maker games, otherwise no need,
    # remembering which type of game:
    if (len(parsed.white_goal_constraints) == 0):
      self.makermaker_game = 0
    else:
      self.makermaker_game = 1


    # Allocating action variables for each time step until depth:
    # for general board the board can be rectangular, allocating for both indexes separately:
    self.num_x_index_variables = int(math.ceil(math.log2(parsed.xmax)))
    self.num_y_index_variables = int(math.ceil(math.log2(parsed.ymax)))


    # if single x,y then log is 0:
    if (self.num_x_index_variables == 0):
      self.num_x_index_variables = 1

    if (self.num_y_index_variables == 0):
      self.num_y_index_variables = 1


    self.xmax = parsed.xmax
    self.ymax = parsed.ymax
    self.upperlimit_xmax = int(math.pow(2, self.num_x_index_variables))
    self.upperlimit_ymax = int(math.pow(2, self.num_y_index_variables))
    # number of black actions:
    self.num_black_actions = len(self.parsed.black_action_list)
    # we need logarithmic number of variables to represent them:
    self.num_black_action_variables = int(math.ceil(math.log2(self.num_black_actions)))
    # if there is only one action, then the number of variables will be 0 so we make it 1:
    # later we optimise that these variables are existence for both players and set it to specific value for better performance:
    # Optmization point TODO:
    if (self.num_black_action_variables == 0):
      self.num_black_action_variables = 1
    self.upperlimit_black_actions = int(math.pow(2,self.num_black_action_variables))
    # number of white actions:
    self.num_white_actions = len(self.parsed.white_action_list)
    # we need logarithmic number of variables to represent them:
    self.num_white_action_variables = int(math.ceil(math.log2(self.num_white_actions)))
    if (self.num_white_action_variables == 0):
      self.num_white_action_variables = 1
    self.upperlimit_white_actions = int(math.pow(2,self.num_white_action_variables))

    self.move_variables = []
    for i in range(parsed.depth):
      temp_list = []
      # for black we use the black log action variables:
      if (i%2 == 0):
        # we always append the binary format, we will optimise later:
        temp_list.append(self.encoding_variables.get_vars(self.num_black_action_variables))
      else:
        # same as black actions, we only generate new action variables if there are more than 1 actions, no need for extra variables if only one action:
        temp_list.append(self.encoding_variables.get_vars(self.num_white_action_variables))
      # Action parameter variables, these are essentially x,y indexes for the action chosen:
      # if ?x is used in the actions:
      if (self.parsed.x_flag == 1):
        temp_list.append(self.encoding_variables.get_vars(self.num_x_index_variables))
      else:
        temp_list.append([])
      if (self.parsed.y_flag == 1):
        temp_list.append(self.encoding_variables.get_vars(self.num_y_index_variables))
      else:
        temp_list.append([])
      # now appending game stop variable and illegal moves for black and white respective, if the game is maker-maker
      # for maker-breaker game these variables are not need, however it is not handled yet:
      temp_list.append(self.encoding_variables.get_vars(1))
      # only for white we need extra variables to specify which position is false in preconditions for illegal moves:
      if (i%2 == 1):
        temp_list.append(self.encoding_variables.get_vars(self.parsed.max_white_preconditions))
        # also add white game stop variable if maker-maker game:
        if (self.makermaker_game == 1):
          temp_list.append(self.encoding_variables.get_vars(1))

      self.move_variables.append(temp_list)

    if (parsed.args.debug == 1):
      print("Number of (log) black choosing variables: ", self.num_black_action_variables)
      print("Number of (log) white choosing variables: ", self.num_white_action_variables)
      print("Number of (log) x index variables: ", self.num_x_index_variables)
      print("Number of (log) y index variables: ", self.num_y_index_variables)
      print("Move variables: ",self.move_variables)

    self.num_black_goal_constraints = len(self.parsed.black_goal_constraints)
    # For disjunction of conjunction constraints, we need to specify which conjunction is true,
    # for that we use boolean variables:
    # we do not need boolean variables if there is only one goal conjunction though:
    if (self.num_black_goal_constraints > 1):
      self.num_black_goal_disjunction_variables = int(math.ceil(math.log2(self.num_black_goal_constraints)))
      self.disjunction_goal_boolean_variables = self.encoding_variables.get_vars(self.num_black_goal_disjunction_variables)

      # remembering upper limit of disjunction, to handle less than constraints for choosing variables:
      self.disjunction_goal_upper_limit = int(math.pow(2,self.num_black_goal_disjunction_variables))


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

    # by default we assume we do not need an extra alternation, this is the case for breakthough and knightthrough (ofcourse and all maker-breaker games):
    self.extra_white_quantifier_alternation = 0
    # we need the length of each white goal, we need it to be the same for all white goal constraints:
    self.white_single_goal_num_constraints = 0


    # if there is a conjunction in any white goal constraint, then we need an extra quantifier alternation,
    # the negation of it becomes disjunction so we need existential variables to look at multiple branches:
    for line in parsed.white_goal_constraints:
      if (len(line) > 1):
        self.extra_white_quantifier_alternation = 1
      # if white goal num constraints is not set to 0, then they are should be equal:
      if (self.white_single_goal_num_constraints == 0):
        self.white_single_goal_num_constraints = len(line)
      else:
        assert(self.white_single_goal_num_constraints == len(line))


    # allocating variables for white constraints, for now looking at the strings to check if both indexes are necessary,
    # we only generate x,y variables for white if we need an extra quantifier alternation (otherwise we simply use the forall positions),
    # note that right now we only handle goal constraints based on single position:

    self.white_goal_index_variables = []
    # checking for x index:
    temp_x_index_white_variables = []
    # we only generate variables if alternation is needed:
    if (self.extra_white_quantifier_alternation == 1):
      for line in parsed.white_goal_constraints:
        for constraint in line:
          if ('?x' in constraint):
            # we have x indexed position:
            temp_x_index_white_variables = self.encoding_variables.get_vars(self.num_x_index_variables)
            break
        # we only allocate the variables once:
        if (len(temp_x_index_white_variables) != 0):
          break
    self.white_goal_index_variables.append(temp_x_index_white_variables)
    # checking for y index
    temp_y_index_white_variables = []
    if (self.extra_white_quantifier_alternation == 1):
      for line in parsed.white_goal_constraints:
        for constraint in line:
          if ('?y' in constraint):
            # we have y indexed position:
            temp_y_index_white_variables = self.encoding_variables.get_vars(self.num_y_index_variables)
            break
        # we only allocate the variables once:
        if (len(temp_y_index_white_variables) != 0):
          break
    self.white_goal_index_variables.append(temp_y_index_white_variables)

    # Allocating univeral variables for white goal constraints, each branch which constrain a single white goal,
    # (in negated white constraints), we need to specify that all the constraints voilate in one of the individual constraints,
    # for that we use boolean variables:
    # we do not need boolean variables if there is only one goal conjunction though:
    self.num_white_goal_constraints = len(self.parsed.white_goal_constraints)
    if (self.num_white_goal_constraints > 1):
      self.num_white_goal_conjunction_forall_variables = int(math.ceil(math.log2(self.num_white_goal_constraints)))
      self.forall_conjunction_white_goal_boolean_variables = self.encoding_variables.get_vars(self.num_white_goal_conjunction_forall_variables)


    # in each of the branch we need to specify where the white constraint fails (good for negation):
    # only if we have more than 1 disjunct in the constraints, we need to generate boolean variables:
    if (self.white_single_goal_num_constraints > 1):
      self.num_white_goal_single_disjunct_boolean_variables = int(math.ceil(math.log2(self.white_single_goal_num_constraints)))
      self.single_white_goal_disjunct_boolean_variables = self.encoding_variables.get_vars(self.num_white_goal_single_disjunct_boolean_variables)

      # since existential, we need lessthan constraint in the white goal so we need the upper bound:
      self.single_white_goal_disjunct_upper_limit = int(math.pow(2,self.num_white_goal_single_disjunct_boolean_variables))



    if (parsed.args.debug == 1):
      print("black goal variables: ",self.black_goal_index_variables)
      print("extra quantifier alternative for white goal: ",self.extra_white_quantifier_alternation)
      print("number of white single goal constraints: ",self.white_single_goal_num_constraints)
      print("white goal variables: ",self.white_goal_index_variables)
      if (self.num_white_goal_constraints > 1):
        print("forall conjunction white goal boolean variables: ",self.forall_conjunction_white_goal_boolean_variables)

    # Allocating forall position variables:
    self.forall_position_variables = []
    self.forall_position_variables.append(self.encoding_variables.get_vars(self.num_x_index_variables))
    self.forall_position_variables.append(self.encoding_variables.get_vars(self.num_y_index_variables))

    if (parsed.args.debug == 1):
      print("Forall position variables: ",self.forall_position_variables)


    # allocating counter variables:
    if (self.parsed.counter_flag == 1):
      self.num_counter_vars = int(math.ceil(math.log2(self.parsed.counter_bound)))
      self.counter_variables = []
      for i in range(parsed.depth+1):
        self.counter_variables.append(self.encoding_variables.get_vars(self.num_counter_vars))

    # Allocating predicate variables, two variables are used one is occupied and
    # other color (but implicitly) for each time step:
    self.predicate_variables = []
    for i in range(parsed.depth+1):
      self.predicate_variables.append(self.encoding_variables.get_vars(2))

    if (parsed.args.debug == 1):
      print("Predicate variables: ",self.predicate_variables)



    # Generating quantifer blocks:
    self.generate_quantifier_blocks()

    if (self.parsed.args.sort_internal_gates == 0):
      self.gates_generator = ggen(self.encoding_variables, self.encoding)
    else:
      self.gates_generator = uggen(self.encoding_variables, self.encoding)

    # Generating d steps i.e., which includes black and white constraints:
    self.generate_d_transitions()

    self.generate_initial_gate()

    self.generate_black_goal_gate()

    self.generate_white_goal_gate()

    self.generate_strong_linear_constraints()

    if (self.parsed.args.force_black_player_stop == 1 or self.parsed.args.force_white_player_stop == 1):
      self.forced_propagation()

    self.generate_final_gate()

    self.print_meta_data_tofile()
