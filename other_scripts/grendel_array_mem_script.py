import argparse
import glob
import os
import re

import linecache

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]

# Main:
if __name__ == '__main__':
  text = "Takes a output folder from array grendel"
  parser = argparse.ArgumentParser(description=text,formatter_class=argparse.RawTextHelpFormatter)
  parser.add_argument("--input", help="folders path")
  parser.add_argument("--time_type",help=" w/c (walltime/CPU-time) default = c",default = "c")
  args = parser.parse_args()


  # first parsing all the stats:
  # Now filling up the stats dictionary:

  stats_path = os.path.join(args.input, "stats.txt")
  f_stats = open(stats_path, "r")
  stats_lines = f_stats.readlines()
  f_stats.close()

  out_parsed_path = os.path.join(args.input, "parsed_stats.R")
  f_new_file = open(out_parsed_path,"w")

  # We gather max memory and time taken:
  max_mem = 0
  cpu_time = 0
  name = ''
  time_out = 0

  stats_dict = {}

  for line_index in range(len(stats_lines)):
    line = stats_lines[line_index]
    # we rest when we find the line with name:
    if ("Name" in line):
      if (name != ''):
        stats_dict[name] = (max_mem,cpu_time)
        #print(name, max_mem)
        if (time_out == 0):
          if (args.time_type == "c"):
            f_new_file.write(str(name) + " " + str(jobid) + " " + str(max_mem) + " " + str(cpu_time) + "\n")
          else:
            f_new_file.write(str(name) + " " + str(jobid) + " " + str(max_mem) + " " + str(wall_time) + "\n")
        else:
          f_new_file.write(str(name) + " " + str(jobid) + " " + str(max_mem) + " TO\n")
      # creating a new name line:
      name = line.strip("\n").split(" ")[-1]
      jobid = stats_lines[line_index-1].strip("\n").split(" ")[-1]
      #print(name)
      # resetting
      max_mem = 0
      wall_time = 0
      cpu_time = 0
      time_out = 0
    elif ("Max Mem used" in line):
      max_mem_string = line.split(" ")[-2]
      max_mem = round(float(max_mem_string[:-1]),2)
      # gigabites or megabites:
      notation = max_mem_string[-1]
      if (notation == "G"):
        max_mem = max_mem * 1000
        max_mem = round(float(max_mem),2)
    elif ("Used walltime" in line):
      wall_time = line.strip("\n").split(" ")[-1]
      split_wall_time = wall_time.split(":")
      wall_time = int(split_wall_time[2]) + int(split_wall_time[1])*60 + int(split_wall_time[0])*3600
      if (wall_time == 0):
        # avoiding the 0 seconds:
        wall_time = 0.1
    elif ("Used CPU time" in line):
      cpu_time = line.strip("\n").split(" ")[-1]
      split_cpu_time = cpu_time.split(":")
      cpu_time = int(split_cpu_time[2]) + int(split_cpu_time[1])*60 + int(split_cpu_time[0])*3600
      if (cpu_time == 0):
        # avoiding the 0 seconds:
        cpu_time = 0.1
    elif ("State" in line):
      if ("TIMEOUT" in line):
        time_out = 1

  stats_dict[name] = max_mem
  if (time_out == 0):
    if (args.time_type == "c"):
      f_new_file.write(str(name) + " " + str(jobid) + " " + str(max_mem) + " " + str(cpu_time) + "\n")
    else:
      f_new_file.write(str(name) + " " + str(jobid) + " " + str(max_mem) + " " + str(wall_time) + "\n")
  else:
    f_new_file.write(str(name) + " " + str(jobid) + " " + str(max_mem) + " TO\n")
  #f_new_file.write(str(name) + " " + str(max_mem) + " " + str(cpu_time) + "\n")
  # creating a new name line:
  f_new_file.close()
  #print(stats_dict)

  # now splitting the main parsed file into domain specific files:
  folder_list = glob.glob(os.path.join(args.input, "*"))
  folder_list.sort(key=natural_keys)

  # new_parsed_list with the right names:
  f_old_parsed = open(out_parsed_path,"r")
  f_old_parsed_lines = f_old_parsed.readlines()
  f_old_parsed.close()

  
  new_parsed_path = os.path.join(args.input, "clean_parsed_stats.R")
  f_new_parsed_file = open(new_parsed_path,"w")

  for line in f_old_parsed_lines:
    clean_line = line.strip("\n").split(" ")
    solver = clean_line[0].split("_")[0]
    preprocessor = clean_line[0].split("_")[1]
    domain = clean_line[0].split("_")[2]
    array_id = int(clean_line[1].split("_")[-1])
    print(clean_line)
    print(solver,preprocessor,domain,array_id)
    for cur_folder in folder_list:
      #print(domain, cur_folder.split("_")[-1], preprocessor,cur_folder.split("_")[-2].split("/")[-1])
      if (domain == cur_folder.split("_")[-1] and preprocessor == cur_folder.split("_")[-2].split("/")[-1]):
        reference_file_name = os.path.join(cur_folder,solver,"array_reference_list.txt")
        print(reference_file_name, cur_folder.split("_")[-2].split("/")[-1])
        data_file_path = os.path.join(cur_folder,solver,"out_" + str(array_id))
        print(line,data_file_path)
        # we grab the satisfiability and unsatisfiability from the file:
        with open(data_file_path, 'r') as file:
          # read all content from a file using read()
          content = file.read()
          if ("UNSAT" in content or "s cnf 0" in content or "c Unsatisfiable" in content or "Result: FALSE" in content):
            status = "UNSAT"
          elif("SAT" in content or "s cnf 1" in content or "c Satisfiable" in content or "Result: TRUE" in content):
            status = "SAT"
          else:
            status = "NA"
        f_data_file = open(data_file_path,"r")
        f_data_file_lines = f_data_file.readlines()
        cur_line = linecache.getline(reference_file_name,array_id)
        only_file_name = cur_line.strip("\n").split("/")[-1]
        f_new_parsed_file.write("_".join([solver, preprocessor, domain, only_file_name]) + " " + status + " " + clean_line[-2] + " " + clean_line[-1] + "\n")
