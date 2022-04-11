# Irfansha Shaik, 14.08.2021, Aarhus.

from run.run_caqe import RunCaqe as rc
from run.run_pedant import RunPedant as rp
from run.run_quabs import RunQuabs as rq
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
  elif (args.solver == 4):
    instance = rp(args)
    # No solution extraction yet:
    #sol_map = instance.sol_map

  # Checking existence of plan:
  if instance.sat == 1 or encoding.parsed.solved == 1:
    print("Plan found")
  elif instance.sat == -1:
    print("====> ERROR from solver <====")
    return
  else:
    print("Plan not found")
    return

  # If plan extraction is enabled:
  if (args.run == 2):

    # if already solved, just print any open position:
    if encoding.parsed.solved == 1:
      print("The problem already solved")
      print(encoding.parsed.black_initial_positions, encoding.parsed.white_initial_positions)
      for i in range(len(encoding.parsed.positions)):
        if (i not in encoding.parsed.black_initial_positions and i not in encoding.parsed.white_initial_positions):
          print("First winning move1:", encoding.parsed.positions[i])
          break
    else:
      move_string = ''
      for val in encoding.move_variables[0]:
        move_string += str(sol_map[val])
        # Action index, powers of two:
      action_index = int(move_string, 2)
      #print("First winning move:", encoding.parsed.positions[action_index])
      # parsing using rearranged positions:
      print("First winning move:", encoding.parsed.rearranged_positions[action_index])
