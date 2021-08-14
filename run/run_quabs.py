# Irfansha Shaik, 14.08.2021, Aarhus.

import subprocess
import os

class RunQuabs():

  def run_quabs(self):
    command = self.solver_path + " --partial-assignment " + self.input_file_path + " > " + self.output_file_path
    try:
      subprocess.run([command], shell = True, timeout=self.time_limit)
    except subprocess.TimeoutExpired:
      self.timed_out = True
      print("Time out after " + str(self.time_limit)+ " seconds.")

  # parsing the quabs solver output:
  def parse_quabs_output(self):
    f = open(self.output_file_path, 'r')
    lines = f.readlines()
    result = lines.pop(0).strip("\n")
    if (result != 'r UNSAT'):
      self.sat = 1
      literals = result.split(" ")
      literals.pop()
      literals.pop(0)
      for literal in literals:
        if int(literal) > 0:
          self.sol_map[int(literal)] = 1
        else:
          self.sol_map[-int(literal)] = 0
    else:
      self.sat = 0

  def __init__(self, args):
    self.input_file_path = args.encoding_out
    self.output_file_path = args.solver_out
    self.time_limit = args.time_limit
    # By default timeout not occured yet:
    self.timed_out = False
    self.solver_path = os.path.join(args.planner_path, 'solvers', 'quabs', 'quabs')
    self.sol_map = {}
    self.sat = -1 # by default plan not found.

    self.run_quabs()
    self.parse_quabs_output()
