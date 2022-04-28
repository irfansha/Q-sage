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


  '''
  count = 0

  for start in parser.start_boarder:
    for end in parser.end_boarder:
      paths = nx.all_simple_paths(G, source=start, target=end, cutoff=max_path_length-1)
      plist = list(paths)
      if (len(plist) != 0):
        count = count + len(plist)
        #print(plist)

  print(count)
  '''
  return min_length
