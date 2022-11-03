# Irfansha Shaik, 26.07.2022, Aarhus.

from collections import Counter

import matplotlib.pyplot as plt
import pandas as pd

int_timeout = 9999
mem_timeout = 99999

def accumulate(sub_data_frame):
  time_list = sub_data_frame["time"].tolist()
  no_timeout_list = list(filter((int_timeout).__ne__, time_list))
  #print(time_list)

  # we set the memory to mem_timeout if there is a timeout:, so we remove them:
  mem_list = sub_data_frame["mem"].tolist()
  no_timeout_memlist = list(filter((mem_timeout).__ne__, mem_list))

  num_solved = len(no_timeout_list)
  total_time = sum(no_timeout_list)
  mem_total = round(sum(no_timeout_memlist),2)
  avg_time = "-"
  if (num_solved != 0):
    avg_time = round(total_time/num_solved,2)

  avg_mem = "-"
  if (num_solved != 0):
    avg_mem = round(mem_total/num_solved,2)

  return num_solved, total_time, avg_time, mem_total, avg_mem

# recieves a list of some data, either time or memory
# generates the data list with accumuates number of data points under the limit for cactus plot:
def cactus_data(lst, exclude_value):
  # first remove timeout times
  filtered_lst = list(filter((exclude_value).__ne__, lst))

  sorted_counter_list = sorted(Counter(filtered_lst).items())

  # counting all the instances under x value:
  count = 0
  plot_list_data = []
  plot_list_count_data = []

  for counter_tuple in sorted_counter_list:
    count = count + counter_tuple[1]
    plot_list_data.append(counter_tuple[0])
    plot_list_count_data.append(count)
  
  return plot_list_data, plot_list_count_data



#f_stats = open("all_stats_second_run_hein_wf_rgex.R", "r")
#f_stats = open("all_champ_27_stats.R", "r")
#f_stats = open("all_27_stats_final_run_white_rgex.R", "r")
f_stats = open("unsat_27_stats_final_white_rgex.R", "r")
#f_stats = open("unsat_second_run_wf_rgex.R", "r")
stats_lines = f_stats.readlines()
f_stats.close()

#for line in stats_lines:
#  print(line)

# creating a list of integers as indexes:
index_list = list(range(1,len(stats_lines)+1))

#print(index_list)


# we create time dictionary,
# here we remember the required slices of time data:
time_dict = dict()


# we create mem dictionary,
# here we remember the required slices of mem data:
mem_dict = dict()


df = pd.DataFrame(columns=["solver", "preprocessor", "format", "encoding", "instance", "mem", "time"], index=index_list,dtype=object)

for i in range(len(stats_lines)):
  cur_split_line = stats_lines[i].strip("\n").split("_")
  solver = cur_split_line[1]
  preprocessor = cur_split_line[2]
  format_type = cur_split_line[3]
  # specifying if the instance is moved, in the prerpocessing:
  if ("-M" in cur_split_line[4]):
    preprocessor = "M-" + preprocessor
    encoding = cur_split_line[4][:-2]
  else:
    encoding = cur_split_line[4]
  # gathering the memory and time from last split cell:
  last_split_cell = cur_split_line[-1].split(" ")
  # can be made into interger if needed:
  if (last_split_cell[-1] == "TO"):
    time = int_timeout
  else:
    time = float(last_split_cell[-1])
  if (last_split_cell[-1] == "TO"):
    mem = mem_timeout
  else:
    mem = float(last_split_cell[-2])
  # instance name:
  instance = cur_split_line[5] + "_" + cur_split_line[6] + "_" + cur_split_line[7][:6]
  df.loc[i+1,:] = [solver, preprocessor, format_type, encoding, instance, mem, time]

#print(df.to_string())



print("=================================================================")
#================================================================================================================================================
# qcir solvers:
#================================================================================================================================================
# checking circuit encodings:
qcir_solvers = ["CT", "QF", "QT", "QU"]
qcir_encodings = ["LL", "SW", "SWB"]
for qcir_encoding in qcir_encodings:
  for solver in qcir_solvers:
    cur_subdf = df[(df['encoding'] == qcir_encoding) & (df['solver'] == solver) & (df['format'] == 'QC')]
    #print(solver, qcir_encoding)
    # 4 tuple as key: (encoding, solver, preprocessor and format):
    time_dict[(qcir_encoding,solver,'N','QC')] = cur_subdf['time'].tolist()
    # 4 tuple as key: (encoding, solver, preprocessor and format):
    mem_dict[(qcir_encoding,solver,'N','QC')] = cur_subdf['mem'].tolist()
    num_solved, total_time, avg_time, mem_total, avg_mem = accumulate(cur_subdf)
    print(qcir_encoding, solver,"  :  ", num_solved, total_time, avg_time, mem_total, avg_mem)
  print("------------------------------------------")

print("=================================================================")
#================================================================================================================================================
# QDIMACS solvers:
#================================================================================================================================================
qdimacs_solvers = ["CQ","DQ","QE","QT"]
# we take input preprocessor folder names, we also add empty string for no preprocessing:
preprocessors = ["N", "B", "H", "Q"]
mpreprocessors =["M-N", "M-B", "M-H", "M-Q"]

expb_encodings = ["EBL", "EBP","EBWD"]
impb_encodings = ["LL","SWB", "LE", "SWE"]

