# Irfansha Shaik, 18.07.2022, Aarhus

import argparse
import glob
import os
import re
from pathlib import Path


def atoi(text):
  return int(text) if text.isdigit() else text

def natural_keys(text):
  return [ atoi(c) for c in re.split(r'(\d+)', text) ]



# Main:
if __name__ == '__main__':
  text = "Generate QCIR and QDIMACS encodings for specified gex inputs"
  parser = argparse.ArgumentParser(description=text,formatter_class=argparse.RawTextHelpFormatter)
  parser.add_argument("--output_dir", help="path to output directory", default = "intermediate_files/output")
  parser.add_argument("--input_dir", help="path to input directory (expecting Gex input files)")
  args = parser.parse_args()

  #====================================================================================
  # QCIR-14 encodings
  #====================================================================================
  # lifted:
  #-------------------------------------------------------------------
  encoding_formats = ["qcir", "qdimacs"]
  for i in range(len(encoding_formats)):

    cur_encoding_format = encoding_formats[i]
    # we specify the encoding formats for the Q-sage explicitly:
    if (cur_encoding_format == "qcir"):
      input_encoding_format = 1
    else:
      input_encoding_format = 2

    cur_encoding = 'pg'

    if not Path(args.output_dir).is_dir():
      print("Creating new directory for output folder.")
      os.mkdir(args.output_dir)

    if not Path(args.output_dir + "/" + cur_encoding_format).is_dir():
      print("Creating new " + cur_encoding_format + " directory in output folder.")
      os.mkdir(args.output_dir + "/" + cur_encoding_format)

    if not Path(args.output_dir + "/" + cur_encoding_format +"/lifted").is_dir():
      print("Creating new " + cur_encoding_format +"/lifted directory in output folder.")
      os.mkdir(args.output_dir +  "/" + cur_encoding_format +"/lifted")

    print("Writing to " + cur_encoding_format +"/lifted folder in output folder")


    output_dir = args.output_dir +  "/" + cur_encoding_format +"/lifted"

    #files_list = glob.glob(args.input_dir + "/MR-Gex/Gex-format/*")
    # for now using a special folder directly:
    files_list = glob.glob(args.input_dir + "/*")
    files_list.sort(key=natural_keys)


    for file_name in files_list:
      only_file_name = file_name.split("/")[-1]
      command = "python3 Q-sage.py -e " + cur_encoding + " --problem " + file_name + " --run 0 --encoding_format " + str(input_encoding_format) +" --encoding_out " + output_dir + "/" + only_file_name + "." + cur_encoding_format
      print(command)
      os.system(command)
    print("========================================================================")
    #-------------------------------------------------------------------
    # witness:
    # we allow tight neighbour pruning with explicit path generation:
    #-------------------------------------------------------------------

    cur_encoding = 'cp'

    if not Path(args.output_dir +  "/" + cur_encoding_format +"/witness").is_dir():
      print("Creating new " + cur_encoding_format +"/witness directory in output folder.")
      os.mkdir(args.output_dir +  "/" + cur_encoding_format +"/witness")

    print("Writing to " + cur_encoding_format +"/witness folder in output folder")


    output_dir = args.output_dir +  "/" + cur_encoding_format +"/witness"

    #files_list = glob.glob(args.input_dir + "/MR-Gex/Gex-format/*")
    # for now using a special folder directly:
    files_list = glob.glob(args.input_dir + "/*")
    files_list.sort(key=natural_keys)


    for file_name in files_list:
      only_file_name = file_name.split("/")[-1]
      command = "python3 Q-sage.py -e " + cur_encoding + " --problem " + file_name + " --tight_neighbour_pruning 1 --black_overwriting_black_enable 1 --run 0 --encoding_format " + str(input_encoding_format) +" --encoding_out " + output_dir + "/" + only_file_name + "." + cur_encoding_format
      print(command)
      os.system(command)

    print("========================================================================")
    #-------------------------------------------------------------------
    # witness-black-legal:
    # we allow tight neighbour pruning with explicit path generation:
    #-------------------------------------------------------------------

    cur_encoding = 'cp'

    if not Path(args.output_dir +  "/" + cur_encoding_format +"/witness_black_legal").is_dir():
      print("Creating new " + cur_encoding_format +"/witness_black_legal directory in output folder.")
      os.mkdir(args.output_dir +  "/" + cur_encoding_format +"/witness_black_legal")

    print("Writing to " + cur_encoding_format +"/witness_black_legal folder in output folder")


    output_dir = args.output_dir +  "/" + cur_encoding_format +"/witness_black_legal"

    #files_list = glob.glob(args.input_dir + "/MR-Gex/Gex-format/*")
    # for now using a special folder directly:
    files_list = glob.glob(args.input_dir + "/*")
    files_list.sort(key=natural_keys)

    #print(files_list)

    for file_name in files_list:
      only_file_name = file_name.split("/")[-1]
      command = "python3 Q-sage.py -e " + cur_encoding + " --problem " + file_name + " --tight_neighbour_pruning 1 --black_overwriting_black_enable 0 --run 0 --encoding_format " + str(input_encoding_format) +" --encoding_out " + output_dir + "/" + only_file_name + "." + cur_encoding_format
      print(command)
      os.system(command)

    print("========================================================================")
  #====================================================================================================================================================================================================================================

