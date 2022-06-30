import networkx as nx


def lower_bound(parser):
  if (parser.args.debug > -1):
    print("Computing lower bounds for stuttering")
  G = nx.Graph()

  for key,value_list in parser.neighbour_dict.items():
    for value in value_list:
      G.add_edge(key, value)

  max_path_length = len(parser.black_initial_positions) + int((parser.depth + 1)/2)

  spl = dict(nx.all_pairs_shortest_path(G, max_path_length-1))


  # initializing minimum length with the max path length:
  min_length = max_path_length

  for start in parser.start_boarder:
    for end in parser.end_boarder:
      if (start in spl):
        if (end in spl[start]):
          if (len(spl[start][end]) < min_length):
            min_length = len(spl[start][end])
          #print(spl[start][end])


  return min_length


def tight_neighbours(parser):
  if (parser.args.debug > -1):
    print("Computing tight neighbours based on winning path position")

  # computing simple paths:
  G = nx.Graph()

  for key,value_list in parser.neighbour_dict.items():
    for value in value_list:
      G.add_edge(key, value)

  max_path_length = len(parser.black_initial_positions) + int((parser.depth + 1)/2)

  all_simple_paths = []

  for start in parser.start_boarder:
    for end in parser.end_boarder:
      paths = nx.all_simple_paths(G, source=start, target=end, cutoff=max_path_length-1)
      plist = list(paths)
      all_simple_paths.extend(plist)

  # getting the minimal paths:
  all_minimal_paths, max_length = all_short_simple_paths(parser)

  # only paths of minimals paths:
  original_minimal_paths = []
  for path in all_simple_paths:
    # we only consider the minimal paths for tight nieghbours:
    # using set to make sure there are no duplicates, which should not be there:
    cur_path_set = list(set(path))
    cur_path_set.sort()
    assert(len(cur_path_set) == len(path))
    if cur_path_set in all_minimal_paths:
      original_minimal_paths.append(path)
  #print(len(original_minimal_paths))

  all_pairs_list = []
  # grouping the pair of nodes for each time step:
  for i in range(max_path_length-1):
    cur_pairs_list = []
    for path in original_minimal_paths:
      if (len(path)-2 < i):
        continue
      else:
        if ((path[i],path[i+1]) not in cur_pairs_list):
          cur_pairs_list.append((path[i],path[i+1]))
    cur_pairs_list.sort()
    all_pairs_list.append(cur_pairs_list)

  return all_pairs_list




# Computes the unreachable nodes i.e., any node which cannot be in the path from a start node to an end node:
def unreachable_nodes(parser):
  G = nx.Graph()

  for neighbour_list in parser.parsed_dict['#neighbours']:
    for index in range(1,len(neighbour_list)):
      G.add_edge(neighbour_list[0], neighbour_list[index])
  #  Because of two chains:
  if (parser.args.e == 'cgcp'):
    max_path_length = len(parser.parsed_dict['#blackinitials']) + 2*int((parser.depth + 1)/2) + 1
  else:
    max_path_length = len(parser.parsed_dict['#blackinitials']) + int((parser.depth + 1)/2)

  spl = dict(nx.all_pairs_shortest_path_length(G))

  num_positions = len(parser.parsed_dict['#positions'][0])

  count = 0
  unreachable_nodes_list = []
  for pos in parser.parsed_dict['#positions'][0]:
    if (pos not in spl):
      continue
    # setting the min length to maximum value:
    min_start_length = num_positions
    for start in parser.parsed_dict['#startboarder'][0]:
      if (start not in spl[pos]):
        continue
      if (min_start_length > spl[pos][start]):
        min_start_length = spl[pos][start]
    # setting the min length to maximum value:
    min_end_length = num_positions
    for end in parser.parsed_dict['#endboarder'][0]:
      if (end not in spl[pos]):
        continue
      if (min_end_length > spl[pos][end]):
        min_end_length = spl[pos][end]
    if (min_start_length+min_end_length > max_path_length - 1):
      unreachable_nodes_list.append(pos)
      #print(pos,min_start_length,min_end_length)
      count = count + 1
  if (parser.args.debug > -1):
    print("Removing unreachable nodes ... " + str(count) + " unreachable out of " + str(num_positions))
  #print(num_positions, count)
  return unreachable_nodes_list

def all_short_simple_paths(parser):
  if (parser.args.debug > -1):
    print("Coumpting all minimal simple paths from start to end boarder")
  G = nx.Graph()

  for key,value_list in parser.neighbour_dict.items():
    for value in value_list:
      G.add_edge(key, value)

  max_path_length = len(parser.black_initial_positions) + int((parser.depth + 1)/2)
  count = 0

  all_final_paths = []
  # maximum path length for the available winning configurations:
  max_length = 0


  for start in parser.start_boarder:
    for end in parser.end_boarder:
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
        count = count + len(final_small_paths)
        # adding all the final small paths:
        for small_path in final_small_paths:
          if (len(small_path) > max_length):
            max_length = len(small_path)
          small_path = list(small_path)
          small_path.sort()
          all_final_paths.append(list(small_path))
        #print(start, end)
        #print(final_small_paths)

  #print(count)
  #print(all_final_paths)

  return all_final_paths, max_length
