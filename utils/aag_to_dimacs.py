# Irfansha Shaik, 23.09.2022, Aarhus

# Takes a ascii-aiger format and transforms to dimacs

import argparse

# parsed gate_lines, without circuit keywords:


# dimacs clauses:
dimacs_clauses_list = []

#==========================================================================================

# simply negates the var
def negate_var(var):
    return -1 * var

# divides with 2, and gets the sign from modulo:
def get_var(gate_var):
  var = int(int(gate_var)/2)
  sign = int(gate_var)%2

  if (sign == 0):
    return var
  else:
    return -var


#==========================================================================================
# Generates cnf clauses from gates:
# Key idea:
#  for any aig gate, we make the intermediate gate as a new variable and then we use iff constraints to maintain correctness
#  if the gate is And gate, for example g1 = and(var1, var2) ------> (g1 -> and(var1, var2) & and(var1, var2) -> g1)
#                           when expanded: (var1 v -g1) ∧ (var2 v -g1)     ∧     (-var1 v -var2 v g1)
#  we need to handle the edge cases where the input gates are simply '1' and '0':
def generate_cnf_clauses(gate_lines):
  for gate in gate_lines:
    #print(gate)
    #  1 1 is a true gate:
    if (gate[1] == '1' and gate[2] == '1'):
      dimacs_clauses_list.append([get_var(gate[0])])
    elif (gate[1] == '0' and gate[2] == '0'):
      dimacs_clauses_list.append([negate_var(get_var(gate[0]))])
    else:
      # asserting there is no false input gate:
      assert(gate[1] != '0')
      assert(gate[2] != '0')
      first_input = get_var(gate[1])
      second_input = get_var(gate[2])

      output = get_var(gate[0])

      # if the vars are contradictory, it is false:
      if (first_input ==  negate_var(second_input)):
        dimacs_clauses_list.append([negate_var(output)])
      else:
        var_list = []
        if (gate[1] != "1"):
          var_list.append(first_input)
        if (gate[2] != "1" and second_input not in var_list):
          var_list.append(second_input)

        #print(gate[0], var_list)

        # binary clauses:
        for var in var_list:
          dimacs_clauses_list.append([var, negate_var(output)])
        # long clause:
        temp_list = []
        for var in var_list:
          temp_list.append(negate_var(var))
        temp_list.append(output)
        dimacs_clauses_list.append(temp_list)


# Main:
if __name__ == '__main__':
  text = "Takes aag file and traslates to dimacs format"
  parser = argparse.ArgumentParser(description=text,formatter_class=argparse.RawTextHelpFormatter)
  parser.add_argument("--input_file", help="input aag file path")
  parser.add_argument("--output_file", help="output dimacs file path")
  args = parser.parse_args()

  f = open(args.input_file,"r")
  aag_lines = f.readlines()
  f.close()

  header = aag_lines.pop(0).strip("\n").split(" ")
  # asserting the input is ascii-aiger format:
  #print(header)
  assert(header[0] == 'aag')

  max_index = int(header[1])

  inputs = []

  # parsing input gates:
  for i in range(int(header[2])):
    inputs.append(int(aag_lines.pop(0).strip("\n")))

  #print(inputs)

  # no latches:
  assert(header[3] == '0')

  outputs = []

  # parsing output gates:
  for i in range(int(header[4])):
    outputs.append(int(aag_lines.pop(0).strip("\n")))

  #print(outputs)

  gate_lines = []

  # parsing and gates:
  for i in range(int(header[5])):
    gate_lines.append(aag_lines.pop(0).strip("\n").split(" "))

  # Generate cnf clauses:
  generate_cnf_clauses(gate_lines)

  #print(dimacs_clauses_list)


  #==================================================================================
  #'''
  # write the cnf encoding:
  f = open(args.output_file,"w")
  # writing the header line:
  f.write("p cnf " + str(max_index) + " " + str(len(dimacs_clauses_list)) + "\n")


  # qdimacs clauses:
  for line in dimacs_clauses_list:
    #print(line)
    string_line = ""
    for var in line:
      string_line += str(var) + " "
    string_line += "0\n"
    f.write(string_line)
  f.close()
  #'''
