# Irfansha Shaik, 06.09.2022, Aarhus.

import argparse
import os
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

# takes a list of vars and a model, returns the binary string based on the model:
def get_binary_string(vars, cur_model):
  bin_string = ''
  # getting the values of state vars:
  for var in vars:
    if (int(var) in cur_model):
      bin_string += '1'
    elif (-(int(var)) in cur_model):
      bin_string += '0'
    else:
      print("Error")

  return bin_string


# takes a list of vars and a model, returns the specific assignment for the vars given in the model:
def get_model_assignmet(vars, cur_model):
  assg_lst = []
  # getting the values of state vars:
  for var in vars:
    if (int(var) in cur_model):
      assg_lst.append(int(var))
    elif (-(int(var)) in cur_model):
      assg_lst.append(-int(var))
    else:
      print("Error")

  return assg_lst


# takes the integer indexes and return the board index for example 'a1' for 1,0
def get_index(x,y):
  return chr(97+x)+str(y+1)

# Printing the board looking the parsed state of the board:
def print_board(board_size_x, board_size_y, board_state):

  index_line = '  '
  for i in range(board_size_x):
    #index_line += chr(97+i) + " "
    index_line += str(i+1) + " "

  print(index_line)

  for j in range(board_size_y):
    row_string_list = []
    for i in range(board_size_x):
      row_string_list.append(board_state[(i,j)])
    print(str(j+1) + " " + ' '.join(row_string_list))


# runs the sat solver with assumption and returns a model:
def run_sat_solver(m, assm):
  m.solve(assumptions=assm)
  return m.get_model()



