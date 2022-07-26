# Irfansha Shaik, 26.07.2022, Aarhus

# Takes a cleansed qcir format and transforms to qdimacs
# - we also add an option to move the new variables to appropriate levels (todo).


# TODO:
# add move option for moving the varaibles to appropriate levels.
#  - we can keep the comments in place if needed
#  - can also add option for generating negated qdimacs, should very simple:

import argparse

# for each variable/gate we specify the level (in matrix)
level_dict = dict()

# parsed matrix, without circuit keywords:
parsed_matrix = []

# parsed gate_lines, without circuit keywords:
parsed_gate_lines = []

# remembering intermediate gates separately:
intermediate_gates = []

# qdimacs clauses:
qdimacs_clauses_list = []

#==========================================================================================
# Parses matrix lines:
def parse_matrix(matrix_lines):
  # we can merge matrix lines if there are the same quatifier type:
  previous_qtype = ''
  # we can already count the level of each variable:
  cur_level = 0

  for line in matrix_lines:
    # asserting the line is part of matrix:
    assert("exists" in line or "forall" in line)
    # removing spaces
    cleaned_line = line.replace(" ","")
    if ("exists" in cleaned_line):
      cur_var_list = cleaned_line.strip("exists(").strip(")").split(",")
      cur_qtype = 'e'
    else:
      assert("forall" in cleaned_line)
      cur_var_list = cleaned_line.strip("forall(").strip(")").split(",")
      cur_qtype = 'a'

    # we are in the same quantifier block:
    if (previous_qtype == cur_qtype):
      parsed_matrix[-1][1].extend(cur_var_list)
    else:
      # a tuple of type and the var list:
      parsed_matrix.append((cur_qtype,cur_var_list))
      previous_qtype = cur_qtype
      # increasing the previous level:
      cur_level = cur_level + 1

    # for each var we update the level:
    for var in cur_var_list:
      level_dict[var] = cur_level

  # assert the quantifier are alternating in the parsed_matrix:
  for i in range(len(parsed_matrix)-1):
    assert(parsed_matrix[i][0]!=parsed_matrix[i+1][0])
#==========================================================================================


#==========================================================================================
# Parse gate lines:
def parse_gates(gate_lines):
  for line in gate_lines:
    # asserting the line is part of gate:
    assert("or" in line or "and" in line)
    # removing spaces
    cleaned_line = line.replace(" ","")
    if ("or" in cleaned_line):
      # first seperating intermediate gate:
      [cur_gate, cur_list] = cleaned_line.split("=")
      cur_var_list = cur_list.strip("or(").strip(")").split(",")
      cur_type = 'or'
    else:
      assert("and" in cleaned_line)
      # first seperating intermediate gate:
      [cur_gate, cur_list] = cleaned_line.split("=")
      cur_var_list = cur_list.strip("and(").strip(")").split(",")
      cur_type = 'and'

    parsed_gate_lines.append((cur_type, cur_gate, cur_var_list))
    # intermediate gate:
    intermediate_gates.append(cur_gate)
    # initializing max at 1, as any variable can be only top most at the least:
    cur_max = 1
    # computing the highest level
    for var in cur_var_list:
      # removing if negative sign in the variable:
      if (var[0] == "-"):
        temp_var = var[1:]
      else:
        temp_var = var
      if (cur_max < level_dict[temp_var]):
        cur_max = level_dict[temp_var]

    level_dict[cur_gate] = cur_max

# simply negates the var
def negate_var(var):
  if (var[0] == '-'):
    return var[1:]
  else:
    return '-' + var


