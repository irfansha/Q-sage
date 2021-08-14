# Irfansha Shaik, 14.08.2021, Aarhus.

from run.run_quabs import RunQuabs as rq
from run.run_caqe import RunCaqe as rc
from run.run_rareqs import RunRareqs as rr

def run_single_solver(encoding):
  # For ease of access declaring locally:
  args = encoding.parsed.args
  if (args.solver == 1):
    instance = rq(args)
    sol_map = instance.sol_map
  elif (args.solver == 2):
    instance = rc(args)
    sol_map = instance.sol_map
  elif (args.solver == 3):
    instance = rr(args)
    sol_map = instance.sol_map

  # Checking existence of plan:
  if instance.sat == 1:
    print("Plan found")
  elif instance.sat == -1:
    print("====> ERROR from solver <====")
    return
  else:
    print("Plan not found")
    return
