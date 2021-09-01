# Irfansha Shaik, 01.09.2021, Aarhus.

import os, subprocess
import argparse


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

def print_to_file(file_path, parsed_dict):
  f = open(file_path, 'w')
  f.write("#blackinitials\n")
  for val in parsed_dict["#blackinitials"]:
    f.write(val[0]+ '\n')

  f.write("#whiteinitials\n")
  for val in parsed_dict["#whiteinitials"]:
    f.write(val[0] + '\n')

  f.write("#times\n")
  f.write(' '.join(parsed_dict["#times"][0]) + '\n')

  f.write("#blackturns\n")
  f.write(' '.join(parsed_dict["#blackturns"][0]) + '\n')

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
      return split_line[-1]
    if ("Plan not found" in line):
      return -1

# Main:
if __name__ == '__main__':
  text = "Plays interactively if a winning strategy is found for given depth, Q-sage is black player and takes the first move"
  parser = argparse.ArgumentParser(description=text,formatter_class=argparse.RawTextHelpFormatter)
  parser.add_argument("--problem", help="problem file path", default = 'testcases/Hein_hex/hein_04_3x3-05.pg')
  parser.add_argument("--depth", help="Depth, default 3", type=int,default = 3)

  args = parser.parse_args()
  # Reading the input problem file
  parsed_dict = parse(args.problem)
  # TODO: repeat the loop of running until either winning configuration is reached
  while (args.depth > 0):
    temp_input_file = "intermediate_files/interactive_problem_file"
    # Writing to temporary intermediate file:
    print_to_file(temp_input_file, parsed_dict)
    command = "python3 Q-sage.py --run 2 --ignore_file_depth 1 --depth " + str(args.depth) + " --problem " + temp_input_file + " > intermediate_files/interactive_output"
    subprocess.run([command], shell = True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT ,check=True)
    winning_move = read_winning_move("intermediate_files/interactive_output")
    if (winning_move == -1):
      print("Not deep enough, winning strategy not found")
      exit()
    else:
      print("Winning strategy found, Q-sage plays move: ",winning_move)
      args.depth = args.depth - 2
      if (args.depth <= 0):
        print("Q-sage wins! game complete")
      else:
        white_move = input("Enter your move: ")
        # updating the dictionary:
        parsed_dict["#blackinitials"].append([winning_move])
        parsed_dict["#whiteinitials"].append([white_move])