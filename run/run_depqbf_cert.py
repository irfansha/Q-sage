# Irfansha Shaik, 23.09.2022, Aarhus.

import os
import subprocess


class RunDepqbfCert():

  def run_depqbf_cert(self):
    if (self.cert_gen == 0):
      command = self.solver_path + " --qdo " + self.input_file_path + " > " + self.output_file_path
    else:
      # first generating the qrp trace:
      command = self.solver_path + " --trace " + self.input_file_path + " > intermediate_files/depqbf_qrp_trace.qrp"
    try:
      subprocess.run([command], shell = True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT ,check=True, timeout=self.time_limit)
    except subprocess.TimeoutExpired:
      self.timed_out = True
      print("Time out after " + str(self.time_limit)+ " seconds.")
    except subprocess.CalledProcessError as e:
      # 10, 20 are statuses for SAT and UNSAT:
      if ("exit status 10" not in str(e) and "exit status 20"  not in str(e)):
        print("Error from solver :", e, e.output)
      else:
        if ("exit status 10" in str(e)):
          cur_string = self.output_sat_string
        else:
          cur_string = self.output_unsat_string

    if (self.cert_gen == 1):
      #cert_generation_command = self.cert_gen_path + " " + cur_string + " --aiger-ascii --simplify intermediate_files/depqbf_qrp_trace.qrp > " + self.cert_path
      cert_generation_command = self.cert_gen_path + " --aiger-ascii --simplify intermediate_files/depqbf_qrp_trace.qrp > " + self.cert_path
      print(cert_generation_command)
      # this must be very light process no need of time limit:
      os.system(cert_generation_command)

  # parsing the depqbf solver output:
  def parse_depqbf_output(self):
    f = open(self.output_file_path, 'r')
    lines = f.readlines()
    # Printing the data to the output for correctness purposes:
    for line in lines:
      #if (line != '\n' and 'V' not in line):
      if (line != '\n'):
        nline = line.strip("\n")
        #print(nline)

    header = lines[0]

    header_split = header.split(" ")

    #print(header_split)

    if (header_split[2] == '1'):
      self.sat = 1
    else:
      self.sat = 0

    for line in lines:
      if ('V' in line):
        temp = line.split(" ")
        if (temp != ['\n']):
          literal = temp[1]
          if int(literal) > 0:
            self.sol_map[int(literal)] = 1
          else:
            self.sol_map[-int(literal)] = 0


  def parse_qrp_output(self):
    f = open("intermediate_files/depqbf_qrp_trace.qrp","r")
    lines = f.readlines()
    f.close()

    if ("r UNSAT" in lines[-1].strip("\n")):
      self.sat = 0
    elif ("r SAT" in lines[-1].strip("\n")):
      self.sat = 1


  def __init__(self, args, encoding):
    self.input_file_path = args.encoding_out
    self.output_file_path = args.solver_out
    self.time_limit = args.time_limit
    # By default timeout not occured yet:
    self.timed_out = False
    self.solver_path = os.path.join(args.planner_path, 'solvers', 'depqbf_cert', 'depqbf')
    self.cert_gen_path = os.path.join(args.planner_path, 'solvers', 'depqbf_cert', 'qrpcert')
    self.sol_map = {}
    self.sat = -1 # by default plan not found.
    # we generate certificate if viz testing is turned on:
    self.cert_gen = args.viz_testing
    self.cert_path = args.certificate_out

    # certificate output gate string:
    self.output_sat_string = encoding.output_sat_index_string
    self.output_unsat_string = encoding.output_unsat_index_string

    self.run_depqbf_cert()
    if (self.cert_gen == 1):
      self.parse_qrp_output()
    else:
      self.parse_depqbf_output()
