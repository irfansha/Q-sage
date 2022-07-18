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
  text = "Run move script within the artifact to generate moved encodings in the same input folder"
  parser = argparse.ArgumentParser(description=text,formatter_class=argparse.RawTextHelpFormatter)
  parser.add_argument("--input_dir", help="path to input directory (expecting qdimacs input files)")
  args = parser.parse_args()


  #====================================================================================
  # moved qdimacs encodings
  #====================================================================================
  for folder in ["lifted", "witness", "witness_black_legal"]:
    print("running move scripts on " + folder + " encodings")
    cur_input_folder = args.input_dir + "/" + folder + "/"
    # first remove all the files in the formulas folder
    print("Emptying formulas folder in the artifact")
    rm_command = "rm ../formulas/*"
    os.system(rm_command)
    # remove output folder in the qbf artifact
    print("Emptying output folder in the artifact")
    rm_output_command = "rm -r ../output/movement"
    os.system(rm_output_command)
    # copy the files to the formulas folder
    print("copying the input files to the formulas folder in artifact")
    copy_command = "cp -r " + cur_input_folder + "* " + "../formulas/"
    print(copy_command)
    os.system(copy_command)
    # run the move script
    move_script_command = "sh move-formulas-wrap.sh"
    print(move_script_command)
    os.system(move_script_command)

    # make a directory in the input folder for the moved encodings:
    if not Path(args.input_dir + "/moved").is_dir():
      print("Creating new moved directory in the input folder.")
      os.mkdir(args.input_dir + "/moved")

    if not Path(args.input_dir + "/moved/" + folder).is_dir():
      print("Creating new /moved/" + folder + " directory in input folder.")
      os.mkdir(args.input_dir +  "/moved/" + folder)


    # move the output files to the corresponding folders
    copy_moved_files_command = "cp -r ../output/movement/*-move.qdimacs " + args.input_dir +  "/moved/" + folder + "/"
    print(copy_moved_files_command)
    print("copying the moved files to the input folder")
    os.system(copy_moved_files_command)
    print("================================================================")
  #====================================================================================
