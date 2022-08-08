# Irfansha Shaik, 08.08.2022, Aarhus

import argparse
import os

# Main:
if __name__ == '__main__':
  text = "Takes a R-Gex file and Gex white flipped file and generates R-Gex-white flipped file"
  parser = argparse.ArgumentParser(description=text,formatter_class=argparse.RawTextHelpFormatter)
  parser.add_argument("--r_gex_problem", help="reference R-Gex file path")
  parser.add_argument("--white_flipped_bhex_problem", help="white-flipped B-Hex file path")

  args = parser.parse_args()

  #=====================================================================================================================================
  # parsing R-Gex file and remembering open positions and depth of the instance:

  f = open(args.r_gex_problem, 'r')
  lines = f.readlines()
  f.close()

  parsed_dict = {}

  for line in lines:
    stripped_line = line.strip("\n").strip(" ").split(" ")
    # we ignore if it is a comment:
    if ('%' == line[0] or line == '\n'):
      continue
    if ("#" in line):
      new_key = line.strip("\n")
      parsed_dict[new_key] = []
    else:
      parsed_dict[new_key].append(stripped_line)

  #for key,value in parsed_dict.items():
  #  print(key, value)

  r_gex_positions = parsed_dict['#positions'][0]

  r_gex_depth = len(parsed_dict['#times'][0])

  #print(r_gex_positions)
  #print(r_gex_depth)
  #=====================================================================================================================================
  # first gex transformation:
  wb_gex_command = "python3 transform_hex_board.py --ignore_file_depth 1 --output_format gex --problem " + str(args.white_flipped_bhex_problem) + " --depth " + str(r_gex_depth) + " > temp_white_flip_gex_transformation.pg"
  os.system(wb_gex_command)
  #=====================================================================================================================================
  # parsing:

  f = open("temp_white_flip_gex_transformation.pg", 'r')
  lines = f.readlines()
  f.close()

  parsed_dict = {}

  for line in lines:
    stripped_line = line.strip("\n").strip(" ").split(" ")
    # we ignore if it is a comment:
    if ('%' == line[0] or line == '\n'):
      continue
    if ("#" in line):
      new_key = line.strip("\n")
      parsed_dict[new_key] = []
    else:
      parsed_dict[new_key].append(stripped_line)

  positions = parsed_dict['#positions'][0]

  #=====================================================================================================================================
  #  writing everything to another file:
  f = open("temp_white_flip_rgex_transformation.pg","w")
  f.write("#blackinitials\n")
  for pos in positions:
    if (pos not in r_gex_positions):
      f.write(pos + "\n")
  # add black, i.e., everything not in the original R-Gex file:
  f.write("#whiteinitials\n")
  f.write("#times" + "\n")
  f.write(" ".join(parsed_dict["#times"][0]) + "\n")
  f.write("#blackturns" + "\n")
  f.write(" ".join(parsed_dict["#blackturns"][0]) + "\n")
  f.write("#positions" + "\n")
  f.write(" ".join(positions) + "\n")
  f.write("#neighbours" + "\n")
  for line in parsed_dict["#neighbours"]:
    f.write(" ".join(line) + "\n")
  f.write("#startboarder" + "\n")
  f.write(" ".join(parsed_dict["#startboarder"][0]) + "\n")
  f.write("#endboarder" + "\n")
  f.write(" ".join(parsed_dict["#endboarder"][0]) + "\n")
  f.close()

  #=====================================================================================================================================
  # Running the final Gex transformation:

  wb_gex_command = "python3 transform_hex_board.py --output_format egf --problem temp_white_flip_rgex_transformation.pg"
  os.system(wb_gex_command)
