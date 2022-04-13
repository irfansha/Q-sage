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

    if (args.ignore_file_depth == 0):
      # If no times are provided in the input file:
      if (len(parsed_dict['#times']) == 0):
        self.depth = 0
      else:
        self.depth = len(parsed_dict['#times'][0])
    else:
      self.depth = args.depth
    self.positions = parsed_dict['#positions'][0]
    self.num_positions = len(parsed_dict['#positions'][0])

    # Pushing already placed positions to the end, and renumbering variables accordingly:
    self.rearranged_positions = []

    if (args.renumber_positions == 1):
      # first gathering open positions:
      for pos in self.positions:
        if ([pos] not in parsed_dict['#blackinitials'] and [pos] not in parsed_dict['#whiteinitials']):
          self.rearranged_positions.append(pos)

      self.num_available_moves = len(self.rearranged_positions)

      # now appending black and white initials:
      for [pos] in parsed_dict['#blackinitials']:
        self.rearranged_positions.append(pos)
      for [pos] in parsed_dict['#whiteinitials']:
        self.rearranged_positions.append(pos)
    else:
      # simply using the original positions and num of available moves are all positions:
      self.rearranged_positions = self.positions
      self.num_available_moves = self.num_positions

    self.white_initial_positions = []
    self.black_initial_positions = []

    self.black_win_configurations = []
    self.white_win_configurations = []

    for initial in parsed_dict['#whiteinitials']:
      # Finding position of white initial var:
      # position = parsed_dict['#positions'][0].index(initial[0])
      # Finding var position from rearranged positions instead:
      position = self.rearranged_positions.index(initial[0])
      self.white_initial_positions.append(position)

    for initial in parsed_dict['#blackinitials']:
      # Finding position of black initial var:
      # position = parsed_dict['#positions'][0].index(initial[0])
      # Finding var position from rearranged positions instead:
      position = self.rearranged_positions.index(initial[0])
      self.black_initial_positions.append(position)


    # Depending on encoding we parse the winning configurations:
    if (args.e == 'pg' or args.e == 'cpg' or args.e == 'ttt' or args.e == 'cp' or args.e == 'cgcp' or args.e == 'ntpg'):
      self.neighbour_dict = {}
      for neighbour_list in parsed_dict['#neighbours']:
        # The neighbours list contains itself as its first element, which is the key for the dict:
        cur_position = self.rearranged_positions.index(neighbour_list.pop(0))
        temp_list = []
        for neighbour in neighbour_list:
          if (neighbour != 'NA'):
            cur_neighbour = self.rearranged_positions.index(neighbour)
            temp_list.append(cur_neighbour)
          else:
            temp_list.append(neighbour)
        self.neighbour_dict[cur_position] = temp_list
      self.start_boarder = []
      for single_vertex in parsed_dict['#startboarder'][0]:
        position = self.rearranged_positions.index(single_vertex)
        self.start_boarder.append(position)

      self.end_boarder = []
      for single_vertex in parsed_dict['#endboarder'][0]:
        position = self.rearranged_positions.index(single_vertex)
        self.end_boarder.append(position)

    else:

      # flag for already solved:
      self.solved = 0

      self.max_win_config_length = 0
      for win_conf in parsed_dict['#blackwins']:
        temp_conf = []
        count = 0
        for single_vextex in win_conf:
          # Finding position of black win vars:
          # position = parsed_dict['#positions'][0].index(single_vextex)
          # Finding var position from rearranged positions instead:
          position = self.rearranged_positions.index(single_vextex)
          # we do not need to check already black position in winning configurations:
          if (position not in self.black_initial_positions):
            temp_conf.append(position)
          else:
            count = count + 1
          if (position in self.white_initial_positions):
            # resetting if white position is found
            temp_conf = []
            break
        # We only append if winning configuration is non-empty and the length is atmost number of black turns:
        if (len(temp_conf) != 0 and len(temp_conf) <= int((self.depth+1)/2)):
          #print(temp_conf)
          self.black_win_configurations.append(temp_conf)
          if (len(temp_conf) > self.max_win_config_length):
            self.max_win_config_length = len(temp_conf)

        # if the black path is already ready satisfied i.e., all the positions are black, add only the first black position as winning configuration:
        if (count == len(win_conf)):
          self.solved = 1

      #assert(len(self.black_win_configurations) != 0)

      if (args.game_type != 'hex'):
        for win_conf in parsed_dict['#whitewins']:
          step_win_positions = []
          black_position_flag = 0
          for single_vextex in win_conf:
            # Finding position of white win vars:
            # position = parsed_dict['#positions'][0].index(single_vextex)
            # Finding var position from rearranged positions instead:
            position = self.rearranged_positions.index(single_vextex)
            # we do not need to check already black position in winning configurations:
            if (position in self.black_initial_positions):
              black_position_flag = 1
              continue
            step_win_positions.append(position)
          if (black_position_flag == 0):
            self.white_win_configurations.append(step_win_positions)
        #assert(len(self.white_win_configurations) != 0)


    if args.debug == 1:
      print("Depth: ",self.depth)
      print("Given positions: ", self.positions)
      print("Total positions: ", self.num_positions)
      print("Rearranged positions: ", self.rearranged_positions)
      print("Upper bound of allowed moves: ", self.num_available_moves)
      print("Black initial positions: ", self.black_initial_positions)
      print("White initial positions: ", self.white_initial_positions)
      if (args.e == 'pg'):
        print("Neighbour dict: ", self.neighbour_dict)
        print("Start boarder: ", self.start_boarder)
        print("End boarder: ", self.end_boarder)
      else:
        print("Black win configurations: ", self.black_win_configurations)
        print("White win configurations: ", self.white_win_configurations)
