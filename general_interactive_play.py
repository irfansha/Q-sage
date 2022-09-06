# Irfansha Shaik, 06.09.2022, Aarhus.

import argparse
import textwrap

from pysat.formula import CNF
from pysat.solvers import Minisat22

# predicate map:
# open  : -
# black : B
# white : W
pred_map = {'00':'-', '01':'-','10':'B','11':'W'}

def parse(problem_path):
  f = open(problem_path, 'r')
  lines = f.readlines()
  f.close()

  parsed_dict = {}

  for line in lines:
    stripped_line = line.strip("\n").strip(" ").split(" ")
    # we ignore if it is a comment:
    if ('%' == line[0] or line == '\n'):
      continue
    if ("#" in line):
      new_key = line.strip("\n")
      parsed_dict[new_key] = []
    else:
      parsed_dict[new_key].append(stripped_line)
  return parsed_dict


# Takes a list of clause variables and maps to a integer value:
def generate_binary_format(clause_variables, corresponding_number):
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


# Printing the board looking the parsed state of the board:
def print_board(board_size_x, board_size_y, board_state):

  for j in range(board_size_y):
    row_string_list = []
    for i in range(board_size_x):
      row_string_list.append(board_state[(i,j)])
    print(' '.join(row_string_list))


# runs the sat solver with assumption and returns a model:
def run_sat_solver(m, assm):
  m.solve(assumptions=assm)
  return m.get_model()



# Main:
if __name__ == '__main__':
  text = "Given a certificate and meta input for a game, plays interactively and checks if the winning condition is satisfied"
  parser = argparse.ArgumentParser(description=text,formatter_class=argparse.RawTextHelpFormatter)
  parser.add_argument("--certificate_path", help="certificate path", default = 'intermediate_files/certificate.cnf')
  parser.add_argument("--meta_path", help="meta information for game file path", default = 'intermediate_files/viz_meta_out')
  parser.add_argument("--player", help=textwrap.dedent('''
                                  player type:
                                  user = interactive user play (default)
                                  random = random player, playes random move'''),default = 'user')
  parser.add_argument("--seed", help="seed value for random generater (default 0)", type=int,default = 0)

  args = parser.parse_args()
  print(args)

  # Reading the input problem file
  parsed_dict = parse(args.meta_path)
  print(parsed_dict)

  # Initialising required info
  board_size_x = int(parsed_dict["#boardsize"][0][0])
  board_size_y = int(parsed_dict["#boardsize"][0][1])

  symb_pos_x, symb_pos_y = parsed_dict["#symbolicpos"][0]
  symb_pos_x_list = symb_pos_x.strip("[").strip("]").split(",")
  symb_pos_y_list = symb_pos_y.strip("[").strip("]").split(",")

  # mapping to int:
  symb_pos_x_list = [int(x) for x in symb_pos_x_list]
  symb_pos_y_list = [int(y) for y in symb_pos_y_list]


  state_vars = parsed_dict["#statevars"]


  formula = CNF(from_file=args.certificate_path)

  m = Minisat22(bootstrap_with=formula.clauses)


  print(symb_pos_x_list,symb_pos_y_list)

  print(state_vars[0])

  board_state = dict()

  # just printing the initial state for now:
  for j in range(board_size_y):
    for i in range(board_size_x):
      cur_sym_pos_list = []
      cur_sym_pos_list.extend(generate_binary_format(symb_pos_x_list, i))
      cur_sym_pos_list.extend(generate_binary_format(symb_pos_y_list, j))
      cur_model = run_sat_solver(m, cur_sym_pos_list)
      bin_string = ''
      # getting the values of state vars:
      for var in state_vars[0]:
        if (int(var) in cur_model):
          bin_string += '1'
        elif (-(int(var)) in cur_model):
          bin_string += '0'
        else:
          print("Error")
      board_state[(i,j)] = pred_map[bin_string]
  print_board(board_size_x,board_size_y,board_state)
