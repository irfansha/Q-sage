# Irfansha Shaik, 13.09.2021, Aarhus

'''
TODOS:
  - Use D-CAQE to take advantage of selected dependency in the earlier rounds
'''

import os
import time
import argparse, textwrap
import q_encodings.encoder as ge
from parse.parser import Parse as ps
import run.run_solver as rs
import testing.tests as ts
import subprocess
import datetime


# Main:
if __name__ == '__main__':
  text = "A tool to generate ungrounded QBF encodings for 2-player positional games and computes winning statergy if requested."
  parser = argparse.ArgumentParser(description=text,formatter_class=argparse.RawTextHelpFormatter)
  parser.add_argument("-V", "--version", help="show program version", action="store_true")
  parser.add_argument("--problem", help="problem file path", default = 'testcases/Hein_hex/hein_04_3x3-03.pg')
  parser.add_argument("--planner_path", help="path for Q-sage.py, allowing remote run", default = os.getcwd())
  parser.add_argument("--depth", help="Depth, default 3", type=int,default = 3)
  parser.add_argument("--ignore_file_depth", help="Ignore time stamps in input file and enforce user depth, default 0", type=int,default = 0)
  parser.add_argument("-e", help=textwrap.dedent('''
                                  encoding types:
                                  gg = grounded goal encoding
                                  ggt = grounded goal with time'''),default = 'gg')
  parser.add_argument("--run", type=int, help=textwrap.dedent('''
                               Three levels of execution:
                               0 = only generate encoding
                               1 = existence of winning strategy
                               2 = extract first step of winning strategy if found'''),default = 0)
  parser.add_argument("--encoding_format", type=int, help="Encoding format: [1 = QCIR14 2 = QDIMACS], default 1",default = 2)
  parser.add_argument("--encoding_out", help="output encoding file",default = 'intermediate_files/encoding')
  parser.add_argument("--intermediate_encoding_out", help="output intermediate encoding file",default = 'intermediate_files/intermediate_encoding')
  parser.add_argument("--solver", type=int, help=textwrap.dedent('''
                                       Solver:
                                       1 = quabs
                                       2 = CAQE
                                       3 = RaReQS'''),default = 2)
  parser.add_argument("--solver_out", help="solver output file",default = 'intermediate_files/solver_output')
  parser.add_argument("--debug", type=int, help="[0/1], default 0" ,default = 0)
  parser.add_argument("--run_tests", type=int, help="[0/1], default 0" ,default = 0)
  parser.add_argument("--seed", help="seed value for random generater for testing (default 0)", type=int,default = 0)
  parser.add_argument("--renumber_positions", type=int, help="renumber positions for tighter lessthan constraints [0/1], default 1" ,default = 1)
  parser.add_argument("--restricted_position_constraints", type=int, help="[0/1], default 1" ,default = 1)
  parser.add_argument("--forall_move_restrictions", help=textwrap.dedent('''
                                       in = let forall restrictions in each if condition
                                       out = forall restrictions outside the transition functions (default)'''), default = 'out')
  parser.add_argument("--preprocessing", type = int, help=textwrap.dedent('''
                                       Preprocessing:
                                       0 = off
                                       1 = bloqqer (version 37)
                                       2 = bloqqer-qdo'''),default = 2)
  parser.add_argument("--preprocessed_encoding_out", help="output preprocessed encoding file",default = 'intermediate_files/preprocessed_encoding')
  parser.add_argument("--time_limit", type=float, help="Solving time limit in seconds, default 1800 seconds",default = 1800)
  parser.add_argument("--preprocessing_time_limit", type=int, help="Preprocessing time limit in seconds, default 900 seconds",default = 900)
  args = parser.parse_args()


  label = subprocess.check_output(["git", "describe", "--always"]).strip()


  print("Start time: " + str(datetime.datetime.now()))

  print("Git commit hash: " + str(label))

  print(args)

  if args.version:
    print("Version 0.5")

  # Run tests include all testcase domains:
  if (args.run_tests == 1):
    # We do not print any additional information:
    if (args.debug != 0):
      args.debug = 0
    ts.run_tests(args)
    exit()

  # --------------------------------------- Timing the encoding ----------------------------------------
  start_encoding_time = time.perf_counter()

  parsed_instance = ps(args)


  encoding = ge.generate_encoding(parsed_instance)


  encoding_time = time.perf_counter() - start_encoding_time
  print("Encoding time: " + str(encoding_time))
  # ----------------------------------------------------------------------------------------------------

  if (args.run >= 1):
    # --------------------------------------- Timing the solver run ----------------------------------------
    start_run_time = time.perf_counter()

    rs.run_single_solver(encoding)

    solving_time = time.perf_counter() - start_run_time
    print("Solving time: " + str(solving_time) + "\n")
    # ------------------------------------------------------------------------------------------------------

  # ------------------------------------- Printing memory stats of encodings -----------------------------
  print("Encoding size (in KB): " + str(os.path.getsize(args.encoding_out)/1000))
  if (args.preprocessing == 1):
    print("Preprocessed encoding size (in KB): " + str(os.path.getsize(args.preprocessed_encoding_out)/1000))
  # ------------------------------------------------------------------------------------------------------


  print("Finish time: " + str(datetime.datetime.now()))
