# Irfansha Shaik, 23.09.2022, Aarhus.

import os
import subprocess


class RunDepqbf():

  def run_depqbf(self):
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


  # parsing the depqbf solver output:
  def parse_depqbf_output(self):
    f = open(self.output_file_path, 'r')
    lines = f.readlines()

    #print(lines)

    for line in lines:
      if ('UNSAT' in line):
        self.sat = 0
        return

    for line in lines:
      if ('SAT' in line):
        self.sat = 1
        return



  def __init__(self, args):
    self.preprocessing = args.preprocessing
    if(self.preprocessing == 1):
      self.input_file_path = args.preprocessed_encoding_out
    else:
      self.input_file_path = args.encoding_out
    self.output_file_path = args.solver_out
    self.time_limit = args.time_limit

    # By default timeout not occured yet:
    self.timed_out = False
    self.solver_path = os.path.join(args.planner_path, 'solvers', 'depqbf', 'depqbf')
    self.sol_map = {}
    self.sat = -1 # by default plan not found.

    self.run_depqbf()
    self.parse_depqbf_output()