# Main:
if __name__ == '__main__':
  text = "Given a certificate and meta input for a game, plays interactively and checks if the winning condition is satisfied/n handle both ascii-aiger and cnf formats for certificates"
  parser = argparse.ArgumentParser(description=text,formatter_class=argparse.RawTextHelpFormatter)
  parser.add_argument("--certificate_path", help="certificate path", default = 'testcases/index_general_certificates/httt_4_4_tic/certificate.cnf')
  parser.add_argument("--meta_path", help="meta information for game file path", default = 'testcases/index_general_certificates/httt_4_4_tic/viz_meta_out')
  parser.add_argument("--player", help=textwrap.dedent('''
                                  player type:
                                  user = interactive user play (default)
                                  random = random player, playes random move'''),default = 'user')
  parser.add_argument("--seed", help="seed value for random generater (default 0)", type=int,default = 0)

  args = parser.parse_args()
  print(args)

  # Reading the input problem file
  parsed_dict = parse(args.meta_path)

  # Initialising required info
  board_size_x = int(parsed_dict["#boardsize"][0][0])
  board_size_y = int(parsed_dict["#boardsize"][0][1])

  depth = int(parsed_dict["#depth"][0][0])

  # for now we assume y_vars hold by default:
  y_vars = 1

  action_vars = []

  for cur_act_var in parsed_dict["#actionvars"]:
    single_action = []
    for single_var_lst in cur_act_var:
      if (len(single_var_lst) != 0):
        cur_int_lst = single_var_lst.strip("[").strip("]").split(",")
        # handling empty parameters:
        if ([""] != cur_int_lst):
          #print(cur_int_lst, len(cur_int_lst))
          cur_int_lst = [int(x) for x in cur_int_lst]
          single_action.append(cur_int_lst)
        else:
          y_vars = 0
          single_action.append([])
    action_vars.append(single_action)
  print(action_vars)

  symb_pos_x, symb_pos_y = parsed_dict["#symbolicpos"][0]
  symb_pos_x_list = symb_pos_x.strip("[").strip("]").split(",")
  symb_pos_y_list = symb_pos_y.strip("[").strip("]").split(",")

  # mapping to int:
  symb_pos_x_list = [int(x) for x in symb_pos_x_list]
  symb_pos_y_list = [int(y) for y in symb_pos_y_list]


  state_vars = parsed_dict["#statevars"]

  # checking the first line of the file for the certificate type:
  with open(args.certificate_path,"r") as f:
    first_line = f.readline()

  if ("cnf" in first_line):
    formula = CNF(from_file=args.certificate_path)
  else:
    # first converting aiger to cnf:
    cnf_translator_command = "python3 utils/aag_to_dimacs.py --input_file " + args.certificate_path + " > intermediate_files/translated_cert.cnf"
    os.system(cnf_translator_command)
    formula = CNF(from_file="intermediate_files/translated_cert.cnf")

    #print(formula)

  m = Minisat22(bootstrap_with=formula.clauses)


  #print(symb_pos_x_list,symb_pos_y_list)

  #print(state_vars[0])

  # for assumption we remember the moves played
  moves_played_vars = []

  for k in range(depth+1):

    print("time step:", k)

    board_state = dict()

    # just printing the board state:
    for j in range(board_size_y):
      for i in range(board_size_x):
        cur_sym_pos_list = []
        cur_sym_pos_list.extend(generate_binary_format(symb_pos_x_list, i))
        cur_sym_pos_list.extend(generate_binary_format(symb_pos_y_list, j))

        # adding move assumptions and specific universal branch:
        all_assumptions = list(cur_sym_pos_list)
        all_assumptions.extend(moves_played_vars)

        #print(all_assumptions)

        cur_model = run_sat_solver(m, all_assumptions)
        #print(all_assumptions, cur_model)
        bin_string = get_binary_string(state_vars[k], cur_model)
        #print(state_vars[k],bin_string)
        board_state[(i,j)] = pred_map[bin_string]
    print_board(board_size_x,board_size_y,board_state)

    #print("move at time step:", k+1)

    # if black player move then we get the winning move:
    if (k%2 == 0):
      cur_move_model = run_sat_solver(m,moves_played_vars)
      #print(moves_played_vars)
      action_name_bin = get_binary_string(action_vars[k][0], cur_move_model)
      cur_action_name = parsed_dict["#blackactions"][int(action_name_bin,2)][0].split("(")[0]

      move_x_bin = get_binary_string(action_vars[k][1], cur_move_model)
      if (y_vars != 0):
        move_y_bin = get_binary_string(action_vars[k][2], cur_move_model)

      #print(move_y_bin)
      #print("\nmove played by black:", cur_action_name+ "(" +get_index(int(move_x_bin,2), int(move_y_bin,2)) + ")")
      # for now handling connect4 only column moves:
      if (y_vars != 0):
        print("\nMove played by black:", cur_action_name+ "(" +str(int(move_x_bin,2)+1)+ "," + str(int(move_y_bin,2)+1) + ")")
        for i in range(3):
          moves_played_vars.extend(get_model_assignmet(action_vars[k][i], cur_move_model))
      else:
        print("\nMove played by black:", cur_action_name+ "(" +str(int(move_x_bin,2)+1) + ")")
        for i in range(3):
          moves_played_vars.extend(get_model_assignmet(action_vars[k][i], cur_move_model))
      #print(moves_played_vars)
    # if white player (for now user), then we get the move from terminal:
    elif (k < depth):
      white_move = input("\nEnter your white move: ")
      white_move_name = white_move.strip(")").split("(")[0]
      #print(white_move_name)

      # getting the index of the action name:
      for i in range(len(parsed_dict["#whiteactions"])):
        if white_move_name in parsed_dict["#whiteactions"][i][0]:
          white_action_name_index = i

      # the board starts with 'a' so mapping to zero:
      #white_move_index_x = ord(white_move_index[0]) - 97
      # the boolean vars mapped to zero:
      #white_move_index_y = int(white_move_index[1:]) - 1
      white_move_indices = white_move.strip(")").split("(")[1].split(",")
      white_move_index_x = int(white_move_indices[0])-1
      if (y_vars != 0):
        white_move_index_y = int(white_move_indices[1])-1


      #print(white_move_index_x, white_move_index_y)

      white_move_assignment = []

      # when there is only one action, it is existential:
      if (len(parsed_dict["#whiteactions"]) > 1):
        white_move_assignment.extend(generate_binary_format(action_vars[k][0], white_action_name_index))
      white_move_assignment.extend(generate_binary_format(action_vars[k][1], white_move_index_x))
      if (y_vars != 0):
        white_move_assignment.extend(generate_binary_format(action_vars[k][2], white_move_index_y))

      #print(white_move_assignment)
      # adding the white move assignment to the moves played for later assumptions:
      moves_played_vars.extend(white_move_assignment)
