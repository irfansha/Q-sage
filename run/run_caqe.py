# Irfansha Shaik, 14.08.2021, Aarhus.

import subprocess
import os

class RunCaqe():

  def run_caqe(self):
    if (self.preprocessing == 2):
      command = self.solver_path + " --preprocessor=bloqqer --qdo " + self.input_file_path + " > " + self.output_file_path
    elif(self.preprocessing == 3):
      command = self.solver_path + " --preprocessor=hqspre --qdo " + self.input_file_path + " > " + self.output_file_path
    else:
      command = self.solver_path + " --qdo " + self.input_file_path + " > " + self.output_file_path
    try:
      subprocess.run([command], shell = True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT ,check=True, timeout=self.time_limit)
    except subprocess.TimeoutExpired:
      self.timed_out = True
      print("Time out after " + str(self.time_limit)+ " seconds.")
    except subprocess.CalledProcessError as e:
      # 10, 20 are statuses for SAT and UNSAT:
      if ("exit status 10" not in str(e) and "exit status 20"  not in str(e)):
        print("Error from solver :", e, e.output)

  # parsing the caqe solver output:
  def parse_caqe_output(self):
    f = open(self.output_file_path, 'r')
    lines = f.readlines()
    # Printing the data to the output for correctness purposes:
    for line in lines:
      #if (line != '\n' and 'V' not in line):
      if (line != '\n'):
        nline = line.strip("\n")
        print(nline)

    # Making sure the state of solution is explicitly specified:
    for line in lines:
      if ('c Unsatisfiable' in line):
        self.sat = 0
        return

    for line in lines:
      if ('c Satisfiable' in line):
        self.sat = 1
        break

    for line in lines:
      if ('V' in line):
        temp = line.split(" ")
        if (temp != ['\n']):
          literal = temp[1]
          if int(literal) > 0:
            self.sol_map[int(literal)] = 1
          else:
            self.sol_map[-int(literal)] = 0

  def __init__(self, args):
    self.input_file_path = args.encoding_out
    self.output_file_path = args.solver_out
    self.time_limit = args.time_limit
    self.preprocessing = args.preprocessing
    # By default timeout not occured yet:
    self.timed_out = False
    self.solver_path = os.path.join(args.planner_path, 'solvers', 'caqe', 'caqe')
    self.sol_map = {}
    self.sat = -1 # by default plan not found.

    self.run_caqe()
    self.parse_caqe_output()
