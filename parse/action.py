# Irfansha Shaik, 03.06.2022, Aarhus.

import ast


# Does addition and substration for now in the string,
# assuming only two numbers in the computation string:
def compute(str):
  # no spaces:
  assert(" " not in str)
  # if addition:
  if ("+" in str):
    split_str = str.split("+")
    sum = int(split_str[0]) + int(split_str[1])
    return sum
  elif ('-' in str):
    split_str = str.split("-")
    dif = int(split_str[0]) - int(split_str[1])
    return dif
  else:
    # nothing to compute:
    return int(str)


class Action:

  def __init__(self, parsed, cur_action_lines):

    self.action_name = ''
    self.parameters = []
    self.positive_indexbounds = []
    self.negative_indexbounds = []
    self.positive_preconditions = []
    self.negative_preconditions = []
    self.positive_effects = []
    self.negative_effects = []

    # just action name is enough:
    #print(cur_action_lines)
    self.action_name = cur_action_lines[0][-1]
    #print(self.action_name)

    # parsing the parameter names, for now restricting to one pair only:
    # asserting if the current line is parameter line:
    assert(cur_action_lines[1][0] == ':parameters')
    for i in range(1, len(cur_action_lines[1])):
      parameter = cur_action_lines[1][i].strip(")").strip("(").strip(",")
      self.parameters.append(parameter)
    #print(self.parameters)

    # index bounds can be both in lessthan-equal and greaterthan-equal,
    # since we only implement lessthan, we convert the constraints to lessthan and separate positive and negative constraints,
    # if there is a "greaterthan 0" constraint we just drop it:
    # asserting if the current line is index bounds line:
    assert(cur_action_lines[2][0] == ':indexbounds')
    original_line = ' '.join(cur_action_lines[2][1:])
    # stripping the '(' and ')' in the line and replacing ", " with simple ","; makes it easier to split:
    original_line_split = original_line[1:-1].replace(", ",",").split(" ")
    # For 'le' bounds: changing (lessthan-equal k) -> (lessthan k+1); adjusting the index to 0 we need subtract 1 -> (lessthan k):
    # For 'ge' bounds: changing (greaterthan-equal k) -> ( not(lessthan k)); adjusting the index to 0 we need subtract 1 -> not(lessthan k-1):
    for bound in original_line_split:
      # replacing xmin with 1 and xmax with xmax from the input:
      bound = bound.replace('xmin','1')
      bound = bound.replace('xmax',str(parsed.xmax))
      # replacing ymin with 1 and ymax with ymax from input:
      bound = bound.replace('ymin','1')
      bound = bound.replace('ymax',str(parsed.ymax))
      if (bound[:2] == 'le'):
        # computing the addition and subtraction:
        bound_computation = bound.strip(")").split(",")[-1]
        result = compute(bound_computation)
        # we do not want negative numbers or zero for less than operator:
        assert((result) > 0)
        # replacing with the computed result:
        bound = bound.replace(bound_computation, str(result))
        # after changes now it is lessthan operator:
        bound = bound.replace('le', 'lt')
        self.positive_indexbounds.append(bound)
        # assert no addition and subtraction present in the string:
        assert('+' not in bound)
        assert('-' not in bound)
      else:
        # asserting the other bound to be 'ge':
        assert(bound[:2] == 'ge')
        bound_computation = bound.strip(")").split(",")[-1]
        result = compute(bound_computation)
        result = result - 1
        # we do not want negative numbers or zero for less than operator:
        # replacing with the computed result -1, since we substract 1 for ge case:
        bound = bound.replace(bound_computation, str(result))
        # after changes now it is lessthan operator:
        bound = bound.replace('ge', 'lt')
        if (result == 0):
          continue
        else:
          self.negative_indexbounds.append(bound)

        # assert no addition and subtraction present in the string:
        assert('+' not in bound)
        assert('-' not in bound)

    # Separating positive and negative preconditions:
    assert(cur_action_lines[3][0] == ':precondition')
    original_line = ' '.join(cur_action_lines[3][1:])
    original_line_split = original_line[1:-1].replace(", ",",").split(" ")
    for condition in original_line_split:
      if ('NOT' not in condition):
        self.positive_preconditions.append(condition)
      else:
        condition = condition.strip("NOT(")[:-1]
        self.negative_preconditions.append(condition)

    # Separating positive and negative effects:
    assert(cur_action_lines[4][0] == ':effect')
    original_line = ' '.join(cur_action_lines[4][1:])
    original_line_split = original_line[1:-1].replace(", ",",").split(" ")
    for condition in original_line_split:
      if ('NOT' not in condition):
        self.positive_effects.append(condition)
      else:
        condition = condition.strip("NOT(")[:-1]
        self.negative_effects.append(condition)


  def __str__(self):
      return 'action: ' + self.action_name + \
      '\n  parameters: ' + str(self.parameters) + \
      '\n  positive indexbounds: ' + str(self.positive_indexbounds) + \
      '\n  negative indexbounds: ' + str(self.negative_indexbounds) + \
      '\n  positive preconditions: ' + str(self.positive_preconditions) + \
      '\n  negative preconditions: ' + str(self.negative_preconditions) + \
      '\n  positive effects: ' + str(self.positive_effects) + \
      '\n  negative effects: ' + str(self.negative_effects) + '\n'
