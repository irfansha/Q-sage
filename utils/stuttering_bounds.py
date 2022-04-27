import networkx as nx


def lower_bound(parser):

  G = nx.Graph()

  for key,value_list in parser.neighbour_dict.items():
    for value in value_list:
      G.add_edge(key, value)

  max_path_length = len(parser.black_initial_positions) + int((parser.depth + 1)/2)

  spl = dict(nx.all_pairs_shortest_path(G, max_path_length))


  # initializing minimum length with the max path length:
  min_length = max_path_length

  path = []

  for start in parser.start_boarder:
    for end in parser.end_boarder:
      if (end in spl[start]):
        if (len(spl[start][end]) < min_length):
          min_length = len(spl[start][end])
        #print(spl[start][end])
  #print(min_length, path)

  return min_length
