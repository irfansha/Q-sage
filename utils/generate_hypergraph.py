# Irfansha Shaik, 30.06.2022, Aarhus

import argparse

import networkx as nx

# Main:
if __name__ == '__main__':
  text = "Takes a gex (with empty board) input and generate hypergraph is pg format"
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

  #for key,value in parsed_dict.items():
  #  print(key, value)

  positions = parsed_dict['#positions'][0]


  neighbour_dict = {}
  for neighbour_list in parsed_dict['#neighbours']:
    # The neighbours list contains itself as its first element, which is the key for the dict:
    cur_position = positions.index(neighbour_list.pop(0))
    temp_list = []
    for neighbour in neighbour_list:
      cur_neighbour = positions.index(neighbour)
      temp_list.append(cur_neighbour)
    neighbour_dict[cur_position] = temp_list
  start_boarder = []
  for single_vertex in parsed_dict['#startboarder'][0]:
    position = positions.index(single_vertex)
    start_boarder.append(position)

  end_boarder = []
  for single_vertex in parsed_dict['#endboarder'][0]:
    position = positions.index(single_vertex)
    end_boarder.append(position)

  #=====================================================================================================================================

  #=====================================================================================================================================
  # Computing hyper graph:
  #-------------------------------------------------------------------------------
  G = nx.Graph()

  for key,value_list in neighbour_dict.items():
    for value in value_list:
      G.add_edge(key, value)

  max_path_length = int((len(parsed_dict["#times"][0]) + 1)/2)

  all_final_paths = []

  for start in start_boarder:
    for end in end_boarder:
      paths = nx.all_simple_paths(G, source=start, target=end, cutoff=max_path_length-1)
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
  print(' '.join(positions))
  print("#blackwins")
  for win in all_final_paths:
    string_win = []
    for pos in win:
      string_win.append(positions[pos])
    print(' '.join(string_win))
  print("#whitewins")

  #=====================================================================================================================================
