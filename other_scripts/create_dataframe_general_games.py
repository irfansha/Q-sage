# Irfansha Shaik, 26.07.2022, Aarhus.

from collections import Counter

import matplotlib.pyplot as plt
import pandas as pd

import argparse

int_timeout = 99999
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



# Main:
if __name__ == '__main__':
  text = "Takes a parsed grendel data"
  parser = argparse.ArgumentParser(description=text,formatter_class=argparse.RawTextHelpFormatter)
  parser.add_argument("--input", help="stats file path")
  args = parser.parse_args()

f_stats = open(args.input,"r")
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


df = pd.DataFrame(columns=["solver", "preprocessor", "domain", "format", "encoding", "instance", "status", "mem", "time"], index=index_list,dtype=object)

for i in range(len(stats_lines)):

  cur_line = stats_lines[i].strip("\n").split(" ")
  #print(cur_line)
  # can be made into interger if needed:
  if (cur_line[-1] == "TO"):
    time = int_timeout
  else:
    time = float(cur_line[-1])
  if (cur_line[-1] == "TO"):
    mem = mem_timeout
  else:
    mem = float(cur_line[-2])
  
  # for solver:
  if ("CQ" in cur_line[0]):
    solver = "CQ"
  elif ("DQ" in cur_line[0]):
    solver = "DQ"
  elif ("CT" in cur_line[0]):
    solver = "CT"
  elif ("QU" in cur_line[0]):
    solver = "QU"
  elif ("QB" in cur_line[0]):
    solver = "QB"

  # format:
  if ("qcir" in cur_line[0]):
    format_type = "cir"
  elif ("dimacs" in cur_line[0]):
    format_type = "qdim"

  #format_type = "qdim"

  '''
  # encoding:
  if ("_bwnib" in cur_line[0]):
    encoding = "bwnib"
  elif ("_nib" in cur_line[0]):
    encoding = "nib"
  elif ("_dnib" in cur_line[0]):
    encoding = "dnib"
  '''

  # encoding:
  if ("_pgt_" in cur_line[0]):
    encoding = "LT"
  elif ("_EA_" in cur_line[0]):
    encoding = "EA"
  elif ("_ET_" in cur_line[0]):
    encoding = "ET"
  elif ("_EN_" in cur_line[0]):
    encoding = "EN"
  elif ("_LN_" in cur_line[0] or "_pg_" in cur_line[0] or "_LL_" in cur_line[0]):
    encoding = "LN"
  elif ("_SN_" in cur_line[0] or "_cp_" in cur_line[0]):
    #print(cur_line[0])
    encoding = "SN"
  elif ("_COR_" in cur_line[0]):
    encoding = "COR"
  elif ("_LA_" in cur_line[0]):
    encoding = "LA"
  elif ("_SA_" in cur_line[0]):
    encoding = "SA"

  #print(encoding)



  # preprocessor:
  if ("_B_" in cur_line[0]):
    preprocessor = "B"
  elif("_H_" in cur_line[0]):
    preprocessor = "H"
  elif("_Q_" in cur_line[0]):
    preprocessor = "Q"
  else:
    preprocessor = "N"


  # domain:
  '''
  if ("_B_" in cur_line[0]):
    domain = "B"
  elif ("_BSP_" in cur_line[0]):
    domain = "BSP"
  elif ("_C4_" in cur_line[0]):
    domain = "C4"
  elif ("_EP_" in cur_line[0]):
    domain = "EP"
  elif ("_hex_" in cur_line[0]):
    domain = "hex"
  elif ("_httt_" in cur_line[0]):
    domain = "httt"
  else:
    domain = "NA"
  '''
  domain = "NA"

  status = cur_line[-3]
  assert(status in ["UNSAT", "SAT", "NA"])
  #status = "UNSAT"

  # instance name:
  instance = "N"
  df.loc[i+1,:] = [solver, preprocessor, domain, format_type, encoding, instance, status, mem, time]

  #print(solver, preprocessor, format_type, encoding, instance, mem, time)
#print(df.to_string())