#==========================================================================================
# Generates cnf clauses from gates:
# Key idea:
#  for any circuit gate, we make the intermediate gate as a new variable and then we use iff constraints to maintain correctness
#  if the gate is And gate, for example g1 = and(var1, var2) ------> (g1 -> and(var1, var2) & and(var1, var2) -> g1)
#                           when expanded: (var1 v -g1) ∧ (var2 v -g1)     ∧     (-var1 v -var2 v g1)
#  if the gate is Or gate, for example g1 = or(var1, var2) ------> (g1 -> or(var1, var2) & or(var1, var2) -> g1)
#                           when expanded: (-var1 v g1) ∧ (-var2 v g1)     ∧     (var1 v var2 v -g1)
def generate_cnf_clauses():
  for gate_line in parsed_gate_lines:
    if (gate_line[0] == "and"):
      assert('-' not in gate_line[1])
      # binary clauses:
      for var in gate_line[2]:
        qdimacs_clauses_list.append([var, negate_var(gate_line[1])])
      # long clause:
      temp_list = []
      for var in gate_line[2]:
        temp_list.append(negate_var(var))
      temp_list.append(gate_line[1])
      qdimacs_clauses_list.append(temp_list)
    elif(gate_line[0] == "or"):
      assert('-' not in gate_line[1])
      # binary clauses:
      for var in gate_line[2]:
        qdimacs_clauses_list.append([negate_var(var), gate_line[1]])
      # long clause:
      temp_list = []
      for var in gate_line[2]:
        temp_list.append(var)
      temp_list.append(negate_var(gate_line[1]))
      qdimacs_clauses_list.append(temp_list)


# Main:
if __name__ == '__main__':
  text = "Takes a cleansed qcir encoding and traslates to qdimacs format"
  parser = argparse.ArgumentParser(description=text,formatter_class=argparse.RawTextHelpFormatter)
  parser.add_argument("--input_file", help="input qcir encoding path")
  parser.add_argument("--output_file", help="output qdimacs file path")
  parser.add_argument("--move_intermediate_gates", type=int, help="use qcir gate information to push the intermediate gates inside, default 0", default=0)
  args = parser.parse_args()

  f = open(args.input_file,"r")
  qcir_lines = f.readlines()
  f.close()

  matrix_lines = []
  # cannot be 0, but initializing to 0:
  output_gate = 0
  gate_lines = []

  # seperate matrix, output gate and inner gates:
  for line in qcir_lines:
    # we strip if there are any next lines or empty spaces:
    stripped_line = line.strip("\n").strip(" ")
    # we ignore if comment or empty line:
    if (line == ""):
      continue
    elif(line[0] == "#"):
      continue
    # if exists/forall in the line then it is part of matrix:
    elif ("exists" in stripped_line or "forall" in stripped_line):
      matrix_lines.append(stripped_line)
    elif ("output" in stripped_line):
      output_gate = stripped_line.strip(")").split("(")[-1]
    else:
      gate_lines.append(stripped_line)

  # Parse matrix lines:
  parse_matrix(matrix_lines)

  # Parse gate lines:
  parse_gates(gate_lines)

  # Generate cnf clauses:
  generate_cnf_clauses()

  # Add output gate:
  qdimacs_clauses_list.append([output_gate])


  #==================================================================================
  # number of variables (for now lets us say we get the maximum value):
  keys_list = list(level_dict.keys())
  max_var = -1
  for key in keys_list:
    if (max_var < int(key)):
      max_var = int(key)
  num_clauses = len(qdimacs_clauses_list)
  #==================================================================================

  # write the cnf encoding:
  f = open(args.output_file,"w")
  # writing the header line:
  f.write("p cnf " + str(max_var) + " " + str(num_clauses) + "\n")

  # this way we only put all the intermediate gate in the inner most layer:
  if (args.move_intermediate_gates == 0):
    for line in parsed_matrix:
      temp_list = []
      temp_list.append(line[0])
      temp_list.extend(line[1])
      f.write(" ".join(temp_list) + " 0\n")
    # now the intermediate gates:
    temp_list = []
    temp_list.append("e")
    temp_list.extend(intermediate_gates)
    f.write(" ".join(temp_list) + " 0\n")

  # qdimacs clauses:
  for line in qdimacs_clauses_list:
    f.write(" ".join(line) + " 0\n")

  # only for checking the testing with leanders script:
  f.write("\n")
  f.close()
