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
from q_encodings.gttt_witness_based import GtttWitnessBased as gtttw
from q_encodings.index_based_general import IndexBasedGeneral as ibgen
from q_encodings.index_based_gomuku import IndexBasedGomuku as ibg
from q_encodings.iterative_squaring_witness_based import \
    IterativeSquaringWitnessBased as iswb
from q_encodings.no_transitions_path_based import \
    NoTransitionsPathBasedGoal as ntpbg
from q_encodings.path_based_goal import PathBasedGoal as pbg
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
    if (parsed_instance.args.debug > -1):
      print("Generating grounded goal encoding")
    encoding = gge(parsed_instance)
  elif (parsed_instance.args.e == 'eg'):
    if (parsed_instance.args.debug > -1):
      print("Generating explicit goal encoding")
    encoding = ege(parsed_instance)
  elif (parsed_instance.args.e == 'ew'):
    if (parsed_instance.args.debug > -1):
      print("Generating explicit goal witness based encoding")
    encoding = egwb(parsed_instance)
  elif (parsed_instance.args.e == 'iw'):
    if (parsed_instance.args.debug > -1):
      print("Generating iterative goal witness based encoding")
    encoding = iswb(parsed_instance)
  elif (parsed_instance.args.e == 'ggt'):
    if (parsed_instance.args.debug > -1):
      print("Generating grounded goal encoding with time")
    encoding = ggte(parsed_instance)
  elif (parsed_instance.args.e == 'pg'):
    if (parsed_instance.args.debug > -1):
      print("Generating path based goal encoding")
    encoding = pbg(parsed_instance)
  elif (parsed_instance.args.e == 'cpg'):
    if (parsed_instance.args.debug > -1):
      print("Generating compact path based goal encoding")
    encoding = cpbg(parsed_instance)
  elif (parsed_instance.args.e == 'ttt'):
    if (parsed_instance.args.debug > -1):
      print("Generating TicTacToe encoding")
    encoding = ttt(parsed_instance)
  elif (parsed_instance.args.e == 'wgttt'):
    if (parsed_instance.args.debug > -1):
      print("Generating GTicTacToe witness encoding")
    encoding = gtttw(parsed_instance)
  elif (parsed_instance.args.e == 'ib' and parsed_instance.args.game_type == "gomuku"):
    if (parsed_instance.args.debug > -1):
      print("Generating Gomuku encoding")
    encoding = ibg(parsed_instance)
  elif (parsed_instance.args.e == 'ib' and parsed_instance.args.game_type == "general"):
    if (parsed_instance.args.debug > -1):
      print("Generating General game encoding")
    encoding = ibgen(parsed_instance)
  elif (parsed_instance.args.e == 'cp'):
    if (parsed_instance.args.debug > -1):
      print("Generating Compact Positional encoding")
    encoding = cp(parsed_instance)
  elif (parsed_instance.args.e == 'cgcp'):
    if (parsed_instance.args.debug > -1):
      print("Generating Compact Goal Compact Positional encoding")
    encoding = cgcp(parsed_instance)
  elif (parsed_instance.args.e == 'ntpg'):
    if (parsed_instance.args.debug > -1):
      print("Generating no transition path based goal encoding")
    encoding = ntpbg(parsed_instance)

  # We print QCIR format directly to the file:
  if (parsed_instance.args.encoding_format == 1 ):
    encoding.print_encoding_tofile(parsed_instance.args.encoding_out)
  elif(parsed_instance.args.encoding_format == 2):
    # For QDIMACS, we write the encoding to an intermediate file and change
    # to right format:
    encoding.print_encoding_tofile(parsed_instance.args.intermediate_encoding_out)
    # Using local script for moving:
    converter_script_path = os.path.join(parsed_instance.args.planner_path, 'utils', 'qcir_to_qdimacs_transformer.py')
    os.system("python3 " + converter_script_path + ' --input_file ' + parsed_instance.args.intermediate_encoding_out + ' --output_file ' + parsed_instance.args.encoding_out)
    # when debug we generate both the conversion and checks if they are the same:
    if (parsed_instance.args.debug == 1):
      converter_tool_path = os.path.join(parsed_instance.args.planner_path, 'tools', 'qcir_to_dimacs_convertor' , 'qcir2qdimacs')
      # Calling the tool
      os.system(converter_tool_path + ' ' + parsed_instance.args.intermediate_encoding_out + ' > ' + parsed_instance.args.encoding_out + "_out")
      print("\n# testing if both conversions are same (correct if next line is empty) =================")
      # checking if both are same files:
      os.system("cmp " + parsed_instance.args.encoding_out + " " + parsed_instance.args.encoding_out + "_out")
      print("# ===========================================================================================\n")
  # QDIMACS + moved:
  elif(parsed_instance.args.encoding_format == 5):
    # For QDIMACS, we write the encoding to an intermediate file and change
    # to right format:
    encoding.print_encoding_tofile(parsed_instance.args.intermediate_encoding_out)
    # Using local script for moving:
    converter_script_path = os.path.join(parsed_instance.args.planner_path, 'utils', 'qcir_to_qdimacs_transformer.py')
    os.system("python3 " + converter_script_path + ' --move_intermediate_gates 1 --input_file ' + parsed_instance.args.intermediate_encoding_out + ' --output_file ' + parsed_instance.args.encoding_out)
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
