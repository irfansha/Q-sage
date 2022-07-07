# Irfansha Shaik, 18.09.2021, Aarhus

import argparse
import string

import networkx as nx

white_initial_positions = []
black_initial_positions = []
new_neighbours_dict = {}


def find_neighbours(position, recursion_list):
  if (position in new_neighbours_dict):
    return new_neighbours_dict[position]

  recursion_list.append(position)
  new_current_neighbours = []
  for neighbour in neighbour_dict[position]:
    if(neighbour in white_initial_positions):
      continue
    elif (neighbour in black_initial_positions and neighbour not in recursion_list):
      temp_return_neighbours = find_neighbours(neighbour, recursion_list)
      for return_pos in temp_return_neighbours:
        if return_pos not in new_current_neighbours:
          new_current_neighbours.append(return_pos)
    else:
      if (neighbour not in new_current_neighbours):
        new_current_neighbours.append(neighbour)
  return new_current_neighbours


# Main:
if __name__ == '__main__':
  text = "Takes a hex board and converts in to another game with only open positions"
  parser = argparse.ArgumentParser(description=text,formatter_class=argparse.RawTextHelpFormatter)
  parser.add_argument("--problem", help="problem file path", default = 'testcases/winning_testcases_ungrounded/hein_04_3x3-05.pg')
  parser.add_argument("--prune_unreachable_nodes",  type=int, help="[0/1], default 0", default=0)
  parser.add_argument("--prune_minimal_path_unreachable_nodes",  type=int, help="[0/1], default 0", default=0)
  parser.add_argument("--ignore_file_depth", help="Ignore time stamps in input file and enforce user depth, default 0", type=int,default = 0)
  parser.add_argument("--depth", help="Depth, default 3", type=int,default = 3)
  parser.add_argument("--output_format", help="gex/egf(easy-graph-format) default=gex", default = 'gex')
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

  #for key,value in parsed_dict.items():
  #  print(key, value)

  if (args.ignore_file_depth == 0):
    depth = len(parsed_dict["#times"][0])
  else:
    depth = args.depth

  # Pushing already placed positions to the end, and renumbering variables accordingly:
  rearranged_positions = []
  new_positions = []

  positions = parsed_dict['#positions'][0]

  # first gathering open positions:
  for pos in positions:
    if ([pos] not in parsed_dict['#blackinitials'] and [pos] not in parsed_dict['#whiteinitials']):
      rearranged_positions.append(pos)
      new_positions.append(pos)

  num_available_moves = len(rearranged_positions)

  # now appending black and white initials:
  for [pos] in parsed_dict['#blackinitials']:
    rearranged_positions.append(pos)
  for [pos] in parsed_dict['#whiteinitials']:
    rearranged_positions.append(pos)

  for initial in parsed_dict['#whiteinitials']:
    # Finding position of white initial var:
    position = rearranged_positions.index(initial[0])
    white_initial_positions.append(position)

  for initial in parsed_dict['#blackinitials']:
    # Finding position of black initial var:
    position = rearranged_positions.index(initial[0])
    black_initial_positions.append(position)


  neighbour_dict = {}
  for neighbour_list in parsed_dict['#neighbours']:
    # The neighbours list contains itself as its first element, which is the key for the dict:
    cur_position = rearranged_positions.index(neighbour_list.pop(0))
    temp_list = []
    for neighbour in neighbour_list:
      cur_neighbour = rearranged_positions.index(neighbour)
      temp_list.append(cur_neighbour)
    neighbour_dict[cur_position] = temp_list
  start_boarder = []
  for single_vertex in parsed_dict['#startboarder'][0]:
    position = rearranged_positions.index(single_vertex)
    start_boarder.append(position)

  end_boarder = []
  for single_vertex in parsed_dict['#endboarder'][0]:
    position = rearranged_positions.index(single_vertex)
    end_boarder.append(position)

  #=====================================================================================================================================

  #=====================================================================================================================================
  # Finding neighbours recursively:

  for pos in range(len(positions)):
    if pos in white_initial_positions:
      continue
    return_neighbours = find_neighbours(pos, [])
    # If itself is a neighbour, we remove:
    if pos in return_neighbours:
      return_neighbours.remove(pos)
    new_neighbours_dict[pos] = return_neighbours

  #=====================================================================================================================================

  #=====================================================================================================================================
  # computing new start boarder:
  # remembering integer values for neigbour simplification
  new_int_start_boarder = []

  for pos in start_boarder:
    if pos in white_initial_positions or len(new_neighbours_dict[pos]) == 0:
      continue
    elif pos in black_initial_positions:
      for cur_neighbour in new_neighbours_dict[pos]:
        if cur_neighbour not in new_int_start_boarder and cur_neighbour not in black_initial_positions:
          new_int_start_boarder.append(cur_neighbour)
    else:
      if (pos not in new_int_start_boarder):
        new_int_start_boarder.append(pos)

  # computing new end boarder:
  # remembering integer values for neigbour simplification
  new_int_end_boarder = []

  for pos in end_boarder:
    if pos in white_initial_positions or len(new_neighbours_dict[pos]) == 0:
      continue
    elif pos in black_initial_positions:
      for cur_neighbour in new_neighbours_dict[pos]:
        if cur_neighbour not in new_int_end_boarder and cur_neighbour not in black_initial_positions:
          new_int_end_boarder.append(cur_neighbour)
    else:
      if (pos not in new_int_end_boarder):
        new_int_end_boarder.append(pos)
  #=====================================================================================================================================

  #=====================================================================================================================================
  # simplifying the neighbour dict:
  simplified_neighbour_dict = dict()

  # Simplifying graph by edges:
  for key,neighbour_list in new_neighbours_dict.items():
    # if the key is black we drop from the neighbour dictionary:
    if key in black_initial_positions:
      continue
    # asserting key is not in white positions, we do not compute white positions:
    assert(key not in white_initial_positions)


    # we only simplify the edges connected to each other in start and end boarders:
    if (key not in new_int_start_boarder and key not in new_int_end_boarder):
      temp_list = []
      for neighbour in neighbour_list:
        # asserting all its neighbours are not white:
        assert(neighbour not in white_initial_positions)
        # we do not need to add black positions:
        if (neighbour not in black_initial_positions):
          temp_list.append(neighbour)
      simplified_neighbour_dict[key] = temp_list
      continue
    temp = []
    for neighbour in neighbour_list:
      if (key in new_int_start_boarder and neighbour in new_int_start_boarder):
        #print("start", rearranged_positions[key], rearranged_positions[neighbour])
        continue
      if (key in new_int_end_boarder and neighbour in new_int_end_boarder):
        #print("end", rearranged_positions[key], rearranged_positions[neighbour])
        continue
      # we do not need to add black positions:
      if (neighbour in black_initial_positions):
        continue
      temp.append(neighbour)
    if (len(temp) != 0):
      simplified_neighbour_dict[key] = temp
  #print(simplified_neighbour_dict)

  # simplifying positions:
  simplified_positions = []
  for i in range(len(new_positions)):
    # if a position in both start and end boarder then problem is already solved:
    #assert(i not in new_int_start_boarder or i not in new_int_end_boarder)
    # if position not in simplified_dict then no neighbours:
    if (i in simplified_neighbour_dict):
      simplified_positions.append(i)

  # simplifying start, end boarder again as some of the neighbour relations much have become empty:
  temp_start_boarder = []
  for pos in new_int_start_boarder:
    if pos in simplified_neighbour_dict:
      temp_start_boarder.append(pos)
  new_int_start_boarder = list(temp_start_boarder)

  temp_end_boarder = []
  for pos in new_int_end_boarder:
    if pos in simplified_neighbour_dict:
      temp_end_boarder.append(pos)
  new_int_end_boarder = list(temp_end_boarder)
  #=====================================================================================================================================

  #=====================================================================================================================================
  # removing unreachable nodes:
  # Computes the unreachable nodes i.e., any node which cannot be in the path from a start node to an end node:
  #-------------------------------------------------------------------------------
  unreachable_nodes_list = []
  if (args.prune_unreachable_nodes == 1):
    G = nx.Graph()

    for key,neighbour_list in simplified_neighbour_dict.items():
      for neighbour in neighbour_list:
        G.add_edge(key, neighbour)

    max_path_length = int((depth + 1)/2)

    spl = dict(nx.all_pairs_shortest_path_length(G))

    #print(spl)

    num_available_moves = len(new_positions)

    #print(spl)
    count = 0
    for pos in range(num_available_moves):
      if (pos not in spl):
        continue
      # setting the min length to maximum value:
      min_start_length = num_available_moves
      for start in new_int_start_boarder:
        if (start not in spl[pos]):
          continue
        if (min_start_length > spl[pos][start]):
          min_start_length = spl[pos][start]
      # setting the min length to maximum value:
      min_end_length = num_available_moves
      for end in new_int_end_boarder:
        if (end not in spl[pos]):
          continue
        if (min_end_length > spl[pos][end]):
          min_end_length = spl[pos][end]
      if (min_start_length+min_end_length > max_path_length - 1):
        unreachable_nodes_list.append(pos)
        #print(pos,min_start_length,min_end_length)
        count = count + 1
    #print("Removing unreachable nodes ... " + str(count) + " unreachable out of " + str(num_available_moves))
    #print(unreachable_nodes_list)

  #-------------------------------------------------------------------------------
  #=====================================================================================================================================

  if (args.prune_unreachable_nodes == 1):
    # first trim the neighbour dict based on unreachability:
    pruned_simplified_neighbour_dict = dict()
    # Simplifying nieghbours based on unreachability:
    for key,neighbour_list in simplified_neighbour_dict.items():
      if key in unreachable_nodes_list:
        continue
      temp_list = []
      for one_neighbour in neighbour_list:
        # we do not add the black initial positions, should not be present here:
        assert(one_neighbour not in black_initial_positions)
        if (one_neighbour in unreachable_nodes_list):
          continue
        temp_list.append(one_neighbour)
      if len(temp_list) == 0:
        continue
      pruned_simplified_neighbour_dict[key] = temp_list

    simplified_neighbour_dict = pruned_simplified_neighbour_dict.copy()

    # pruning the  empty nodes in the start and end boarder nodes, due to unreachability:
    temp_start_boarder = []
    for pos in new_int_start_boarder:
      if pos in simplified_neighbour_dict:
        temp_start_boarder.append(pos)
    new_int_start_boarder = list(temp_start_boarder)

    temp_end_boarder = []
    for pos in new_int_end_boarder:
      if pos in simplified_neighbour_dict:
        temp_end_boarder.append(pos)
    new_int_end_boarder = list(temp_end_boarder)


    # pruning the empty nodes in positions due to unreachability:
    temp_simplified_positions = []
    for pos in simplified_positions:
      if pos in simplified_neighbour_dict:
        temp_simplified_positions.append(pos)
    simplified_positions = list(temp_simplified_positions)
  #=====================================================================================================================================



  #=====================================================================================================================================
  # Computing hyper graph:
  #-------------------------------------------------------------------------------
  minimal_unreachable_path_nodes = []
  if (args.prune_minimal_path_unreachable_nodes == 1):
    min_G = nx.Graph()

    for key,value_list in simplified_neighbour_dict.items():
      for value in value_list:
        min_G.add_edge(key, value)

    max_path_length = int((depth + 1)/2)

    all_final_paths = []

    #print(new_int_start_boarder)
    #print(new_int_end_boarder)

    for start in new_int_start_boarder:
      for end in new_int_end_boarder:
        paths = nx.all_simple_paths(min_G, source=start, target=end, cutoff=max_path_length-1)
        plist = list(paths)

        set_list = []
        for path in plist:
          set_list.append(set(path))

        # sorting the set_list based on path lengths:
        set_list.sort(key=len)
        # For now, quadratic complexity loops:

        final_small_paths = []

        list_for_avail_paths = list(set_list)
        # checking each path one at a time:
        for path in set_list:
          remove_path_list = []
          # if the current path is not in the avail list then it has been supersumed and remove already, we do not need to do it again:
          if path not in list_for_avail_paths:
              continue
          for temp_path in list_for_avail_paths:
            intersection = set.intersection(path, temp_path)
            if path == intersection:
              remove_path_list.append(temp_path)
            # if the temp_path in the avialable paths is same as intersection, that means the temp_path is same as the path we are checking for:
            if (temp_path == intersection):
              assert(path == temp_path)
          # first removing the large paths:
          for remove_path in remove_path_list:
            list_for_avail_paths.remove(remove_path)
          # adding the current small path:
          final_small_paths.append(path)
        if (len(final_small_paths) != 0):
          # adding all the final small paths:
          for small_path in final_small_paths:
            small_path = list(small_path)
            small_path.sort()
            all_final_paths.append(list(small_path))
          #print(start, end)
          #print(final_small_paths)
    # iterate through the paths and compute the unreachable nodes:
    touched_positions = []
    for win in all_final_paths:
      for pos in win:
        if (pos not in touched_positions):
          touched_positions.append(pos)
    for sim_pos in simplified_positions:
      if sim_pos not in touched_positions:
        minimal_unreachable_path_nodes.append(sim_pos)
    #print(minimal_unreachable_path_nodes)
  #-------------------------------------------------------------------------------
  # dropping the minimal unreachable positions:
  if (args.prune_minimal_path_unreachable_nodes == 1):
    # first trim the neighbour dict based on minimal unreachability:
    pruned_minimal_simplified_neighbour_dict = dict()
    # Simplifying nieghbours based on minimal unreachability:
    for key,neighbour_list in simplified_neighbour_dict.items():
      if key in minimal_unreachable_path_nodes:
        continue
      temp_list = []
      for one_neighbour in neighbour_list:
        # we do not add the black initial positions, should not be present here:
        assert(one_neighbour not in black_initial_positions)
        if (one_neighbour in minimal_unreachable_path_nodes):
          continue
        temp_list.append(one_neighbour)
      if len(temp_list) == 0:
        continue
      pruned_minimal_simplified_neighbour_dict[key] = temp_list

    simplified_neighbour_dict = pruned_minimal_simplified_neighbour_dict.copy()

    # pruning the  empty nodes in the start and end boarder nodes, due to unreachability:
    temp_start_boarder = []
    for pos in new_int_start_boarder:
      if pos in simplified_neighbour_dict:
        temp_start_boarder.append(pos)
    new_int_start_boarder = list(temp_start_boarder)

    temp_end_boarder = []
    for pos in new_int_end_boarder:
      if pos in simplified_neighbour_dict:
        temp_end_boarder.append(pos)
    new_int_end_boarder = list(temp_end_boarder)

    # pruning the empty nodes in positions due to unreachability:
    temp_simplified_positions = []
    for pos in simplified_positions:
      if pos in simplified_neighbour_dict:
        temp_simplified_positions.append(pos)
    simplified_positions = list(temp_simplified_positions)

  #=====================================================================================================================================
  # printing input files:
  print("#blackinitials")
  print("#whiteinitials")
  # times to be appended:
  times_string = ''
  black_times_string = ''
  for i in range(depth):
    times_string = times_string + 't' + str(i+1) + " "
    if (i % 2 == 0):
      black_times_string = black_times_string + 't' + str(i+1) + " "

  times_string = times_string.strip(" ")
  black_times_string = black_times_string.strip(" ")


  print("#times")
  print(times_string)
  print("#blackturns")
  print(black_times_string)
  print('#positions')

  temp_positions = []
  # printing simplified positions:
  for pos in simplified_positions:
      temp_positions.append(rearranged_positions[pos])
  if (len(temp_positions) != 0):
    print(' '.join(temp_positions))

  if (args.output_format == "gex"):
    print("#neighbours")
  elif (args.output_format == "egf"):
    print("#edges")


  # for easy graph format we need to remove symmetric edges, so keeping track of them:
  added_edges = []

  # only add neighbours which are reachable:
  for key,neighbour_list in simplified_neighbour_dict.items():
    # for printing, we revert to original position names:
    temp_list = []
    for neighbour in neighbour_list:
      temp_list.append(rearranged_positions[neighbour])
    if (args.output_format == "gex"):
      print(rearranged_positions[key] + ' ' + ' '.join(temp_list))
    elif (args.output_format == "egf"):
      for cur_neighbour in temp_list:
        # we only add if the edge is not already added:
        if ((rearranged_positions[key], cur_neighbour) in added_edges or (cur_neighbour, rearranged_positions[key]) in added_edges):
          continue
        print(rearranged_positions[key] + ' ' + cur_neighbour)
        # now add the edge in the list:
        added_edges.append((rearranged_positions[key], cur_neighbour))

  # printing start boarder:
  if (args.output_format == "gex"):
    print("#startboarder")
  cur_boarder_list = []
  for pos in new_int_start_boarder:
    cur_boarder_list.append(rearranged_positions[pos])
  cur_boarder_list.sort()
  if (args.output_format == "gex"):
    if (len(cur_boarder_list) != 0):
      print(' '.join(cur_boarder_list))
  elif (args.output_format == "egf"):
    for cur_start_pos in cur_boarder_list:
      print("S " + cur_start_pos)

  # printing end boarder:
  if (args.output_format == "gex"):
    print("#endboarder")
  cur_boarder_list = []
  for pos in new_int_end_boarder:
    cur_boarder_list.append(rearranged_positions[pos])
  cur_boarder_list.sort()
  if (args.output_format == "gex"):
    if (len(cur_boarder_list) != 0):
      print(' '.join(cur_boarder_list))
  elif (args.output_format == "egf"):
    for cur_end_pos in cur_boarder_list:
      print("T " + cur_end_pos)

  if (args.output_format == "egf"):
    print("#source\nS\n#target\nT")
  #=====================================================================================================================================