#print(len(df))
print("=================================================================")
print("SAT data")
print("=================================================================")
#===========================================================================================================================================================================
#================================================================================================================================================
# qcir solvers:
#================================================================================================================================================
# SAT instances:
# checking circuit encodings:
#qcir_solvers = ["CT", "QU"]
qcir_solvers = ["QB"]
qcir_encodings = ["LN", "SN","LT"]
preprocessors = ["B","N"]
for qcir_encoding in qcir_encodings:
  for solver in qcir_solvers:
    for preprocessor in preprocessors:
      #print(df)
      cur_subdf = df[(df['encoding'] == qcir_encoding) & (df['solver'] == solver) & (df['preprocessor'] == preprocessor) & (df['format'] == 'cir') & (df['status'] == 'SAT')]
      #print(solver, qcir_encoding)
      # 4 tuple as key: (encoding, solver, preprocessor and format):
      time_dict[(qcir_encoding,solver, 'SAT', preprocessor,'cir')] = cur_subdf['time'].tolist()
      # 4 tuple as key: (encoding, solver, preprocessor and format):
      mem_dict[(qcir_encoding,solver, 'SAT',preprocessor,'cir')] = cur_subdf['mem'].tolist()
      num_solved, total_time, avg_time, mem_total, avg_mem = accumulate(cur_subdf)
      print(qcir_encoding, solver, preprocessor,"  :  ", str(num_solved), round(total_time, 2), avg_time, mem_total, avg_mem)
  print("------------------------------------------")

print("=================================================================")

#================================================================================================================================================
# QDIMACS solvers:
#================================================================================================================================================
qdimacs_solvers = ["CQ","DQ"]
# we take input preprocessor folder names, we also add empty string for no preprocessing:
preprocessors = ["B","H","Q","N"]
#mpreprocessors =["M-N", "M-B", "M-H", "M-Q"]

#encodings = ["bwnib"]
encodings = ["COR","EA","EN","ET","LN","SN","LT"]
# checking qdimacs encodings:
for expb_encoding in encodings:
  for solver in qdimacs_solvers:
    for preprocessor in preprocessors:
      cur_subdf = df[(df['encoding'] == expb_encoding) & (df['solver'] == solver) & (df['preprocessor'] == preprocessor) & (df['format'] == 'qdim')& (df['status'] == 'SAT')]
      time_dict[(expb_encoding,solver, "SAT" ,preprocessor,'qdim')] = cur_subdf['time'].tolist()
      mem_dict[(expb_encoding,solver,"SAT", preprocessor,'qdim')] = cur_subdf['mem'].tolist()
      num_solved, total_time, avg_time, mem_total, avg_mem = accumulate(cur_subdf)
      print(expb_encoding, solver, preprocessor, "  :  ", str(num_solved)   , round(total_time, 2), avg_time, mem_total, avg_mem)
  print("------------------------------------------")
print("=================================================================")
print("UNSAT data")
print("=================================================================")
#=================================================================================================================================================
# UNSAT instances:
preprocessors = ["B","N"]
# checking circuit encodings:
for qcir_encoding in qcir_encodings:
  for solver in qcir_solvers:
    for preprocessor in preprocessors:
      cur_subdf = df[(df['encoding'] == qcir_encoding) & (df['solver'] == solver) & (df['preprocessor'] == preprocessor) & (df['format'] == 'cir') & (df['status'] == 'UNSAT')]
      #print(solver, qcir_encoding)
      # 4 tuple as key: (encoding, solver, preprocessor and format):
      time_dict[(qcir_encoding,solver, 'UNSAT',preprocessor,'cir')] = cur_subdf['time'].tolist()
      # 4 tuple as key: (encoding, solver, preprocessor and format):
      mem_dict[(qcir_encoding,solver, 'UNSAT',preprocessor,'cir')] = cur_subdf['mem'].tolist()
      num_solved, total_time, avg_time, mem_total, avg_mem = accumulate(cur_subdf)
      print(qcir_encoding, solver, preprocessor,"  :  ", str(num_solved), round(total_time, 2), avg_time, mem_total, avg_mem)
  print("------------------------------------------")

print("=================================================================")

