# Irfansha Shaik, 07.09.2021, Aarhus.

import glob
import re
import os, subprocess

def atoi(text):
  return int(text) if text.isdigit() else text

def natural_keys(text):
  return [ atoi(c) for c in re.split(r'(\d+)', text) ]

def run_tests(args):
  print("Running tests")
  if (args.e == 'pg'):
    cur_path = os.path.join(args.planner_path, 'testcases', 'winning_testcases_ungrounded', '*')
  else:
    cur_path = os.path.join(args.planner_path, 'testcases', 'winning_testcases', '*')
  files_list = glob.glob(cur_path)
  files_list.sort(key=natural_keys)
  for testcase in files_list:
    print("Running for the testcase:", testcase)
    print("--------------------------------------------------------------------------------------------")
    command = "python3 interactive_play.py --ignore_file_depth 0 --player random -e " + args.e + " --forall_move_restrictions " + args.forall_move_restrictions + " --restricted_position_constraints " + str(args.restricted_position_constraints) + " --seed " + str(args.seed) +  " --problem " + testcase + " > intermediate_files/testing_output"
    subprocess.run([command], shell = True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT ,check=True)

    # Checking if the rercent testrun is successful:
    cur_output_path = os.path.join(args.planner_path, 'intermediate_files', 'testing_output')
    f = open(cur_output_path, 'r')
    lines = f.readlines()
    f.close()
    for line in lines:
      print(line.strip("\n"))
    print("--------------------------------------------------------------------------------------------")