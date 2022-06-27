import glob
import re
import os

def atoi(text):
  return int(text) if text.isdigit() else text

def natural_keys(text):
  return [ atoi(c) for c in re.split(r'(\d+)', text) ]

# read the file and join the outermost existensial layer:
def rewrite(f_path):

  cur_command = "cp qbf_eval_file " + f_path

  os.system(cur_command)

  '''
  
  f_init = open("qbf_eval_file", 'r')
  lines = f_init.readlines()
  f_init.close()

  matrix = []

  # printing to the new file with modified lines:
  f = open(f_path,'w')
  while(lines):
    cur_line = lines.pop(0)
    if (cur_line[0] != 'p' and cur_line[0] != 'e' and cur_line[0] != 'a'):
      lines.insert(0,cur_line)
      break
    else:
      matrix.append(cur_line)
  for i in range(len(matrix)-2):
    f.write(matrix[i])
  # combining the last two matrix lines:
  assert(matrix[-2][-2:] == '0\n')
  assert(matrix[-1][:2] == 'e ')
  
  final_line = matrix[-2][:-2] + matrix[-1][2:]

  f.write(final_line)

  for line in lines:
    f.write(line)
  '''
# Easy
#====================================================================================================================================================================================================================================
#'''

cur_encoding = 'cgcp'

cur_dir = "Easy"

#os.mkdir("Hex_qcir")
#os.mkdir("Hex_qcir/" + cur_encoding)
os.mkdir("Hex_qcir/" + cur_encoding + "/"+ cur_dir)



files_list = glob.glob("Benchmarks/temp_unground_bench/" + cur_dir + "/*")
files_list.sort(key=natural_keys)

print(files_list)

for file_name in files_list:
  command = "python3 Q-sage.py -e " + cur_encoding + " --problem " + file_name + " --run 0 --encoding_format 1 --encoding_out qbf_eval_file"
  os.system(command)

  only_file_name = file_name.split("/")[-1]
  
  rewrite("Hex_qcir/" + cur_encoding + "/" + cur_dir + "/" + only_file_name + ".qcir")
#'''

#====================================================================================================================================================================================================================================
