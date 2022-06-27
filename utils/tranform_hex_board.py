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
  args = parser.parse_args()

  #=====================================================================================================================================
  # paring:

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
  # computing start boarder:
  new_start_boarder = []
  # remembering integer values for neigbour simplification
  new_int_start_boarder = []

  for pos in start_boarder:
    if pos in white_initial_positions or len(new_neighbours_dict[pos]) == 0:
      continue
    elif pos in black_initial_positions:
      for cur_neighbour in new_neighbours_dict[pos]:
        if rearranged_positions[cur_neighbour] not in new_start_boarder and cur_neighbour not in black_initial_positions:
          new_start_boarder.append(rearranged_positions[cur_neighbour])
          new_int_start_boarder.append(cur_neighbour)
    else:
      if (rearranged_positions[pos] not in new_start_boarder):
        new_start_boarder.append(rearranged_positions[pos])
        new_int_start_boarder.append(pos)

  # computing new end boarder:
  new_end_boarder = []
  # remembering integer values for neigbour simplification
  new_int_end_boarder = []

  for pos in end_boarder:
    if pos in white_initial_positions or len(new_neighbours_dict[pos]) == 0:
      continue
    elif pos in black_initial_positions:
      for cur_neighbour in new_neighbours_dict[pos]:
        if rearranged_positions[cur_neighbour] not in new_end_boarder and cur_neighbour not in black_initial_positions:
          new_end_boarder.append(rearranged_positions[cur_neighbour])
          new_int_end_boarder.append(cur_neighbour)
    else:
      if (rearranged_positions[pos] not in new_end_boarder):
        new_end_boarder.append(rearranged_positions[pos])
        new_int_end_boarder.append(pos)
  #=====================================================================================================================================

  #=====================================================================================================================================
  # simplifying the neighbour dict:
  simplified_neighbour_dict = dict()

  # Simplifying graph by edges:
  for key,neighbour_list in new_neighbours_dict.items():
    # we only simplify the edges connected to each other in start and end boarders:
    if (key not in new_int_start_boarder and key not in new_int_end_boarder):
      simplified_neighbour_dict[key] = neighbour_list
      continue
    temp = []
    for neighbour in neighbour_list:
      if (key in new_int_start_boarder and neighbour in new_int_start_boarder):
        #print("start", rearranged_positions[key], rearranged_positions[neighbour])
        continue
      if (key in new_int_end_boarder and neighbour in new_int_end_boarder):
        #print("end", rearranged_positions[key], rearranged_positions[neighbour])
        continue
      else:
        temp.append(neighbour)
    if (len(temp) != 0):
      simplified_neighbour_dict[key] = temp
  #print(simplified_neighbour_dict)
  #=====================================================================================================================================

  #=====================================================================================================================================
  # removing unreachable nodes:
  # Computes the unreachable nodes i.e., any node which cannot be in the path from a start node to an end node:
  #-------------------------------------------------------------------------------
  G = nx.Graph()

  for key,neighbour_list in simplified_neighbour_dict.items():
    for neighbour in neighbour_list:
      G.add_edge(key, neighbour)

  max_path_length = int((len(parsed_dict["#times"][0]) + 1)/2)

  spl = dict(nx.all_pairs_shortest_path_length(G))

  #print(spl)

  num_available_moves = len(new_positions)

  #print(spl)
  count = 0
  unreachable_nodes_list = []
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

  #=====================================================================================================================================
  # printing input files:
  print("#blackinitials")
  print("#whiteinitials")
  print("#times")
  print(' '.join(parsed_dict["#times"][0]))
  print("#blackturns")
  print(' '.join(parsed_dict["#blackturns"][0]))
  print('#positions')
  temp_positions = []

  # asserting that no position is not in both start and end boarder:
  # removing any unreachable positions:
  for i in range(len(new_positions)):
    assert(i not in new_int_start_boarder or i not in new_int_end_boarder)
    # if position not in simplified_dict then no neighbours and we drop we it is unreachable:
    if (i in simplified_neighbour_dict and i not in unreachable_nodes_list):
      temp_positions.append(new_positions[i])
  print(' '.join(temp_positions))

  print("#neighbours")


  # Simplifying nieghbours based on unreachability:
  for key,neighbour_list in simplified_neighbour_dict.items():
    temp = []
    for neighbour in neighbour_list:
      if (neighbour not in unreachable_nodes_list):
        temp.append(neighbour)
    simplified_neighbour_dict[key] = temp

  # only add neighbours which are reachable:
  for key,neighbour_list in simplified_neighbour_dict.items():
    #print(rearranged_positions[key], neighbour_list)
    if key in white_initial_positions or key in black_initial_positions or key in unreachable_nodes_list:
      continue
    if (len(neighbour_list) == 0):
      continue
    temp_list = []
    for one_neighbour in neighbour_list:
      if (one_neighbour in black_initial_positions):
        continue
      temp_list.append(rearranged_positions[one_neighbour])
    print(rearranged_positions[key] + ' ' + ' '.join(temp_list))


  # dropping unreachable nodes:

  print("#startboarder")
  cur_boarder_list = []
  for pos in new_int_start_boarder:
    if pos not in simplified_neighbour_dict or pos in unreachable_nodes_list:
      continue
    if len(new_neighbours_dict[pos])!= 0:
      cur_boarder_list.append(rearranged_positions[pos])
  cur_boarder_list.sort()
  print(' '.join(cur_boarder_list))

  print("#endboarder")
  cur_boarder_list = []
  for pos in new_int_end_boarder:
    if pos not in simplified_neighbour_dict or pos in unreachable_nodes_list:
      continue
    if len(new_neighbours_dict[pos])!= 0:
      cur_boarder_list.append(rearranged_positions[pos])
  cur_boarder_list.sort()
  print(' '.join(cur_boarder_list))
  #=====================================================================================================================================
