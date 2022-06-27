# Irfansha Shaik, 01.09.2021, Aarhus.

import argparse
import math
import random
import subprocess
import textwrap


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

def print_to_file(file_path, parsed_dict, args):
  f = open(file_path, 'w')
  f.write("#blackinitials\n")
  for val in parsed_dict["#blackinitials"]:
    f.write(val+ '\n')

  f.write("#whiteinitials\n")
  for val in parsed_dict["#whiteinitials"]:
    f.write(val + '\n')

  f.write("#times\n")
  f.write(' '.join(parsed_dict["#times"][0]) + '\n')

  f.write("#positions\n")
  f.write(' '.join(parsed_dict["#positions"][0]) + '\n')


  f.write("#blackwins\n")
  for win in parsed_dict["#blackwins"]:
    f.write(' '.join(win) + '\n')


  f.close()



def read_winning_move(file_path):
  f = open(file_path, 'r')
  lines = f.readlines()
  f.close()

  for line in lines:
    if ("First winning move" in line):
      split_line = line.split(" ")
      print("Plan found, winning move", split_line[-1].strip("\n"))
      return split_line[-1].strip("\n")
    if ("Plan not found" in line):
      print("Plan not found")
      return -1

# depending on the board position, corresponding symbol is returned:
def get_symbol(position, parsed_dict):
  if position in parsed_dict['#blackinitials']:
    return 'x'
  elif position in parsed_dict['#whiteinitials']:
    return 'o'
  else:
    return '-'



# Printing the board looking the parsed state of the board:
def print_board(board_size, parsed_dict):
  for i in range(board_size):
    temp = []
    for j in range(board_size):
      x_pos = chr(ord('a') + i)
      temp.append(get_symbol(x_pos + str(j+1), parsed_dict))
    print(''.join(temp))



# Main:
if __name__ == '__main__':
  text = "Plays interactively if a winning strategy is found for given depth, Q-sage is black player and takes the first move"
  parser = argparse.ArgumentParser(description=text,formatter_class=argparse.RawTextHelpFormatter)
  parser.add_argument("--problem", help="problem file path", default = 'testcases/gomuku_5_4_testcases/empty_5_4.pg')
  parser.add_argument("--seed", help="seed for random generater (default 0)", type=int,default = 0)
  parser.add_argument("--num_initial_moves", help="random inital moves by each player (default 2)", type=int,default = 2)
  parser.add_argument("--num_plays", help="number of random plays (default 10)", type=int,default = 10)

  args = parser.parse_args()
  #print(args)

  random.seed(args.seed)
  print("Initializing random generator with seed: ", args.seed)

  # Reading the input problem file
  parsed_dict = parse(args.problem)
  board_size = int(math.sqrt(len(parsed_dict['#positions'][0])))

  # Initializing open moves:
  moves = list(parsed_dict['#positions'][0])

  #print(moves)

  for index in range(args.num_plays):
    random.shuffle(moves)
    #print(moves)
    print("==================================================================================")
    parsed_dict["#blackinitials"] = list(moves[:args.num_initial_moves])
    parsed_dict["#whiteinitials"] = list(moves[args.num_initial_moves:2*args.num_initial_moves])

    print(parsed_dict['#blackinitials'])
    print(parsed_dict['#whiteinitials'])
    for i in range(3,9,2):
      print("------------------------------------------")
      print("Depth: ", i)
      # adding the first two positions to black moves and second two positions to white moves:
      parsed_dict["#blackinitials"] = list(moves[:args.num_initial_moves])
      parsed_dict["#whiteinitials"] = list(moves[args.num_initial_moves:2*args.num_initial_moves])
      temp_input_file = "intermediate_files/interactive_problem_file"
      # Writing to temporary intermediate file:
      print_to_file(temp_input_file, parsed_dict, args)
      command = "python3 Q-sage.py --run 2 -e ib --ignore_file_depth 1 --game_type gomuku --depth " + str(i) + " --problem " + temp_input_file + " > intermediate_files/interactive_output"
      subprocess.run([command], shell = True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT ,check=True)
      winning_move = read_winning_move("intermediate_files/interactive_output")
      if (winning_move != -1):
        parsed_dict["#blackinitials"].append(winning_move)
        print("Winning move:", winning_move)
        print_board(board_size, parsed_dict)
