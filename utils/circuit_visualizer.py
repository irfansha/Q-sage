# Irfansha Shaik, 08.12.2022, Aarhus

from pyvis.network import Network
#import networkx as nx


def circuit_viz(encoding):

  net = Network()

  nodes = []

  in_out_vars_dict = {}

  for line in encoding.encoding:
    if (len(line) > 1):
      gate_type = line[0]
      out_var = line[1]
      in_vars = line[2]
      #print(gate_type, out_var, in_vars)
      if (out_var not in nodes):
        nodes.append(out_var)
        net.add_node(out_var, label=str(out_var))
      # adding edges for each in_vars to out_var:
      for in_var in in_vars:
        # if negative:
        if (in_var < 0):
          non_neg_var = -in_var
          # first setting nodes if not available:
          if (non_neg_var not in nodes):
            nodes.append(non_neg_var)
            net.add_node(non_neg_var, label=str(non_neg_var))
          net.add_edge(non_neg_var,out_var, color="red")
          #----------------------------------------------
          # we remember the outgoing edges:
          if (non_neg_var not in in_out_vars_dict):
            # second array is outvariables
            in_out_vars_dict[non_neg_var] = [[],[out_var]]
          else:
            in_out_vars_dict[non_neg_var][1].append(out_var)
          #----------------------------------------------
        else:
          # first setting nodes if not available:
          if (in_var not in nodes):
            nodes.append(in_var)
            net.add_node(in_var, label=str(in_var))
          net.add_edge(in_var,out_var, color="blue")
          #----------------------------------------------
          # we remember the outgoing edges:
          if (in_var not in in_out_vars_dict):
            # second array is outvariables
            in_out_vars_dict[in_var] = [[],[out_var]]
          else:
            in_out_vars_dict[in_var][1].append(out_var)
          #----------------------------------------------
  #out_vars_dict.sorted()
  sorted_in_out_vars_dict = dict(sorted(in_out_vars_dict.items()))
  count = 0
  for key,value in sorted_in_out_vars_dict.items():
    if (len(value[1]) == 1):
      #print(key, value)
      count = count + 1
  #print(count)

  #net.show_buttons(filter_=['physics','layout', 'edges'])
  #'''
  net.set_options("""
  const options = {
  "edges": {
    "arrows": {
      "to": {
        "enabled": true
      }
    },
    "color": {
      "inherit": true
    },
    "selfReferenceSize": null,
    "selfReference": {
      "angle": 0.7853981633974483
    },
    "smooth": false
  },
  "layout": {
    "hierarchical": {
      "enabled": true,
      "sortMethod": "directed"
    }
  },
  "physics": {
    "hierarchicalRepulsion": {
      "centralGravity": 0,
      "avoidOverlap": null
    },
    "minVelocity": 0.75,
    "solver": "hierarchicalRepulsion"
  }
  }
  """)
  #'''
  net.show('mygraph.html')