# Irfansha Shaik, 14.08.2021, Aarhus.

from q_encodings.grounded_goal_encoding import GroundedGoalEncoding as gge
from q_encodings.grounded_goal_with_time import GroundedGoalTimeEncoding as ggte
from q_encodings.path_based_goal import PathBasedGoal as pbg
from q_encodings.compact_path_based_goal import CompactPathBasedGoal as cpbg
import os

def generate_encoding(parsed_instance):
  if (parsed_instance.args.e == 'gg'):
    print("Generating grounded goal encoding")
    encoding = gge(parsed_instance)
  elif (parsed_instance.args.e == 'ggt'):
    print("Generating grounded goal encoding with time")
    encoding = ggte(parsed_instance)
  elif (parsed_instance.args.e == 'pg'):
    print("Generating path based goal encoding")
    encoding = pbg(parsed_instance)
  elif (parsed_instance.args.e == 'cpg'):
    print("Generating compact path based goal encoding")
    encoding = cpbg(parsed_instance)

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
    print("For now printing other encodings to file as well, work in progress!")
    encoding.print_encoding_tofile(parsed_instance.args.encoding_out)

  # External preprocessing:
  if (parsed_instance.args.preprocessing == 1):
    preprocessor_path = os.path.join(parsed_instance.args.planner_path, 'tools', 'Bloqqer', 'bloqqer')
    # Calling the tool:
    # We preprocess only qdimacs format encoding:
    assert(parsed_instance.args.encoding_format == 2)
    os.system(preprocessor_path + ' ' + parsed_instance.args.encoding_out + ' > ' + parsed_instance.args.preprocessed_encoding_out)


  # Returning encoding for plan extraction:
  return encoding
