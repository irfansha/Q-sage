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

  print("======================================================================")
  # generating parsed games list:
  print("Parsing the SGF file...")
  print("Generating parsed games list...")

  parse_command = "python3 tournment_parse.py"
  os.system(parse_command)
  print("Parse complete")
  print("======================================================================")
  #=====================================================================================================================================
  # Generating B-Hex files using generate_gex_human_games.py:

  print("Generating B-Hex files...")
  bhex_generation_command = "python3 generate_gex_human_games.py --unrolling_depth " + str(args.unrolling_depth)
  os.system(bhex_generation_command)
  # printing number of files generated:
  bhex_files_list = glob.glob(os.path.join("intermediate_files/B-Hex", "*"))

  bhex_copy_command = "cp -r intermediate_files/B-Hex/ " + args.output_dir + "/"
  os.system(bhex_copy_command)
  print("Complete, number of files created: ", len(bhex_files_list))
  print("======================================================================")
  #=====================================================================================================================================
  # Generate R-Gex, and only consider reachable instances
  print("Generating R-GEX files...")
  reachable_instances = []
  # Generating R-Gex directory:
  if not Path(args.output_dir + "/R-Gex").is_dir():
    print("Creating new R-Gex directory in output folder.")
    os.mkdir(args.output_dir + "/R-Gex")

  # Generating R-Gex/Gex-format directory:
  if not Path(args.output_dir + "/R-Gex/Gex-format").is_dir():
    print("Creating new R-Gex/Gex-format directory in output folder.")
    os.mkdir(args.output_dir + "/R-Gex/Gex-format")


  print("Computing reachable R-Gex instances...")
  print("Writing to R-Gex/Gex_format folder in output folder in Gex format...")
  for file in bhex_files_list:
    cur_instance_name = file.split("/")[-1]
    # best to write to a file and read the contents:
    rgex_command = "python3 transform_hex_board.py  --prune_unreachable_nodes 1 --ignore_file_depth 1 --problem " +  file + " --depth " + str(args.instance_depth) + " > intermediate_files/cur_gex_file"
    #print(rgex_command)
    os.system(rgex_command)
    #print(file)
    # if file is not empty then we write it to the R-gex file and remember its name for next computations:
    if (os.stat("intermediate_files/cur_gex_file").st_size != 0):
      rgex_file_name = "depth_" + str(args.instance_depth) + "_" + cur_instance_name
      copy_command  = "cp intermediate_files/cur_gex_file " + args.output_dir + "/R-Gex/Gex-format/" + rgex_file_name
      os.system(copy_command)
      reachable_instances.append(cur_instance_name)
  print("Complete, number of reachable instances found: ", len(reachable_instances))
  print("---------------------------------------------------------------------")
  #-------------------------------------------------------------------------------------------------------------------------------------
  # first generating the EGF-format directory:
  # Generating R-Gex/EGF-format directory:
  if not Path(args.output_dir + "/R-Gex/EGF-format").is_dir():
    print("Creating new R-Gex/EGF-format directory in output folder.")
    os.mkdir(args.output_dir + "/R-Gex/EGF-format")
  print("Writing to R-Gex/EGF-format folder in output folder in EGF format...")
  # Generate R-Gex in EGF-format
  for file in reachable_instances:
    # we use the transform_hex_board.py to print in EGF-fromat:
    rgex_egf_command = "python3 transform_hex_board.py --output_format egf --problem " + args.output_dir + "/R-Gex/Gex-format/depth_" + str(args.instance_depth) + "_" + file + " > " + args.output_dir + "/R-Gex/EGF-format/depth_"  + str(args.instance_depth) + "_" + file
    #print(rgex_egf_command)
    os.system(rgex_egf_command)
  print("Complete.")
  print("======================================================================")
  #=====================================================================================================================================
  # Generate Gex, and only reachable instances (in Gex-format and EGF-format)
  print("Generating GEX files...")
  # Generating Gex directory:
  if not Path(args.output_dir + "/Gex").is_dir():
    print("Creating new Gex directory in output folder.")
    os.mkdir(args.output_dir + "/Gex")
  # Gex in Gex-format:
  # Generating Gex/Gex-format directory:
  if not Path(args.output_dir + "/Gex/Gex-format").is_dir():
    print("Creating new Gex/Gex-format directory in output folder.")
    os.mkdir(args.output_dir + "/Gex/Gex-format")
  print("Writing to Gex/Gex-format folder in output folder in Gex format...")
  # Generate R-Gex in EGF-format
  for file in reachable_instances:
    # we use the transform_hex_board.py to print in Gex-fromat:
    rgex_egf_command = "python3 transform_hex_board.py --problem intermediate_files/B-Hex/" + file + " > " + args.output_dir + "/Gex/Gex-format/depth_"  + str(args.instance_depth) + "_" + file
    #print(rgex_egf_command)
    os.system(rgex_egf_command)
  print("Complete.")
  print("---------------------------------------------------------------------")
  #-------------------------------------------------------------------------------------------------------------------------------------
  # Gex in EGF-format:
  # Generating Gex/EGF-format directory:
  if not Path(args.output_dir + "/Gex/EGF-format").is_dir():
    print("Creating new Gex/EGF-format directory in output folder.")
    os.mkdir(args.output_dir + "/Gex/EGF-format")
  print("Writing to Gex/EGF-format folder in output folder in EGF format...")
  # Generate R-Gex in EGF-format
  for file in reachable_instances:
    # we use the transform_hex_board.py to print in EGF-fromat:
    rgex_egf_command = "python3 transform_hex_board.py --output_format egf --problem intermediate_files/B-Hex/" + file + " > " + args.output_dir + "/Gex/EGF-format/depth_"  + str(args.instance_depth) + "_" + file
    #print(rgex_egf_command)
    os.system(rgex_egf_command)
  print("Complete.")
  print("======================================================================")
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
