# Irfansha Shaik, 30.06.2022, Aarhus

import argparse

import networkx as nx

# TODO: needs to handle the case where we generate the second player as black instead for the human played games:

# Main:
if __name__ == '__main__':
  text = "Takes a B-Gex input and generate Flipped B-Gex file"
  parser = argparse.ArgumentParser(description=text,formatter_class=argparse.RawTextHelpFormatter)
  parser.add_argument("--problem", help="problem file path")
  args = parser.parse_args()

    #=====================================================================================================================================
  # parsing:

  problem_path = args.problem
  f = open(problem_path, 'r')
  lines = f.readlines()

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

  #=====================================================================================================================================

  #=====================================================================================================================================
  # printing input files:
  # flipping the positions:
  print("#blackinitials")
  for pos in parsed_dict['#whiteinitials']:
    print(pos[0])
  print("#whiteinitials")
  for pos in parsed_dict['#blackinitials']:
    print(pos[0])
  print("#times")
  print(' '.join(parsed_dict["#times"][0]))
  print("#blackturns")
  print(' '.join(parsed_dict["#blackturns"][0]))
  print('#positions')
  print(' '.join(parsed_dict['#positions'][0]))
  print("#neighbours")
  for neighbour_list in parsed_dict['#neighbours']:
    print(' '.join(neighbour_list))
  # board size must be same as the length of the start boarder in B-Gex format:
  board_size = len(parsed_dict['#startboarder'][0])
  # using the standard boarder positions for the white player:
  print("#startboarder")
  cur_start_list = []
  for i in range(board_size):
    cur_start_list.append('a' + str(i+1))
  print(' '.join(cur_start_list))
  print("#endboarder")
  cur_end_list = []
  for i in range(board_size):
    cur_end_list.append(chr(ord('a') + board_size - 1) + str(i+1))
  print(' '.join(cur_end_list))
  #=====================================================================================================================================
