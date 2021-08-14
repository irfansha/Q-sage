# Irfansha Shaik, 13.08.2021, Aarhus

import os

# Board vertexs are numbered from 0


class Parse:

  # Parses domain and problem file:
  def __init__(self, args):
    self.args = args
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
    
    if (args.debug == 1):
      for key,value in parsed_dict.items():
        print(key, value)

    self.depth = len(parsed_dict['#times'][0])
    self.num_positions = len(parsed_dict['#positions'][0])

    self.white_initial_positions = []
    self.black_initial_positions = []

    self.black_win_configurations = []

    for initial in parsed_dict['#whiteinitials']:
      # Finding position of white initial var:
      position = parsed_dict['#positions'][0].index(initial[0])
      self.white_initial_positions.append(position)

    for initial in parsed_dict['#blackinitials']:
      # Finding position of black initial var:
      position = parsed_dict['#positions'][0].index(initial[0])
      self.black_initial_positions.append(position)


    for win_conf in parsed_dict['#blackwins']:
      temp_conf = []
      for single_vextex in win_conf:
        # Finding position of black win vars:
        position = parsed_dict['#positions'][0].index(single_vextex)
        temp_conf.append(position)
      self.black_win_configurations.append(temp_conf)
    
    if args.debug == 1:
      print("Depth: ",self.depth)
      print("Total positions: ", self.num_positions)
      print("Black initial positions: ", self.black_initial_positions)
      print("White initial positions: ", self.white_initial_positions)
      print("Black win configurations: ", self.black_win_configurations)