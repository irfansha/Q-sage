import argparse
import glob
import os
import re
import textwrap
from pathlib import Path
from resource import *


def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]


files_list = glob.glob(os.path.join("human_games_repo/19_games/simplified_gex_inputs/", "*"))
#files_list = glob.glob(os.path.join("2-player_max_gex_inputs/", "*"))
files_list.sort(key=natural_keys)

for fname in files_list:
  only_file_name = fname.split("/")[-1]
  command = "python3 Q-sage.py --run 2 -e cp --time_limit 21600 --ignore_file_depth 1 --depth 11 --problem " + fname + " >> temp_human_played_games_19_test_second_player_7_look_ahead_11  "
  #command = "python3 Q-sage.py --run 0 -e eg --problem " + fname + " --encoding_out 2-player_max_benchmarks_10_04_2022/explicit_symbolic/" + only_file_name
  print(command)
  os.system(command)
