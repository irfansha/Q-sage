# Irfansha Shaik, 19.07.2022, Aarhus

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
  text = "Preprocess QDIMACS encodings for specified gex inputs"
  parser = argparse.ArgumentParser(description=text,formatter_class=argparse.RawTextHelpFormatter)
  parser.add_argument("--output_dir", help="path to output directory")
  parser.add_argument("--input_dir", help="path to input directory (expecting qdimacs input files)")
  parser.add_argument("--preprocessor_dir", help="path to preprocessor directory (expecting preprocessors)")
  args = parser.parse_args()

  #====================================================================================
  # Preprocessing
  #====================================================================================
  preprocessor_paths = ["/Bloqqer/bloqqer", "/HQSpre/hqspre", "/QRATPre+/qratpre+"]
  # we use these as paths for preprocessor output files:
  preprocessor_folders = ["/Bloqqer", "/HQSpre", "/QRATPre+"]
  # paths for the qdimacs folders:
  input_folders = ["/explicit_board_level", "/explicit_board_pg_format", "/explicit_board_white_disconnecting",
                   "/qdimacs/lifted", "/qdimacs/witness", "/qdimacs/witness_black_legal",
                   "/qdimacs/moved/lifted", "/qdimacs/moved/witness", "/qdimacs/moved/witness_black_legal"]
  # We iterate through each preprocessor:
  for i in range(len(preprocessor_paths)):
    cur_path = args.preprocessor_dir + preprocessor_paths[i]
    print(cur_path)

    if not Path(args.output_dir).is_dir():
      print("Creating new directory for output folder.")
      os.mkdir(args.output_dir)

    # for each preprocessed encodings, we have a specific folder:
    if not Path(args.output_dir + preprocessor_folders[i]).is_dir():
      print("Creating new " + preprocessor_folders[i] + " directory in output folder.")
      os.mkdir(args.output_dir + preprocessor_folders[i])

    # qdimacs folder is needed:
    if not Path(args.output_dir + preprocessor_folders[i] + "/qdimacs").is_dir():
      print("Creating new " + preprocessor_folders[i] + "/qdimacs directory in output folder.")
      os.mkdir(args.output_dir + preprocessor_folders[i] + "/qdimacs")


    # moved folder is needed:
    if not Path(args.output_dir + preprocessor_folders[i] + "/qdimacs/moved").is_dir():
      print("Creating new " + preprocessor_folders[i] + "/qdimacs/moved directory in output folder.")
      os.mkdir(args.output_dir + preprocessor_folders[i] + "/qdimacs/moved")


    # In each folder, we need specific folder for each encoding:
    for j in range(len(input_folders)):
      cur_encoding_folder = input_folders[j]

      if not Path(args.output_dir + preprocessor_folders[i] + cur_encoding_folder).is_dir():
        print("Creating new " + preprocessor_folders[i] + cur_encoding_folder + " directory in output folder.")
        os.mkdir(args.output_dir + preprocessor_folders[i] + cur_encoding_folder)


      files_list = glob.glob(args.input_dir + cur_encoding_folder + "/*")
      files_list.sort(key=natural_keys)

      #'''
      for file_path in files_list:
        only_file_name = file_path.split("/")[-1]
        if (preprocessor_folders[i] == "/Bloqqer"):
          command = cur_path + " --timeout=100 " + file_path + " > " + args.output_dir + preprocessor_folders[i] + cur_encoding_folder + "/" + only_file_name
        elif (preprocessor_folders[i] == "/HQSpre"):
          command = cur_path + " --timeout 100 --pipe " + file_path + " > " + args.output_dir + preprocessor_folders[i] + cur_encoding_folder + "/" + only_file_name
        elif (preprocessor_folders[i] == "/QRATPre+"):
          command = cur_path + " --print-formula " + file_path + " 100 > " + args.output_dir + preprocessor_folders[i] + cur_encoding_folder + "/" + only_file_name
        print(command)
        os.system(command)
    print("========================================================================")
