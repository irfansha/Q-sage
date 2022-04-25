# Irfansha Shaik, 14.08.2021, Aarhus.

import os

from q_encodings.compact_goal_compact_positional import \
    CompactGoalCompactPositonal as cgcp
from q_encodings.compact_path_based_goal import CompactPathBasedGoal as cpbg
from q_encodings.compact_positional import CompactPositonal as cp
from q_encodings.explicit_goal_encoding import ExplicitGoalEncoding as ege
from q_encodings.explicit_goal_witness_based import \
    ExplicitGoalWitnessBased as egwb
from q_encodings.grounded_goal_encoding import GroundedGoalEncoding as gge
from q_encodings.grounded_goal_with_time import \
    GroundedGoalTimeEncoding as ggte
from q_encodings.iterative_squaring_witness_based import \
    IterativeSquaringWitnessBased as iswb
from q_encodings.no_transitions_path_based import \
    NoTransitionsPathBasedGoal as ntpbg
from q_encodings.path_based_goal import PathBasedGoal as pbg
from q_encodings.path_based_no_bool_goal import PathBasedNoBoolGoal as pbnbg
from q_encodings.tictactoe import TicTacToe as ttt


def add_dependencies_to_qdimacs(parsed_instance, encoding):
  # Read the encoding file:
  f = open(parsed_instance.args.encoding_out, 'r')
  lines = f.readlines()
  f.close()

  header = lines.pop(0)
  previous_line = ''
  for line in lines:
    # Looking at the prefix:
    if (line[0] == 'a' or line[0] == 'e'):
      previous_line = line
    else:
      # this stops the previous line at the last existential layer
      break

  f = open(parsed_instance.args.encoding_out, 'w')

  # Writing the header
  f.write(header)
  # Adding the dependencies:
  for line in encoding.dqdimacs_prefix:
    f.write(line + "\n")
  # Adding the last existential line:
  f.write(previous_line)
  # Adding rest of the clauses:
  for line in lines:
    if (line[0] == 'a' or line[0] == 'e'):
      continue
    else:
      f.write(line)
  f.close()




def generate_encoding(parsed_instance):
  if (parsed_instance.args.e == 'gg'):
    print("Generating grounded goal encoding")
    encoding = gge(parsed_instance)
  elif (parsed_instance.args.e == 'eg'):
    print("Generating explicit goal encoding")
    encoding = ege(parsed_instance)
  elif (parsed_instance.args.e == 'ew'):
    print("Generating explicit goal witness based encoding")
    encoding = egwb(parsed_instance)
  elif (parsed_instance.args.e == 'iw'):
    print("Generating iterative goal witness based encoding")
    encoding = iswb(parsed_instance)
  elif (parsed_instance.args.e == 'ggt'):
    print("Generating grounded goal encoding with time")
    encoding = ggte(parsed_instance)
  elif (parsed_instance.args.e == 'pg'):
    if (parsed_instance.args.stuttering == 'b'):
      print("Generating path based goal encoding")
      encoding = pbg(parsed_instance)
    elif (parsed_instance.args.stuttering == 'nb'):
      print("Generating path based goal encoding, without bool vars")
      encoding = pbnbg(parsed_instance)
  elif (parsed_instance.args.e == 'cpg'):
    print("Generating compact path based goal encoding")
    encoding = cpbg(parsed_instance)
  elif (parsed_instance.args.e == 'ttt'):
    print("Generating TicTacToe encoding")
    encoding = ttt(parsed_instance)
  elif (parsed_instance.args.e == 'cp'):
    print("Generating Compact Positional encoding")
    encoding = cp(parsed_instance)
  elif (parsed_instance.args.e == 'cgcp'):
    print("Generating Compact Goal Compact Positional encoding")
    encoding = cgcp(parsed_instance)
  elif (parsed_instance.args.e == 'ntpg'):
    print("Generating no transition path based goal encoding")
    encoding = ntpbg(parsed_instance)

  # We print QCIR format directly to the file:
  if (parsed_instance.args.encoding_format == 1 ):
    encoding.print_encoding_tofile(parsed_instance.args.encoding_out)
  elif(parsed_instance.args.encoding_format == 2):
    # For QDIMACS, we write the encoding to an intermediate file and change
    # to right format:
    encoding.print_encoding_tofile(parsed_instance.args.intermediate_encoding_out)
    converter_tool_path = os.path.join(parsed_instance.args.planner_path, 'tools', 'qcir_to_dimacs_convertor' , 'qcir2qdimacs')
    # Calling the tool
    os.system(converter_tool_path + ' ' + parsed_instance.args.intermediate_encoding_out + ' > ' + parsed_instance.args.encoding_out)
  elif(parsed_instance.args.encoding_format == 3):
    encoding.print_encoding_tofile(parsed_instance.args.encoding_out)
  else:
    # For dqdimacs:
    encoding.print_encoding_tofile(parsed_instance.args.intermediate_encoding_out)
    converter_tool_path = os.path.join(parsed_instance.args.planner_path, 'tools', 'qcir_to_dimacs_convertor' , 'qcir2qdimacs')
    # Calling the tool
    os.system(converter_tool_path + ' ' + parsed_instance.args.intermediate_encoding_out + ' > ' + parsed_instance.args.encoding_out)
    add_dependencies_to_qdimacs(parsed_instance, encoding)




  # External preprocessing:
  if (parsed_instance.args.preprocessing == 1):
    preprocessor_path = os.path.join(parsed_instance.args.planner_path, 'tools', 'Bloqqer', 'bloqqer')
    # Calling the tool:
    # We preprocess only qdimacs format encoding:
    assert(parsed_instance.args.encoding_format == 2)
    os.system(preprocessor_path + ' ' + parsed_instance.args.encoding_out + ' > ' + parsed_instance.args.preprocessed_encoding_out)


  # Returning encoding for plan extraction:
  return encoding
