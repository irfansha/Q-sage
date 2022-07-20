# Irfansha Shaik, 20.07.2022, Aarhus

import argparse
import glob
import os
import re
import textwrap
from pathlib import Path


def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]

# Main:
if __name__ == '__main__':
  text = "Generates and dispatches batch jobs for different encodings and solvers"
  parser = argparse.ArgumentParser(description=text,formatter_class=argparse.RawTextHelpFormatter)
  parser.add_argument("--partition", help="partition name", default = 'q48')
  parser.add_argument("--input_original_folder_path", help="directory path for original (not-preprocessed) input files")
  parser.add_argument("--input_preprocessed_folder_path", help="directory path for preprocessed input files")
  parser.add_argument("--output_dir", help="directory path for output files")

  args = parser.parse_args()


  # Checking if out directory exits:
  if not Path(args.output_dir).is_dir():
    print("Invalid directory path: " + args.output_dir)
    print("Creating new directory with same path.")
    os.mkdir(args.output_dir)


  abrv_dict = {"Bloqqer":"B", "HQSpre":"H", "QRATPre+":"Q",
               "cqesto":"CQ", "qfun":"QF", "qute":"QT", "caqe":"CQ", "depqbf":"DQ", "qesto-1.0":"QE",
               "explicit_board_level":"EBL", "explicit_board_pg_format":"EBP", "explicit_board_white_disconnecting":"EBWD",
               "lifted":"LL", "witness":"SW", "witness_black_legal":"SWB"}

  qcir_solvers = ["cqesto", "qfun", "qute"]

  #================================================================================================================================================
  # Batch scripts for qcir solvers:
  #================================================================================================================================================
  for solver in qcir_solvers:
    solver_path = "./solvers/" + solver

    #-------------------------------------------------------------------------------------------------------------------------------
    # we only consider 3 encodings for qcir format, for now:
    #-------------------------------------------------------------------------------------------------------------------------------
    qcir_encodings = ["lifted", "witness", "witness_black_legal"]
    for qcir_encoding in qcir_encodings:
      qcir_encoding_path =  args.input_original_folder_path + "/qcir/" + qcir_encoding

      files_list = glob.glob(os.path.join(qcir_encoding_path, "*"))
      files_list.sort(key=natural_keys)


      for file_path in files_list:
        file_name = file_path.strip("/n").split("/")[-1]

        # abbreviation string,
        # first, add solver type from dictionary:
        ab_string = abrv_dict[solver]
        # second, add preprocessor type, none for circuit solvers:
        ab_string += "_N"
        # third, add encoding format type, here QCIR so QC:
        ab_string += "_QC"
        # finally, add encoding type from the dictionary:
        ab_string = ab_string + "_" + abrv_dict[qcir_encoding] + "_"

        #print(file_name)
        # Generate batch script:
        f = open("run_" + ab_string + file_name + ".sh", "w")

        f.write("#!/bin/bash\n")
        f.write("#SBATCH --partition=" + args.partition + "\n")
        f.write("#SBATCH --nodes=1\n")
        f.write("#SBATCH --mem=0\n")
        # Exclusive flag:
        f.write("#SBATCH --exclusive\n")
        f.write("#SBATCH --time=01:03:00" + "\n")
        f.write("#SBATCH --mail-type=END\n")
        f.write("#SBATCH --mail-user=irfansha.shaik@cs.au.dk\n\n")

        f.write("echo '========= Job started  at `date` =========='\n\n")

        f.write("cd $SLURM_SUBMIT_DIR\n\n")

        f.write("time " + solver_path + " " + file_path + " &> " + args.output_dir + "/" + ab_string + file_name + "_$SLURM_JOB_ID\n")

        command = 'sbatch run_' + ab_string + file_name + ".sh"



        f.write("\necho '========= Job finished at `date` =========='\n")

        f.close()


        print(command)
        #os.popen(command)
  #================================================================================================================================================

  #qdimacs_solvers = ["caqe", "depqbf", "qesto-1.0", "qute"]
