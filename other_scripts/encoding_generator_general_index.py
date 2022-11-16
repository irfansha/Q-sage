# Irfansha Shaik, 18.07.2022, Aarhus

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
  text = "Generate QCIR and QDIMACS encodings for general index games"
  parser = argparse.ArgumentParser(description=text,formatter_class=argparse.RawTextHelpFormatter)
  parser.add_argument("--output_dir", help="path to output directory", default = "intermediate_files/output/")
  parser.add_argument("--input_dir", help="path to input directory")
  parser.add_argument("--game", help=textwrap.dedent('''
                                  game type:
                                  D = domineering
                                  C4 = connect4/connect-c
                                  PG = positional games (with hex)
                                  B = Breakthrough
                                  EP = evader-pursuer)'''),default = 'NA')
  parser.add_argument("--preprocessor_path", help="path to preprocessor directory (expecting bloqqer)", default = "tools/Bloqqer/bloqqer")
  args = parser.parse_args()

  #====================================================================================
  # QCIR-14 encodings
  #====================================================================================
  # lifted:
  #-------------------------------------------------------------------
  encoding_formats = ["qcir", "qdimacs"]
  for i in range(len(encoding_formats)):

    cur_encoding_format = encoding_formats[i]
    # we specify the encoding formats for the Q-sage explicitly:
    if (cur_encoding_format == "qcir"):
      input_encoding_format = 1
    else:
      input_encoding_format = 2

    if not Path(args.output_dir).is_dir():
      print("Creating new directory for output folder.")
      os.mkdir(args.output_dir)

    for encoding in ['ib','nib','dnib']:
      if (args.game == "D"):
        for x in range(4,7):
          for y in range(4,7):
            max_moves = int((x*y)/2)
            print(x,y,max_moves)
            if(max_moves%2 == 0):
              depth = max_moves + 1
            else:
              depth = max_moves
            if (depth <14):
              command = "python3 Q-sage.py --run 0 --ignore_file_depth 1 --ignore_file_boardsize 1 --game_type general --ib_domain " + os.path.join(args.input_dir, "domain.ig") + " --ib_problem " + os.path.join(args.input_dir, "problem.ig")  + " -e "+ encoding  +  " --xmax " + str(x) + " --ymax " + str(y) + " --depth " + str(depth) + " --encoding_format " + str(input_encoding_format) + " --encoding_out " + args.output_dir + "_".join([str(x),str(y),str(depth),args.game,encoding]) + "." + cur_encoding_format
              print(command)
              os.system(command)
        print("========================================================================")
      elif(args.game == "PG"):
        # first httt:
        # for now only 4 board size
        for board_size in range(4,5):
          if (board_size == 3):
            depth = 9
          elif(board_size == 4):
            depth = 11
          print(board_size,depth)
          # first listing all shapes:
          shapes_files_list = glob.glob(args.input_dir + "/httt/*")
          shapes_files_list.sort(key=natural_keys)
          for file in shapes_files_list:
            file_name = file.split("/")[-1][:-3]
            command = "python3 Q-sage.py --run 0 --ignore_file_depth 1 --ignore_file_boardsize 1 --game_type general --ib_domain " + os.path.join(args.input_dir, "domain.ig") + " --ib_problem " + file  + " -e "+ encoding  +  " --xmax " + str(board_size) + " --ymax " + str(board_size) + " --depth " + str(depth) + " --encoding_format " + str(input_encoding_format) + " --encoding_out " + args.output_dir + "_".join([str(board_size),str(board_size),str(depth),args.game,file_name,encoding]) + "." + cur_encoding_format
            print(command)
            os.system(command)
        print("========================================================================")

        # hex:
        hex_files_list = glob.glob(args.input_dir + "/hex/*")
        hex_files_list.sort(key=natural_keys)
        for file in hex_files_list:
          file_name = file.split("/")[-1][:-3]
          command = "python3 Q-sage.py --run 0 --ignore_file_depth 0 --ignore_file_boardsize 1 --game_type general --ib_domain " + os.path.join(args.input_dir, "domain.ig") + " --ib_problem " + file  + " -e "+ encoding  +  " --xmax " + str(board_size) + " --ymax " + str(board_size) + " --encoding_format " + str(input_encoding_format) + " --encoding_out " + args.output_dir + "_".join([args.game,file_name,encoding]) + "." + cur_encoding_format
          print(command)
          os.system(command)
        print("========================================================================")
      elif(args.game == "C4"):
        for board_size in range(4,7):
          for c in range(2,5):
            for depth in range(11,14):
              if (depth%2 == 1):
                command = "python3 Q-sage.py --run 0 --ignore_file_depth 1 --ignore_file_boardsize 1 --game_type general --ib_domain " + os.path.join(args.input_dir, "domain.ig") + " --ib_problem " + os.path.join(args.input_dir, "connect" + str(c)+".ig")  + " -e "+ encoding  +  " --xmax " + str(board_size) + " --ymax " + str(board_size) + " --depth " + str(depth) + " --encoding_format " + str(input_encoding_format) + " --encoding_out " + args.output_dir + "_".join([str(board_size),str(board_size),str(depth),args.game,encoding]) + "." + cur_encoding_format
                print(command)
                os.system(command)
        print("========================================================================")
      elif(args.game == "B"):
        B_files_list = glob.glob(args.input_dir + "/*")
        B_files_list.sort(key=natural_keys)

        for depth in range(7,12):
          if (depth%2 == 1):
            for file in B_files_list:
              if ("domain" not in file):
                file_name = file.split("/")[-1][:-3]
                command = "python3 Q-sage.py --run 0 --ignore_file_depth 1 --game_type general --ib_domain " + os.path.join(args.input_dir, "domain.ig") + " --ib_problem " + file  + " -e "+ encoding  +  " --encoding_format " + str(input_encoding_format) + " --depth " + str(depth) + " --encoding_out " + args.output_dir + "_".join([args.game,str(depth),file_name,encoding]) + "." + cur_encoding_format
                print(command)
                os.system(command)
        print("========================================================================")
      elif(args.game == "EP"):
        EP_files_list = glob.glob(args.input_dir + "/*")
        EP_files_list.sort(key=natural_keys)

        for depth in range(5,10):
          if (depth%2 == 1):
            for file in EP_files_list:
              if ("domain" not in file):
                file_name = file.split("/")[-1][:-3]
                command = "python3 Q-sage.py --run 0 --ignore_file_depth 1 --game_type general --ib_domain " + os.path.join(args.input_dir, "domain.ig") + " --ib_problem " + file  + " -e "+ encoding  +  " --encoding_format " + str(input_encoding_format) + " --depth " + str(depth) + " --encoding_out " + args.output_dir + "_".join([args.game,str(depth),file_name,encoding]) + "." + cur_encoding_format
                print(command)
                os.system(command)
        print("========================================================================")



        
#====================================================================================================================================================================================================================================

# for now using a special folder directly:
qdimacs_files_list = glob.glob(args.output_dir + "/*.qdimacs")
qdimacs_files_list.sort(key=natural_keys)

# Preprocess with bloqqer:
for file in qdimacs_files_list:
  command = "./" + args.preprocessor_path + " --timeout=100 " + file + " > " + file + ".bloqqer"
  print(command)
  os.system(command)


# some qcir dolvers do not take comments:
qcir_files_list = glob.glob(args.output_dir + "/*.qcir")
qcir_files_list.sort(key=natural_keys)
for file in qcir_files_list:
  command = "sed -i '/#/d' " + file
  print(command)
  os.system(command)
  command = "sed -i '1 i\#QCIR-G14' " + file
  print(command)
  os.system(command)
