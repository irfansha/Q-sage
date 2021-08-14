# Irfansha Shaik, 14.08.2021, Aarhus.

from q_encodings.grounded_goal_encoding import GroundedGoalEncoding as gge
import os

def generate_encoding(parsed_instance):
  if (parsed_instance.args.e == 'gg'):
    print("Generating grounded goal encoding")
    encoding = gge(parsed_instance)

  # We print QCIR format directly to the file:
  if (parsed_instance.args.encoding_format == 1):
    encoding.print_encoding_tofile(parsed_instance.args.encoding_out)
  else:
    # For QDIMACS, we write the encoding to an intermediate file and change
    # to right format:
    encoding.print_encoding_tofile(parsed_instance.args.intermediate_encoding_out)
    converter_tool_path = os.path.join(parsed_instance.args.planner_path, 'tools', 'qcir_to_dimacs_convertor' , 'qcir2qdimacs')
    # Calling the tool
    os.system(converter_tool_path + ' ' + parsed_instance.args.intermediate_encoding_out + ' > ' + parsed_instance.args.encoding_out)

  # External preprocessing:
  if (parsed_instance.args.preprocessing == 1):
    preprocessor_path = os.path.join(parsed_instance.args.planner_path, 'tools', 'Bloqqer', 'bloqqer')
    # Calling the tool:
    # We preprocess only qdimacs format encoding:
    assert(parsed_instance.args.encoding_format == 2)
    os.system(preprocessor_path + ' ' + parsed_instance.args.encoding_out + ' > ' + parsed_instance.args.preprocessed_encoding_out)


  # Returning encoding for plan extraction:
  return encoding
