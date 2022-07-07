# Irfansha Shaik, 07.07.2022, Aarhus

import argparse
import glob
import os
from pathlib import Path

# Main:
if __name__ == '__main__':
  text = "Takes SGF hex file and generators Gex,R-Gex,MR-Gex inputs in different formats"
  parser = argparse.ArgumentParser(description=text,formatter_class=argparse.RawTextHelpFormatter)
  parser.add_argument("--input_file", help="SGF hex file, either of a tournament or simply a set of games")
  parser.add_argument("--output_dir", help="path to output directory", default = "intermediate_files/output")
  parser.add_argument("--unrolling_depth", help="number of move to unroll the game, default 1", type=int, default = 1)
  parser.add_argument("--instance_depth", help="gex input depth, default 11", type=int, default = 11)
  args = parser.parse_args()


  #=====================================================================================================================================
  # Checking if intermediate_files exists:
  if not Path("intermediate_files").is_dir():
    print("Creating intermediate_files directory")
    os.mkdir("intermediate_files")

  # Checking if intermediate_files/B-Hex directory exists:
  if not Path("intermediate_files/B-Hex").is_dir():
    print("Creating intermediate_files/B-Hex directory")
    os.mkdir("intermediate_files/B-Hex")

  #=====================================================================================================================================
  # Checking if out directory exits:
  if not Path(args.output_dir).is_dir():
    print("Invalid output directory path: " + args.output_dir)
    print("Creating new output directory with same path.")
    os.mkdir(args.output_dir)
  #=====================================================================================================================================

  


  #=====================================================================================================================================
  # tournament_parse script reads from intermediate_files/games_list.txt;
  # so writing to the games list file:
  # reading and writing, instead of copying the file directly:
  f_input = open(args.input_file, "r")
  input_lines = f_input.readlines()
  f_input.close()

  f_parsed_game_output = open("intermediate_files/games_list.txt", "w")
  for line in input_lines:
    f_parsed_game_output.write(line)
  f_parsed_game_output.close()

  # generating parsed games list:
  print("Parsing the SGF file...")
  print("Generating parsed games list...")

  parse_command = "python3 tournment_parse.py"
  os.system(parse_command)
  print("Parse complete")
  #=====================================================================================================================================
  # Generating B-Hex files using generate_gex_human_games.py:

  print("Generating B-Hex files...")
  bhex_generation_command = "python3 generate_gex_human_games.py --unrolling_depth " + str(args.unrolling_depth)
  os.system(bhex_generation_command)
  # printing number of files generated:
  bhex_files_list = glob.glob(os.path.join("intermediate_files/B-Hex", "*"))
  print("Complete, number of files created: ", len(bhex_files_list))
  #=====================================================================================================================================
  # Generate R-Gex, and only consider reachable instances
  # TODO
  #=====================================================================================================================================
  # Generate Gex, and only reachable instances (in Gex-format and EGF-format)
  # TODO
  #=====================================================================================================================================
  # Generate MR-Gex, and only reachable instances (in Gex-format and EGF-format)
  # TODO
  #=====================================================================================================================================
  # Generate PG_format (hypergraph), and only reachable instances
  # TODO
  #=====================================================================================================================================
  # Generate white flipped B-Hex, and only reachable instances (in EGF-format)
  # TODO
  #=====================================================================================================================================
  # Generate white flipped Gex, and only reachable instances (in EGF-format)
  # TODO
  #=====================================================================================================================================