# checking explicit board qdimacs encodings:
for expb_encoding in expb_encodings:
  for solver in qdimacs_solvers:
    for preprocessor in preprocessors:
      cur_subdf = df[(df['encoding'] == expb_encoding) & (df['solver'] == solver) & (df['preprocessor'] == preprocessor) & (df['format'] == 'QD')]
      time_dict[(expb_encoding,solver,preprocessor,'QD')] = cur_subdf['time'].tolist()
      mem_dict[(expb_encoding,solver,preprocessor,'QD')] = cur_subdf['mem'].tolist()
      num_solved, total_time, avg_time, mem_total, avg_mem = accumulate(cur_subdf)
      print(expb_encoding, solver, preprocessor, "  :  ", num_solved, total_time, avg_time, mem_total, avg_mem)
  print("------------------------------------------")
print("=================================================================")

# checking implicit board qdimacs encodings:
for impb_encoding in impb_encodings:
  for solver in qdimacs_solvers:
    for preprocessor in preprocessors:
      cur_subdf = df[(df['encoding'] == impb_encoding) & (df['solver'] == solver) & (df['preprocessor'] == preprocessor) & (df['format'] == 'QD')]
      time_dict[(impb_encoding,solver,preprocessor,'QD')] = cur_subdf['time'].tolist()
      mem_dict[(impb_encoding,solver,preprocessor,'QD')] = cur_subdf['mem'].tolist()
      num_solved, total_time, avg_time, mem_total, avg_mem = accumulate(cur_subdf)
      print(impb_encoding, solver, preprocessor, "  :  ", num_solved, total_time, avg_time, mem_total, avg_mem)
  print("------------------------------------------")
print("=================================================================")
# checking implicit board qdimacs encodings with moved preprocessors:
for impb_encoding in impb_encodings:
  for solver in qdimacs_solvers:
    for mpreprocessor in mpreprocessors:
      cur_subdf = df[(df['encoding'] == impb_encoding) & (df['solver'] == solver) & (df['preprocessor'] == mpreprocessor) & (df['format'] == 'QD')]
      time_dict[(impb_encoding,solver,mpreprocessor,'QD')] = cur_subdf['time'].tolist()
      mem_dict[(impb_encoding,solver,mpreprocessor,'QD')] = cur_subdf['mem'].tolist()
      num_solved, total_time, avg_time, mem_total, avg_mem = accumulate(cur_subdf)
      print(impb_encoding, solver, mpreprocessor, "  :  ", num_solved, total_time, avg_time, mem_total, avg_mem)
  print("------------------------------------------")
print("=================================================================")

'''
best_combinations = [("SW","CT","N","QC"),("EBP","CQ","B","QD"),("EBL","CQ","N","QD"),("EBWD","CQ","H","QD"),("LL","CQ","B","QD"),("SWB","CQ","B","QD")]
labels = ["SW-CT","EBP-CQ-B","EBL-CQ","EBWD-CQ-H","LL-CQ-B","SWB-CQ-B"]
'''
#'''
best_combinations = [("SWB","CQ","B","QD"), ("LL","CQ","B","QD"), ("EBL","CQ","B","QD"), ("EBWD","CQ","B","QD")]
labels = ["SN","LN","EN","ET"]
markers = ['x','+','^','<',]
colors = ['m','c','g','r']
#'''

'''
best_combinations = [("EBP","CQ","B","QD"),("EBL","CQ","B","QD"),("EBWD","CQ","B","QD"),("LL","CQ","B","QD"),("SWB","CQ","B","QD"), ("LE","CQ","B","QD"), ("SWE","CQ","B","QD") ]
labels = ["EA","EN","ET","LN","SN", "LA","SA"]


markers = ['v','^','<','+','x','.','o']
colors = ["b","g","r","c","m","k","y"]
'''

#=======================================================================================
# time plot:
#=======================================================================================
'''
for index in range(len(best_combinations)):
  b_comb = best_combinations[index]
  time_lst, count_lst =  cactus_data(time_dict[(b_comb)], int_timeout)
  plt.scatter(count_lst, time_lst, label = labels[index],marker = markers[index], color=colors[index])

plt.grid()
plt.xlabel("Cumulative instances solved")
plt.ylabel("time taken in sec (log scale)")
plt.yscale('log')
plt.legend()
plt.show()
'''
#=======================================================================================

#=======================================================================================
# mem plot:
#=======================================================================================
#'''
for index in range(len(best_combinations)):
  b_comb = best_combinations[index]
  #if ("EB" not in b_comb[0]):
  #  continue
  mem_lst, count_lst =  cactus_data(mem_dict[(b_comb)], mem_timeout)
  print(mem_lst, count_lst,b_comb)
  #''
  if (mem_lst[0] == 1.4):
    mem_lst.pop(0)
    count_lst.pop(0)
  if (mem_lst[0] == 1.41):
    mem_lst.pop(0)
    count_lst.pop(0)
  #''
  print(mem_lst, count_lst)
  #plt.scatter(count_lst[2:], mem_lst[2:], label = labels[index],marker = markers[index])
  plt.scatter(count_lst, mem_lst, label = labels[index],marker = markers[index],color=colors[index])
plt.grid()
plt.xlabel("Cumulative instances solved")
plt.ylabel("mem taken in mb (log scale) ")
plt.yscale('log')
plt.legend()
plt.show()
#'''
#=======================================================================================