#UNSAT
preprocessors = ["B","H","Q","N"]
# checking qdimacs encodings:
for expb_encoding in encodings:
  for solver in qdimacs_solvers:
    for preprocessor in preprocessors:
      cur_subdf = df[(df['encoding'] == expb_encoding) & (df['solver'] == solver) & (df['preprocessor'] == preprocessor) & (df['format'] == 'qdim')& (df['status'] == 'UNSAT')]
      time_dict[(expb_encoding,solver, "UNSAT" ,preprocessor,'qdim')] = cur_subdf['time'].tolist()
      mem_dict[(expb_encoding,solver,"UNSAT", preprocessor,'qdim')] = cur_subdf['mem'].tolist()
      num_solved, total_time, avg_time, mem_total, avg_mem = accumulate(cur_subdf)
      print(expb_encoding, solver, preprocessor, "  :  ", str(num_solved)  , round(total_time, 2), avg_time, mem_total, avg_mem)
  print("------------------------------------------")
print("=================================================================")
#===========================================================================================================================================================================
#all data:
print("=================================================================")
print("ALL data")
print("=================================================================")
#===========================================================================================================================================================================
# checking circuit encodings:
#qcir_solvers = ["CT", "QU"]
qcir_solvers = ["QB"]
qcir_encodings = ["LN", "SN","LT"]
preprocessors = ["B","N"]
for qcir_encoding in qcir_encodings:
  for solver in qcir_solvers:
    for preprocessor in preprocessors:
      cur_subdf = df[(df['encoding'] == qcir_encoding) & (df['solver'] == solver) & (df['preprocessor'] == preprocessor) & (df['format'] == 'cir')]
      #print(solver, qcir_encoding)
      # 4 tuple as key: (encoding, solver, preprocessor and format):
      time_dict[(qcir_encoding,solver, 'ALL',preprocessor,'cir')] = cur_subdf['time'].tolist()
      # 4 tuple as key: (encoding, solver, preprocessor and format):
      mem_dict[(qcir_encoding,solver, 'ALL',preprocessor,'cir')] = cur_subdf['mem'].tolist()
      num_solved, total_time, avg_time, mem_total, avg_mem = accumulate(cur_subdf)
      print(qcir_encoding, solver, preprocessor,"  :  ", str(num_solved), round(total_time, 2), avg_time, mem_total, avg_mem)
  print("------------------------------------------")

print("=================================================================")

#================================================================================================================================================
# QDIMACS solvers:
#================================================================================================================================================
#qdimacs_solvers = ["CQ","DQ"]
# we take input preprocessor folder names, we also add empty string for no preprocessing:
#preprocessors = ["B","H","Q"]
#mpreprocessors =["M-N", "M-B", "M-H", "M-Q"]

#encodings = ["bwnib"]
#encodings = ["COR","EA","EN","ET","LN","SN"]

qdimacs_solvers = ["CQ","DQ"]
# we take input preprocessor folder names, we also add empty string for no preprocessing:
preprocessors = ["B","H","Q","N"]
#mpreprocessors =["M-N", "M-B", "M-H", "M-Q"]

#encodings = ["bwnib"]
encodings = ["COR","EA","EN","ET","LN","SN","LT"]

# checking qdimacs encodings:
for expb_encoding in encodings:
  for solver in qdimacs_solvers:
    for preprocessor in preprocessors:
      cur_subdf = df[(df['encoding'] == expb_encoding) & (df['solver'] == solver) & (df['preprocessor'] == preprocessor) & (df['format'] == 'qdim')]
      #print(expb_encoding,solver,preprocessor)
      #print(cur_subdf['time'].tolist())
      #print(cur_subdf['mem'].tolist())
      time_dict[(expb_encoding,solver, "ALL" ,preprocessor,'qdim')] = cur_subdf['time'].tolist()
      mem_dict[(expb_encoding,solver,"ALL", preprocessor,'qdim')] = cur_subdf['mem'].tolist()
      num_solved, total_time, avg_time, mem_total, avg_mem = accumulate(cur_subdf)
      print(expb_encoding, solver, preprocessor, "  :  ", str(num_solved)   , round(total_time, 2), avg_time, mem_total, avg_mem)
  print("------------------------------------------")
print("=================================================================")


base_markers = ['v','^','<','+','x','.','o']
base_colors = ["b","g","r","c","m","k","y"]

