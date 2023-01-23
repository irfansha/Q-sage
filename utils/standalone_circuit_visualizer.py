# Irfansha Shaik, 08.12.2022, Aarhus

import argparse

from pyvis.network import Network
#import networkx as nx

# for each variable/gate we specify the level (in matrix)
level_dict = dict()

# inverse level dict, can be used to append to matrix in appropriate levels:
inverse_level_dict = dict()

# parsed matrix, without circuit keywords:
parsed_matrix = []

parsed_matrix_dict = {}

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

  for line in parsed_matrix:
    for var in line[1]:
      parsed_matrix_dict[int(var)] = line[0]
      #print(var,line[0])

#==========================================================================================


#==========================================================================================
# Parse gate lines:
def parse_gates(gate_lines):
  for line in gate_lines:
    if (line == "\n" or len(line) == 0):
        continue
    #print(line, len(line), [line])
    # asserting the line is part of gate:
    assert("or" in line or "and" in line)
    # removing spaces
    cleaned_line = line.replace(" ","")
    if ("or" in cleaned_line):
      # first seperating intermediate gate:
      [cur_gate, cur_list] = cleaned_line.split("=")
      cur_var_list = cur_list.strip("or(").strip(")").split(",")
      # if empty gate, we make the list empty:
      if (cur_var_list == ['']):
        cur_var_list = []
      cur_type = 'or'
    else:
      assert("and" in cleaned_line)
      # first seperating intermediate gate:
      [cur_gate, cur_list] = cleaned_line.split("=")
      cur_var_list = cur_list.strip("and(").strip(")").split(",")
      # if empty gate, we make the list empty:
      if (cur_var_list == ['']):
        cur_var_list = []
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


# Main:
if __name__ == '__main__':
  text = "Takes a qcir instance and visualises"
  parser = argparse.ArgumentParser(description=text,formatter_class=argparse.RawTextHelpFormatter)
  parser.add_argument("--input", help="qcir instance path")
  args = parser.parse_args()


  f = open(args.input,"r")
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

  #print(parsed_matrix)

  # Parse gate lines:
  parse_gates(gate_lines)


  net = Network()

  nodes = []

  for line in parsed_gate_lines:
    print(line)
    if (len(line) > 1):
      gate_type = line[0]
      out_var = int(line[1])
      in_vars = line[2]
      #print(gate_type, out_var, in_vars)
      if (out_var not in nodes):
        nodes.append(out_var)
        assert(out_var not in parsed_matrix_dict)
        net.add_node(out_var, label=str(out_var))
      # adding edges for each in_vars to out_var:
      for in_var in in_vars:
        in_var = int(in_var)
        # if negative:
        if (in_var < 0):
          non_neg_var = -in_var
          # first setting nodes if not available:
          if (non_neg_var not in nodes):
            #print(non_neg_var)
            nodes.append(non_neg_var)
            if (parsed_matrix_dict[non_neg_var] == 'a'):
              #print("universal")
              net.add_node(non_neg_var, label=str(non_neg_var),color="red")
            else:
              assert(parsed_matrix_dict[non_neg_var] == 'e')
              #print(non_neg_var)
              net.add_node(non_neg_var, label=str(non_neg_var),color="green")
          net.add_edge(non_neg_var,out_var, color="red")
        else:
          # first setting nodes if not available:
          if (in_var not in nodes):
            nodes.append(in_var)
            if (parsed_matrix_dict[in_var] == 'a'):
              #print("universal")
              net.add_node(in_var, label=str(in_var),color="red")
            else:
              assert(parsed_matrix_dict[in_var] == 'e')
              #print(in_var)
              net.add_node(in_var, label=str(in_var),color="green")
          net.add_edge(in_var,out_var, color="blue")
          #----------------------------------------------

  #net.show_buttons(filter_=['physics','layout', 'edges'])
  '''
  net.set_options("""
    const options = {
    "edges": {
    "arrows": {
    "to": {
    "enabled": true
    }
    },
    "color": {
    "inherit": true
    },
    "selfReferenceSize": null,
    "selfReference": {
    "angle": 0.7853981633974483
    },
    "smooth": false
    },
    "layout": {
    "hierarchical": {
    "enabled": true,
    "sortMethod": "directed"
    }
    },
    "physics": {
    "enabled": false,
    "hierarchicalRepulsion": {
    "centralGravity": 0,
    "avoidOverlap": null
    },
    "minVelocity": 0.75,
    "solver": "hierarchicalRepulsion"
    }
    }
    """)
   '''

  net.set_options("""
    const options = {
    "edges": {
        "arrows": {
        "to": {
            "enabled": true
        }
        },
        "color": {
        "inherit": true
        },
        "hoverWidth": 8,
        "selfReferenceSize": null,
        "selfReference": {
        "angle": 0.7853981633974483
        },
        "smooth": false
    },
    "layout": {
        "hierarchical": {
        "enabled": true,
        "levelSeparation": 475,
        "nodeSpacing": 40,
        "treeSpacing": 430,
        "sortMethod": "directed"
        }
    },
    "physics": {
        "hierarchicalRepulsion": {
        "centralGravity": 0,
        "avoidOverlap": null
        },
        "minVelocity": 0.75,
        "solver": "hierarchicalRepulsion"
    }
    }
  """)

  net.show('mygraph2.html')