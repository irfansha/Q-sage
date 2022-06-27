# Irfansha Shaik, 04.01.2022, Aarhus.


import argparse, textwrap
import glob
import re
import os
from pathlib import Path



def atoi(text):
  return int(text) if text.isdigit() else text

def natural_keys(text):
  return [ atoi(c) for c in re.split(r'(\d+)', text) ]

def parse_file(file_path, f_out):
  f = open(file_path, 'r')
  lines = f.readlines()
  f.close()

  # extracting the file name without whole path assuming linux:
  parsed_file_path = file_path.split("/")
  file_name = parsed_file_path[-1].split("_")

  problem_name = '_'.join(file_name[:-1])

  for line in lines:
    if ('====> ERROR from solver <====' in line):
      status = 'none'
    elif ('Plan found' in line):
      status = 'sat'
    elif ('Plan not found' in line):
      status = 'unsat'
    elif ('Solving time:' in line):
      time_line = line.split(" ")
      cur_time = time_line[-1]

  #if (status == 'sat'):
  f_out.write(problem_name + " " + status + " " + cur_time)

# Main:
if __name__ == '__main__':
  text = "Parses data files and generates R files"
  parser = argparse.ArgumentParser(description=text,formatter_class=argparse.RawTextHelpFormatter)
  parser.add_argument("--dir", help="directory path", default = 'data/')
  parser.add_argument("--output_dir", help="output directory path for generated R files", default = 'parsed_data/')
  parser.add_argument("--outfile", help="output file name", default = 'data.R')
  args = parser.parse_args()


  # Checking if directory exists:
  if not Path(args.dir).is_dir():
    print("Invalid directory path: " + args.dir)
    exit
  files_list = glob.glob(args.dir + "*")
  files_list.sort(key=natural_keys)

  # Checking if out directory exits:
  if not Path(args.output_dir).is_dir():
    print("Invalid directory path: " + args.output_dir)
    print("Creating new directory with same path.")
    os.mkdir(args.output_dir)

  # Opening out file in the out directory:
  f_out = open(args.output_dir + args.outfile, "w+")

  # Parsing each file seperately:
  for file_path in files_list:
    parse_file(file_path, f_out)
  f_out.close()
