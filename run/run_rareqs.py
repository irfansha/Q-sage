# Irfansha Shaik, 14.08.2021, Aarhus.

import subprocess
import os

class RunRareqs():

  def run_rareqs(self):
    command = self.solver_path + " " + self.input_file_path + " > " + self.output_file_path
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
  def parse_rareqs_output(self):
    f = open(self.output_file_path, 'r')
    lines = f.readlines()
    # Not needed as of now:
    '''
    # Printing the data to the output for correctness purposes:
    for line in lines:
      if (line != '\n' and 'c' not in line):
        nline = line.strip("\n")
        print(nline)
    '''

    # Making sure the state of solution is explicitly specified:
    for line in lines:
      if ('s cnf 0' in line):
        self.sat = 0
        return

    for line in lines:
      if ('s cnf 1' in line):
        self.sat = 1
        break

    for line in lines:
      if ('V' in line):
        trimmed_line = line.strip("\n")
        temp = trimmed_line.split(" ")
        for var in temp:
          if (var != '' and var != 'V'):
            if int(var) > 0:
              self.sol_map[int(var)] = 1
            else:
              self.sol_map[-int(var)] = 0

  def __init__(self, args):
    if (args.preprocessing == 0):
      self.input_file_path = args.encoding_out
    elif (args.preprocessing == 1):
      self.input_file_path = args.preprocessed_encoding_out
    self.output_file_path = args.solver_out
    self.time_limit = args.time_limit
    # By default timeout not occured yet:
    self.timed_out = False
    self.solver_path = os.path.join(args.planner_path, 'solvers', 'RaReQS', 'rareqs-1.1')
    self.sol_map = {}
    self.sat = -1 # by default plan not found.

    self.run_rareqs()
    self.parse_rareqs_output()
