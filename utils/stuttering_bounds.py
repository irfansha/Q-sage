import networkx as nx


def lower_bound(parser):

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


def all_short_simple_paths(parser):

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
        if path not in list_for_avail_paths:
            continue
        for temp_path in list_for_avail_paths:
          intersection = set.intersection(path, temp_path)
          if path == intersection:
            remove_path_list.append(temp_path)
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
          all_final_paths.append(list(small_path))
        #print(start, end)
        #print(final_small_paths)

  #print(count)
  #print(all_final_paths)

  return all_final_paths, max_length
