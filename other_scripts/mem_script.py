#stats_file_paths = ["explicit_gex_symbolic_stats","explicit_gex_witness_stats",
#                    "implicit_gex_symbolic_1_hour_stats","implicit_gex_symbolic_3_hour_stats",
#                    "implicit_gex_witness_1_hour_stats","implicit_gex_witness_3_hour_stats"]

stats_file_paths = ["cor_stats"]

for i in range(1):
  # Now filling up the stats dictionary:
  f_stats = open(stats_file_paths[i], "r")
  stats_lines = f_stats.readlines()
  f_stats.close()

  f_new_file = open("parsed_" + stats_file_paths[i] + ".R","w")

  # We gather max memory and time taken:
  max_mem = 0
  cpu_time = 0
  name = ''

  stats_dict = {}

  for line in stats_lines:
    # we rest when we find the line with name:
    if ("Name" in line):
      if (name != ''):
        stats_dict[name] = (max_mem,cpu_time)
        #print(name, max_mem)
        f_new_file.write(str(name) + " " + str(max_mem) + " " + str(cpu_time) + "\n")
      # creating a new name line:
      name = line.strip("\n").split(" ")[-1]
      #print(name)
      # resetting
      max_mem = 0
    elif ("Max Mem used" in line):
      max_mem_string = line.split(" ")[-2]
      max_mem = round(float(max_mem_string[:-1]),2)
      # gigabites or megabites:
      notation = max_mem_string[-1]
      if (notation == "G"):
        max_mem = max_mem * 1000
        max_mem = round(float(max_mem),2)
    elif ("Used CPU time" in line):
      cpu_time = line.strip("\n").split(" ")[-1]
      split_cpu_time = cpu_time.split(":")
      cpu_time = int(split_cpu_time[2]) + int(split_cpu_time[1])*60 + int(split_cpu_time[0])*3600
      if (cpu_time == 0):
        # avoiding the 0 seconds:
        cpu_time = 0.1

  stats_dict[name] = max_mem
  f_new_file.write(str(name) + " " + str(max_mem) + " " + str(cpu_time) + "\n")
  # creating a new name line:
  f_new_file.close()
  #print(stats_dict)