#base_markers = ['x','+','^','.','<','>']
#base_colors = ["b","g","r","k","m","y"]

labels = []

# encoding combinations with both unsat and sat instances (total 6 variations):
cur_encodings = list(encodings)
cur_encodings = ["LN"]
#cur_encodings = ["EA","EN","ET"]
#cur_encodings = ["LN","SN"]
best_combinations = []
markers = []
colors = []
count = 0
'''
#------------------------------------------
# qdimacs instances:
format_t = "qdim"
#cur_solvers = list(qdimacs_solvers)
cur_solvers = ["DQ"]
#cur_preprocessors = list(preprocessors)
cur_preprocessors = ["B"]
#------------------------------------------
'''
#------------------------------------------
# qcir instances:
format_t = "cir"
cur_solvers = list(qcir_solvers)
cur_preprocessors = ["N"]
#------------------------------------------
#'''

for cur_encoding in cur_encodings:
  for solr in cur_solvers:
    for prep in cur_preprocessors:
      best_combinations.append((cur_encoding,solr,"ALL",prep,format_t))
      labels.append(cur_encoding + "_" + solr + "_" + prep)
      markers.append(base_markers[count])
      colors.append(base_colors[count])
      count = count + 1
#best_combinations = [("COR","CQ","ALL","B","qdim"),("COR","CQ","ALL","H","qdim"), ("COR","CQ","ALL","Q","qdim")]

#print(best_combinations)

#markers = ['x','+','^','.','<','>']
#colors = ["b","g","r","k","m","y"]
markers = ['v','^','<','+','x','.','o']
colors = ["b","g","r","c","m","k","y"]

'''

labels = ["COR_DQ_B","EA_CQ_B", "EN_CQ_Q", "ET_CQ_Q", "LN_CQ_B","SN_CQ_B","ET_CQ_B"]
best_combinations = [('COR', 'CQ', 'ALL', 'B', 'qdim'), ('EA', 'CQ', 'ALL', 'B', 'qdim'), ('EN', 'CQ', 'ALL', 'B', 'qdim'),
                     ('ET', 'CQ', 'ALL', 'B', 'qdim'), ('LN', 'CQ', 'ALL', 'B', 'qdim'), ('SN', 'CQ', 'ALL', 'B', 'qdim'),('LT', 'CQ', 'ALL', 'B', 'qdim')]
'''

#=======================================================================================
# time plot:
#=======================================================================================
#'''
for index in range(len(best_combinations)):
  b_comb = best_combinations[index]
  time_lst, count_lst =  cactus_data(time_dict[(b_comb)], int_timeout)
  print(best_combinations[index])
  print(time_lst)
  print(count_lst)
  plt.scatter(count_lst, time_lst, label = labels[index],marker = markers[index], color=colors[index])

plt.grid()
plt.xlabel("Cumulative instances solved")
plt.ylabel("time taken in sec (log scale)")
plt.yscale('log')
plt.legend()
plt.show()
#'''
#=======================================================================================

'''
cor_base_CQ_Q = [0.87,57.45,719,0.01,0.01,10.2,15.5,0.3,4.31,4.13,104,0.01,0.11,367,4906,5.17,240,0.02,0.11,0.24,15.6,0.38,19,3247,26938,651,8964,2.29,44.4]
cor_CQ_Q = [1,31,330,0.1,0.1,3,12,0.1,3,5,71,0.1,0.1,103,2229,6,58,0.1,0.1,0.1,12,1,19,795,3294,164,3350,2,24]

plt.scatter(cor_base_CQ_Q, cor_CQ_Q)

plt.grid()
plt.xlabel("base")
plt.ylabel("grendel run")
plt.xscale('log')
plt.yscale('log')
#plt.legend()
plt.show()
'''


#=======================================================================================
# mem plot:
#=======================================================================================
'''
for index in range(len(best_combinations)):
  b_comb = best_combinations[index]
  print(best_combinations[index])
  #if ("EB" not in b_comb[0]):
  #  continue
  mem_lst, count_lst =  cactus_data(mem_dict[(b_comb)], mem_timeout)
  #print(mem_lst, count_lst,b_comb)
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
'''
#=======================================================================================
