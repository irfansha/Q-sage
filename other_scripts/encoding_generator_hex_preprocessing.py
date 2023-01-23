# Irfansha Shaik, 12.12.2022, Aarhus

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
  text = "Generate QCIR and QDIMACS encodings for hex games"
  parser = argparse.ArgumentParser(description=text,formatter_class=argparse.RawTextHelpFormatter)
  parser.add_argument("--output_dir", help="path to output directory", default = "intermediate_files/output/")
  parser.add_argument("--input_dir", help="path to input directory")
  parser.add_argument("--encoding", help="encoding, default pg", default="pg")
  parser.add_argument("--preprocessor", help="1:bloqqer (default), 3:hqspre", type=int,default = 1)
  args = parser.parse_args()

  #====================================================================================
  # QCIR-14 encodings
  #====================================================================================
  # lifted:
  #-------------------------------------------------------------------
  #encodings_list = ['pg','ibign']
  #encoding_formats = ["qcir", "qdimacs"]
  encoding_formats = ["qdimacs"]
  #encoding_formats = ["qcir"]
  for i in range(len(encoding_formats)):

    cur_encoding_format = encoding_formats[i]
    # we specify the encoding formats for the Q-sage explicitly:
    if (cur_encoding_format == "qcir"):
      input_encoding_format = 1
    else:
      input_encoding_format = 2

    if not Path(args.output_dir).is_dir():
      print("Creating new directory for output folder.")
      os.mkdir(args.output_dir)

    encoding = args.encoding
    files_list = glob.glob(args.input_dir + "/*")
    files_list.sort(key=natural_keys)
    for file in files_list:
      file_name = file.split("/")[-1][:-3]
      if (cur_encoding_format == "qcir"):
        command = "python3 Q-sage.py --run 0 --game_type hex --problem " + file  + " -e "+ encoding  +  " --encoding_format " + str(input_encoding_format) + " --encoding_out " + os.path.join(args.output_dir, "_".join([file_name,encoding]) + "." + cur_encoding_format)
      else:
        if (args.preprocessor == 1):
            command = "python3 Q-sage.py --run 0 --preprocessing 1 --game_type hex --problem " + file  + " -e "+ encoding  +  " --encoding_format " + str(input_encoding_format) + " --preprocessed_encoding_out " + os.path.join(args.output_dir, "_".join([file_name,encoding]) + "." + cur_encoding_format + ".bloqqer")
        elif(args.preprocessor == 3):
            command = "python3 Q-sage.py --run 0 --preprocessing 3 --game_type hex --problem " + file  + " -e "+ encoding  +  " --encoding_format " + str(input_encoding_format) + " --preprocessed_encoding_out " + os.path.join(args.output_dir, "_".join([file_name,encoding]) + "." + cur_encoding_format + ".hqspre")
        else:
            command = "python3 Q-sage.py --run 0 --preprocessing 0 --game_type hex --problem " + file  + " -e "+ encoding  +  " --encoding_format " + str(input_encoding_format) + " --encoding_out " + os.path.join(args.output_dir, "_".join([file_name,encoding]) + "." + cur_encoding_format)
      print(command)
      os.system(command)

        
#====================================================================================================================================================================================================================================


# some qcir dolvers do not take comments:
qcir_files_list = glob.glob(args.output_dir + "/*.qcir")
qcir_files_list.sort(key=natural_keys)
for file in qcir_files_list:
  command = "sed -i '/#/d' " + file
  print(command)
  os.system(command)
  command = "sed -i '1 i\#QCIR-G14' " + file
  print(command)
  os.system(command)
