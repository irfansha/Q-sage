# Irfansha Shaik, 22.11.2022, Aarhus

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
  text = "Generates and dispatches batch jobs for different encodings and solvers"
  parser = argparse.ArgumentParser(description=text,formatter_class=argparse.RawTextHelpFormatter)
  parser.add_argument("--partition", help="partition name", default = 'q48')
  parser.add_argument("--input_dir", help="directory path for input files")
  parser.add_argument("--output_dir", help="directory path for output files")
  parser.add_argument("--no_of_iterations", type=int, help="number of iterations", default=1)
  parser.add_argument("--args_list_file", help="path to file with arguments", default="cur_arg_list.txt")
  parser.add_argument("--batch_file_name", help="batch file name", default="test.sh")
  parser.add_argument("--run_batch", type=int, help="when enable, batch files are run default 0 (only generated)", default=0)

  args = parser.parse_args()


  # Checking if out directory exits:
  if not Path(args.output_dir).is_dir():
    print("Invalid directory path: " + args.output_dir)
    print("Creating new directory with same path.")
    os.mkdir(args.output_dir)

  # for now only with bloqqer:
  abrv_dict = {"cqesto":"CT", "quabs":"QU", "caqe":"CQ-B", "depqbf":"DQ-B", "qesto-1.0":"QE-B"}

  #solvers = ["caqe","depqbf"]
  solvers = ["depqbf"]

  #================================================================================================================================================
  # Batch scripts for solvers:
  #================================================================================================================================================
  for solver in solvers:
    print("---------------------------------------------------------------------------------------------")
    solver_path = "./solvers/" + solver

    #-------------------------------------------------------------------------------------------------------------------------------
    # qcir format
    #-------------------------------------------------------------------------------------------------------------------------------
    # only qcir files for qcir solvers
    if (solver in ["cqesto","quabs"]):
      files_list = glob.glob(os.path.join(args.input_dir, "*.qcir"))
    else:
      #files_list = glob.glob(os.path.join(args.input_dir, "*.bloqqer"))
      files_list = glob.glob(os.path.join(args.input_dir, "*"))
    files_list.sort(key=natural_keys)


    f_args = open(args.args_list_file,"w")

    # counter for array:
    counter = 0

    for file_path in files_list:
        file_name = file_path.strip("/n").split("/")[-1]
        for iter in range(args.no_of_iterations):
          counter = counter + 1
          f_args.write(file_path + "\n")
    f_args.close()

    #print(file_name)
    # Generate batch script:
    f = open(abrv_dict[solver] + "_" + args.batch_file_name, "w")

    f.write("#!/bin/bash\n")
    f.write("#SBATCH --partition=" + args.partition + "\n")
    f.write("#SBATCH --nodes=1\n")
    f.write("#SBATCH --mem=0\n")
    # Exclusive flag:
    f.write("#SBATCH --exclusive\n")
    f.write("#SBATCH --time=01:03:00" + "\n")
    f.write("#SBATCH --array=1-" + str(counter) +"%1" + "\n")
    f.write("#SBATCH --mail-type=END\n")
    f.write("#SBATCH --mail-user=irfansha.shaik@cs.au.dk\n\n")

    f.write("echo '========= Job started  at `date` =========='\n\n")

    f.write("cd $SLURM_SUBMIT_DIR\n\n")

    f.write("time " + solver_path + " " + '`awk "NR == $SLURM_ARRAY_TASK_ID" ' + args.args_list_file +'`' + " > " + args.output_dir + "/$SLURM_ARRAY_TASK_ID_" + abrv_dict[solver] + "_$SLURM_JOB_ID\n")

    command = 'sbatch ' + abrv_dict[solver] + "_" + args.batch_file_name



    f.write("\necho '========= Job finished at `date` =========='\n")

    f.close()


    print(command)
    if (args.run_batch == 1):
        os.popen(command)

  print("===============================================================")
