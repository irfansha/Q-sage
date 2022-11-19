# Irfansha Shaik, 13.09.2021, Aarhus

'''
TODOS:
  - Need to handle non-existence of white goals, first looking at tic-tac-toe game
  - Reduce the black search space further by only considering one levels of nighbours
    for each peice we can play.
  - Use D-CAQE to take advantage of selected dependency in the earlier rounds.
'''

import argparse
import datetime
import os
import subprocess
import textwrap
import time

import q_encodings.encoder as ge
import run.run_solver as rs
import testing.tests as ts
from parse.parser import Parse as ps

# Main:
if __name__ == '__main__':
  text = "A tool to generate ungrounded QBF encodings for 2-player positional games and computes winning statergy if requested."
  parser = argparse.ArgumentParser(description=text,formatter_class=argparse.RawTextHelpFormatter)
  parser.add_argument("-V", "--version", help="show program version", action="store_true")
  parser.add_argument("--ib_domain", help=" index based domain file path", default = 'testcases/index_separate_inputs/domain.ig')
  parser.add_argument("--ib_problem", help=" index based problem file path", default = 'testcases/index_separate_inputs/problem.ig')
  parser.add_argument("--problem", help="problem file path", default = 'testcases/winning_testcases_ungrounded_new_boards/hein_04_3x3-05.pg')
  parser.add_argument("--planner_path", help="path for Q-sage.py, allowing remote run", default = os.getcwd())
  parser.add_argument("--depth", help="Depth, default 3", type=int,default = 3)
  parser.add_argument("--xmax", help="xmax, default 4", type=int,default = 4)
  parser.add_argument("--ymax", help="ymax, default 4", type=int,default = 4)
  parser.add_argument("--ignore_file_depth", help="Ignore time stamps in input file and enforce user depth, default 0", type=int,default = 0)
  parser.add_argument("--ignore_file_boardsize", help="Ignore board size in input file and enforce user sizes, default 0", type=int,default = 0)
  parser.add_argument("-e", help=textwrap.dedent('''
                                  encoding types:
                                  pg = path based goal (ungrounded)
                                  cpg = compact path based goal (ungrounded)
                                  gg = grounded goal encoding
                                  ggt = grounded goal with time
                                  eg = explicit goal encoding
                                  ew = explicit goal witness based
                                  iw = iteratice squaring witness based
                                  ttt = tictactoe
                                  cp = compact positional
                                  cgcp = compact goal compact positional
                                  ntpg = path based goal, without transition function
                                  ib = index based (grid games)
                                  nib = nested index based (grid games)
                                  dnib = double nested index based (grid games)
                                  bwnib = black white nested index based (grid games)
                                  wgttt = witness based gttt)'''),default = 'pg')
  parser.add_argument("--game_type", help=textwrap.dedent('''
                                  games (for specific optimizations):
                                  hex = hex game (default)
                                  ttt = tic-tac-toe
                                  gomuku = gomuku
                                  general = general game, for index based'''),default = 'hex')
  parser.add_argument("--goal_length", help="Goal line length for games such as tic-tac-toe and gomuku, default 3", type=int,default = 3)
  parser.add_argument("--run", type=int, help=textwrap.dedent('''
                               Three levels of execution:
                               0 = only generate encoding
                               1 = existence of winning strategy
                               2 = extract first step of winning strategy if found'''),default = 0)
  parser.add_argument("--encoding_format", type=int, help=textwrap.dedent('''
                                       Encoding format:
                                       1 = QCIR14
                                       2 = QDIMACS (default)
                                       3 = DQCIR
                                       4 = DQDIMACS
                                       5 = QDIMACS-moved'''),default = 2)
  parser.add_argument("--encoding_out", help="output encoding file",default = 'intermediate_files/encoding')
  parser.add_argument("--intermediate_encoding_out", help="output intermediate encoding file",default = 'intermediate_files/intermediate_encoding')
  parser.add_argument("--certificate_out", help="certificate file path",default = 'intermediate_files/certificate')
  parser.add_argument("--solver", type=int, help=textwrap.dedent('''
                                       Solver:
                                       1 = quabs
                                       2 = CAQE (default)
                                       3 = RaReQS
                                       4 = Pedant
                                       5 = DepQBF-qrp-cert (for now, main focus on certificate generation)
                                       6 = DepQBF'''),default = 2)
  parser.add_argument("--solver_out", help="solver output file",default = 'intermediate_files/solver_output')
  parser.add_argument("--debug", type=int, help="[0/1], default 0" ,default = 0)
  parser.add_argument("--run_tests", type=int, help="[0/1], default 0" ,default = 0)
  parser.add_argument("--viz_testing", type=int, help="vizual testing with certificate generation for general games (for now pedant)  [0/1], default 0" ,default = 0)
  parser.add_argument("--viz_meta_data_out", help="visual testing meta data (input and vars) file path",default = 'intermediate_files/viz_meta_out')
  parser.add_argument("--seed", help="seed value for random generater for testing (default 0)", type=int,default = 0)
  parser.add_argument("--renumber_positions", type=int, help=textwrap.dedent('''
                                       renumber positions for tighter lessthan constraints:
                                       0 = None
                                       1 = renumber open position to the front
                                       2 = extra equality clauses for the transformed board with only open positions (default 0)''') ,default = 0)
  parser.add_argument("--restricted_position_constraints", type=int, help="[0/1], default 0" ,default = 0)
  parser.add_argument("--black_move_restrictions", type=int, help="[0/1], default 1" ,default = 1)
  parser.add_argument("--black_overwriting_black_enable", type=int, help=" for witness encoding (compact positional) we can either allow black overwriting itself or not [0/1], default 1" ,default = 1)
  parser.add_argument("--forall_move_restrictions", help=textwrap.dedent('''
                                       in = let forall restrictions in each if condition
                                       out = forall restrictions outside the transition functions
                                       none = no restrictions (default)'''), default = 'none')
  parser.add_argument("--remove_unreachable_nodes", type=int, help="[0/1], default 0" ,default = 0)
  parser.add_argument("--tight_neighbour_pruning", type=int, help="[0/1], default 0" ,default = 0)
  parser.add_argument("--tight_neighbours_with_distances", type=int, help="computer tight neighbours with distances, less powerful but also less overhead [0/1], default 0" ,default = 0)
  parser.add_argument("--force_black_player_stop", type=int, help="[0/1], default 0 once black player stops the game, rest of the predicates are forced to open" ,default = 0)
  parser.add_argument("--force_white_player_stop", type=int, help="[0/1], default 0 once white player stops the game, rest of the predicates are forced to open" ,default = 0)
  parser.add_argument("--preprocessing", type = int, help=textwrap.dedent('''
                                       Preprocessing:
                                       0 = off
                                       1 = bloqqer (version 37)
                                       2 = bloqqer-qdo
                                       3 = hqspre'''),default = 2)
  parser.add_argument("--preprocessed_encoding_out", help="output preprocessed encoding file",default = 'intermediate_files/preprocessed_encoding')
  parser.add_argument("--time_limit", type=float, help="Solving time limit in seconds, default 1800 seconds",default = 1800)
  parser.add_argument("--preprocessing_time_limit", type=int, help="Preprocessing time limit in seconds, default 900 seconds",default = 900)
  args = parser.parse_args()


  label = subprocess.check_output(["git", "describe", "--always"]).strip()


  if (args.debug > -1):
    print("Start time: " + str(datetime.datetime.now()))

    print("Git commit hash: " + str(label))

    print(args)

  if args.version:
    print("Version 0.7")

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

  # If problem is unsolvable, we simply stop:
  if parsed_instance.unsolvable == 1:
    print("Plan not found")
    exit()

  encoding = ge.generate_encoding(parsed_instance)


  encoding_time = time.perf_counter() - start_encoding_time
  if (args.debug > -1):
    print("Encoding time: " + str(encoding_time))
  # ----------------------------------------------------------------------------------------------------

  if (args.run >= 1):
    # --------------------------------------- Timing the solver run ----------------------------------------
    start_run_time = time.perf_counter()

    rs.run_single_solver(encoding)

    solving_time = time.perf_counter() - start_run_time
    if (args.debug > -1):
      print("Solving time: " + str(solving_time) + "\n")
    # ------------------------------------------------------------------------------------------------------

  # ------------------------------------- Printing memory stats of encodings -----------------------------
  if (args.debug > -1):
    print("Encoding size (in KB): " + str(os.path.getsize(args.encoding_out)/1000))
    if (args.preprocessing == 1):
      print("Preprocessed encoding size (in KB): " + str(os.path.getsize(args.preprocessed_encoding_out)/1000))
  # ------------------------------------------------------------------------------------------------------

  if (args.debug > -1):
    print("Finish time: " + str(datetime.datetime.now()))
