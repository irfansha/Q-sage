# Irfansha Shaik, 13.08.2021, Aarhus

import os

import utils.stuttering_bounds as sb

# Board vertexs are numbered from 0


class Parse:

  # Parses domain and problem file:
  def __init__(self, args):
    self.args = args
    problem_path = args.problem
    f = open(problem_path, 'r')
    lines = f.readlines()

    self.parsed_dict = {}

    # flag for unsat instance:
    self.unsolvable = 0

    # flag for solved instance:
    self.solved = 0

    for line in lines:
      stripped_line = line.strip("\n").strip(" ").split(" ")
      # we ignore if it is a comment:
      if ('%' == line[0] or line == '\n'):
        continue
      if ("#" in line):
        new_key = line.strip("\n")
        self.parsed_dict[new_key] = []
      else:
        self.parsed_dict[new_key].append(stripped_line)
    
    if (args.debug == 1):
      for key,value in self.parsed_dict.items():
        print(key, value)

    if (args.ignore_file_depth == 0):
      # If no times are provided in the input file:
      if (len(self.parsed_dict['#times']) == 0):
        self.depth = 0
      else:
        self.depth = len(self.parsed_dict['#times'][0])
    else:
      self.depth = args.depth

    #'''
    # It is possible to remove unreachable nodes from here:
    if (self.args.game_type == "hex" and self.args.remove_unreachable_nodes == 1):
      unreachable_nodes = sb.unreachable_nodes(self)

      # removing the unreachable nodes from the problem:
      # removing from positions:
      for node in unreachable_nodes:
        self.parsed_dict['#positions'][0].remove(node)

      # if positions empty then instance is unsolved:
      if (len(self.parsed_dict['#positions'][0]) == 0):
        self.unsolvable = 1

      # removing from neighours:
      temp_neighbour_list = []
      for neighbour_list in self.parsed_dict['#neighbours']:
        if (neighbour_list[0] in unreachable_nodes):
          continue
        else:
          temp_neighbours = []
          for cur_node in neighbour_list:
            if (cur_node in unreachable_nodes):
              continue
            else:
              temp_neighbours.append(cur_node)
          if (len(temp_neighbours) != 0):
            temp_neighbour_list.append(temp_neighbours)
      # updating the neighbours list:
      self.parsed_dict['#neighbours'] = temp_neighbour_list
      # removing from start positions:
      for node in unreachable_nodes:
        if (node in self.parsed_dict['#startboarder'][0]):
          self.parsed_dict['#startboarder'][0].remove(node)
      # removing from end positions:
      for node in unreachable_nodes:
        if (node in self.parsed_dict['#endboarder'][0]):
          self.parsed_dict['#endboarder'][0].remove(node)
    #'''

    self.positions = self.parsed_dict['#positions'][0]
    self.num_positions = len(self.parsed_dict['#positions'][0])


    if (self.args.game_type == "hex"):
      # Pushing already placed positions to the end, and renumbering variables accordingly:
      self.rearranged_positions = []

      if (args.renumber_positions == 1):
        print("Renumbering positions")
        # first gathering open positions:
        for pos in self.positions:
          if ([pos] not in self.parsed_dict['#blackinitials'] and [pos] not in self.parsed_dict['#whiteinitials']):
            self.rearranged_positions.append(pos)

        self.num_available_moves = len(self.rearranged_positions)

        # now appending black and white initials:
        for [pos] in self.parsed_dict['#blackinitials']:
          self.rearranged_positions.append(pos)
        for [pos] in self.parsed_dict['#whiteinitials']:
          self.rearranged_positions.append(pos)
      else:
        # simply using the original positions and num of available moves are all positions:
        self.rearranged_positions = self.positions
        self.num_available_moves = self.num_positions

      self.white_initial_positions = []
      self.black_initial_positions = []

      self.black_win_configurations = []
      self.white_win_configurations = []

      for initial in self.parsed_dict['#whiteinitials']:
        # Finding position of white initial var:
        # position = parsed_dict['#positions'][0].index(initial[0])
        # Finding var position from rearranged positions instead:
        position = self.rearranged_positions.index(initial[0])
        self.white_initial_positions.append(position)

      for initial in self.parsed_dict['#blackinitials']:
        # Finding position of black initial var:
        # position = parsed_dict['#positions'][0].index(initial[0])
        # Finding var position from rearranged positions instead:
        position = self.rearranged_positions.index(initial[0])
        self.black_initial_positions.append(position)


      # parsing the winning configurations:
      self.start_boarder = []
      for single_vertex in self.parsed_dict['#startboarder'][0]:
        position = self.rearranged_positions.index(single_vertex)
        self.start_boarder.append(position)

      self.end_boarder = []
      for single_vertex in self.parsed_dict['#endboarder'][0]:
        position = self.rearranged_positions.index(single_vertex)
        self.end_boarder.append(position)


      self.neighbour_dict = {}
      for neighbour_list in self.parsed_dict['#neighbours']:
        # The neighbours list contains itself as its first element, which is the key for the dict:
        cur_position = self.rearranged_positions.index(neighbour_list.pop(0))
        temp_list = []
        for neighbour in neighbour_list:
          if (neighbour != 'NA'):
            cur_neighbour = self.rearranged_positions.index(neighbour)
            temp_list.append(cur_neighbour)
          else:
            temp_list.append(neighbour)
        if (len(temp_list)  != 0):
          self.neighbour_dict[cur_position] = temp_list

      self.lower_bound_path_length = sb.lower_bound(self)

      # tight nieghbours for cp encoding:
      if (args.e == 'cp' and args.tight_neighbour_pruning == 1):
        self.tight_neighbour_pairs_list = sb.tight_neighbours(self)
        #print(self.tight_neighbour_pairs_list)

      # only for explicit goals, we generate the winning configurations:
      if (args.e == 'ew' or args.e == 'eg'):
        self.black_win_configurations, self.max_win_config_length = sb.all_short_simple_paths(self)

      if args.debug == 1:
        print("Depth: ",self.depth)
        print("Given positions: ", self.positions)
        print("Total positions: ", self.num_positions)
        print("Rearranged positions: ", self.rearranged_positions)
        print("Upper bound of allowed moves: ", self.num_available_moves)
        print("Black initial positions: ", self.black_initial_positions)
        print("White initial positions: ", self.white_initial_positions)
        print("Neighbour dict: ", self.neighbour_dict)
        print("Start boarder: ", self.start_boarder)
        print("End boarder: ", self.end_boarder)


    elif (self.args.game_type == "gomuku"):

      self.white_initial_positions = []
      self.black_initial_positions = []

      self.black_win_configurations = []
      self.white_win_configurations = []

      self.num_available_moves = len(self.positions)

      # Rewriting intial positions for gomuku based on indexes:
      for initial in self.parsed_dict['#whiteinitials']:
        # resetting the base to a, to get from 0:
        x_index = ord(initial[0][0]) - ord('a')
        y_index = int(initial[0][1:]) - 1
        self.white_initial_positions.append((x_index,y_index))

      for initial in self.parsed_dict['#blackinitials']:
        # resetting the base to a, to get from 0:
        x_index = ord(initial[0][0]) - ord('a')
        y_index = int(initial[0][1:]) - 1
        self.black_initial_positions.append((x_index,y_index))

      self.max_win_config_length = 0
      for win_conf in self.parsed_dict['#blackwins']:
        temp_conf = []
        for single_vertex in win_conf:
          # resetting the base to a, to get from 0:
          x_index = ord(single_vertex[0]) - ord('a')
          y_index = int(single_vertex[1:]) - 1
          temp_conf.append((x_index,y_index))
        # We only append if winning configuration is non-empty:
        if (len(temp_conf) != 0):
          self.black_win_configurations.append(temp_conf)
          # for gomuku this must be constant:
          if (len(temp_conf) > self.max_win_config_length):
            self.max_win_config_length = len(temp_conf)

      if args.debug == 1:
        print("Depth: ",self.depth)
        print("Given positions: ", self.positions)
        print("Total positions: ", self.num_positions)
        print("Black initial positions: ", self.black_initial_positions)
        print("White initial positions: ", self.white_initial_positions)
        print("Black win configurations: ", self.black_win_configurations)
        print("White win configurations: ", self.white_win_configurations)
