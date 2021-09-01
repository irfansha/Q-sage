# Irfansha Shaik, 01.09.2021, Aarhus.

import os
import argparse

# Main:
if __name__ == '__main__':
  text = "Plays interactively if a winning strategy is found for given depth, Q-sage is black player and takes the first move"
  parser = argparse.ArgumentParser(description=text,formatter_class=argparse.RawTextHelpFormatter)
  parser.add_argument("--problem", help="problem file path", default = 'testcases/Hein_hex/hein_04_3x3-05.pg')
  parser.add_argument("--depth", help="Depth, default 3", type=int,default = 3)

  args = parser.parse_args()

  # TODO: read the input file with existing parser
  # TODO: repeat the loop of running until either winning configuration is reached
  ### TODO: run the program to find the winning move
  ### TODO: ask for the white move
  ### TODO: update the data structure and write it to a new intermediate file