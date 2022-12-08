# Irfansha Shaik, 19.11.2022, Aarhus.

'''
TODO: Some testing is needed.
'''

class GatesGen:

  # removes redundant vars and sorts the list:
  def clean_list(self,cur_list):
    new_list = []
    for var in cur_list:
      if (var not in new_list):
        new_list.append(var)
    new_list.sort()
    return new_list

  '''
  # Takes list and current list of gates
  # generates OR gate:
  # TODO: if single length we can return with out gate:
  def or_gate(self, current_list):
    list_key = self.clean_list(current_list)
    #key = ('or', tuple(current_list))
    key = ('or', tuple(list_key))
    if key in self.gate_reuse_map:
      self.output_gate = self.gate_reuse_map[key]
      return
    if (len(list_key) == 1):
      self.output_gate = list_key[0]
      return
    temp_gate = ['or', self.next_gate, current_list]
    self.gates.append(temp_gate)
    self.output_gate = self.next_gate
    self.next_gate = self.vd.get_single_var()
    self.gate_reuse_map[key] = self.output_gate
  '''


  # Takes list and call and gate with negations:
  def or_gate(self, current_list):
    negated_list = []
    for var in current_list:
      negated_list.append(-var)
    self.and_gate(negated_list)
    self.output_gate = -self.output_gate



  # Takes list and current list of gates
  # generates AND gate:
  # TODO: if single length we can return with out gate:
  def and_gate(self, current_list):
    list_key = self.clean_list(current_list)
    #if(len(list_key)>4):
    #  print(len(list_key))
    #key = ('and', tuple(current_list))
    key = ('and', tuple(list_key))
    if key in self.gate_reuse_map:
      self.output_gate = self.gate_reuse_map[key]
      return
    if (len(list_key) == 1):
      self.output_gate = list_key[0]
      return
    temp_gate = ['and', self.next_gate, current_list]
    self.gates.append(temp_gate)
    self.output_gate = self.next_gate
    self.next_gate = self.vd.get_single_var()
    self.gate_reuse_map[key] = self.output_gate

  # Takes list and current list of gates
  # generates if then gate i.e., if x then y -> y' = AND(y) and OR(-x, y'):
  def if_then_gate(self, if_gate, then_list):
    # checking if then_list is an int:
    if isinstance(then_list, int):
      key = ('ifthen', if_gate, then_list)
    else:
      list_key = self.clean_list(then_list)
      #key = ('ifthen', if_gate, tuple(then_list))
      key = ('ifthen', if_gate, tuple(list_key))
    if key in self.gate_reuse_map:
      self.output_gate = self.gate_reuse_map[key]
      return
    # AND gate for then list:
    if isinstance(then_list, int):
      self.or_gate([-if_gate, then_list])
    else:
      self.and_gate(then_list)
      self.or_gate([-if_gate, self.output_gate])
    self.gate_reuse_map[key] = self.output_gate


  # Takes list and current list of gates
  # generates eq gate i.e., x == y -> if x then y and if y then x:
  def single_equality_gate(self, x, y):
    key = ('eq', x, y)
    if key in self.gate_reuse_map:
      self.output_gate = self.gate_reuse_map[key]
      return
    self.if_then_gate(x,y)
    temp_first_gate = self.output_gate
    self.if_then_gate(y,x)
    self.and_gate([temp_first_gate,self.output_gate])
    self.gate_reuse_map[key] = self.output_gate

  # Takes lists of gates of two object vars and generates equality gate:
  def complete_equality_gate(self, first_vars, second_vars):
    key = ('eq', tuple(first_vars), tuple(second_vars))
    if key in self.gate_reuse_map:
      self.output_gate = self.gate_reuse_map[key]
      return
    #assert(len(first_vars) == len(second_vars))

    temp_first_vars = list(first_vars)
    temp_second_vars = list(second_vars)

    step_output_gates = []

    # If the number of vars is inequal then we need to change the equality gates,
    # we simly negate all the extra variables:
    while (len(temp_first_vars) != len(temp_second_vars)):
      if (len(temp_first_vars) < len(temp_second_vars)):
        cur_var = temp_second_vars.pop(0)
      elif(len(temp_second_vars) < len(temp_first_vars)):
        cur_var = temp_second_vars.pop(0)
      step_output_gates.append(-cur_var)

    for i in range(len(temp_first_vars)):
      self.single_equality_gate(temp_first_vars[i], temp_second_vars[i])
      step_output_gates.append(self.output_gate)
    self.and_gate(step_output_gates)
    self.gate_reuse_map[key] = self.output_gate


  def __init__(self, vd, gates):
    self.vd = vd
    self.output_gate = 0 # output gate will next be 0
    self.next_gate = self.vd.get_single_var()
    self.gate_reuse_map = dict()
    self.gates = gates

