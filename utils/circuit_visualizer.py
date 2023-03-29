# Irfansha Shaik, 08.12.2022, Aarhus

from pyvis.network import Network
#import networkx as nx

def check_if_white(encoding,var):
  for i in range(len(encoding.move_variables)):
    if (i%2==1):
      if (var in encoding.move_variables[i]):
        return True
  return False

def circuit_viz(encoding):

  net = Network()

  nodes = []

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
            #net.add_node(non_neg_var, label=str(non_neg_var))
            if (check_if_white(encoding,non_neg_var)):
              net.add_node(non_neg_var, label=str(non_neg_var),color="red")
            else:
              net.add_node(non_neg_var, label=str(non_neg_var))
          net.add_edge(non_neg_var,out_var, color="red")
        else:
          # first setting nodes if not available:
          if (in_var not in nodes):
            nodes.append(in_var)
            #net.add_node(in_var, label=str(in_var))
            if(check_if_white(encoding,in_var)):
              net.add_node(in_var, label=str(in_var),color="red")
            else:
              net.add_node(in_var, label=str(in_var))
          net.add_edge(in_var,out_var, color="blue")
          #----------------------------------------------
  #out_vars_dict.sorted()

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