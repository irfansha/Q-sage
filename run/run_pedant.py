# Irfansha Shaik, 07.10.2021, Aarhus.

import subprocess
import os

class RunPedant():

  def run_pedant(self):
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

  # parsing the pedant solver output:
  def parse_pedant_output(self):
    f = open(self.output_file_path, 'r')
    lines = f.readlines()
    # Printing the data to the output for correctness purposes:
    for line in lines:
      #if (line != '\n'):
      if (line != '\n'):
        nline = line.strip("\n")
        print(nline)

    # Making sure the state of solution is explicitly specified:
    for line in lines:
      if ('UNSATISFIABLE' in line):
        self.sat = 0
        return

    for line in lines:
      if ('SATISFIABLE' in line):
        self.sat = 1
        break


  def __init__(self, args):
    self.input_file_path = args.encoding_out
    self.output_file_path = args.solver_out
    self.time_limit = args.time_limit
    # By default timeout not occured yet:
    self.timed_out = False
    self.solver_path = os.path.join(args.planner_path, 'solvers', 'pedant-solver', 'pedant')
    self.sol_map = {}
    self.sat = -1 # by default plan not found.

    self.run_pedant()
    self.parse_pedant_output()
