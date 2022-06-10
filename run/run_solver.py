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

    if (encoding.parsed.args.game_type == 'gomuku'):
      x_index_string = ''
      # computing x index value:
      for i in range(encoding.num_single_index_move_variables):
        x_index_string += str(sol_map[encoding.move_variables[0][i]])
      x_index = int(x_index_string, 2)
      y_index_string = ''
      # computing y index value:
      for i in range(encoding.num_single_index_move_variables, len(encoding.move_variables[0])):
        y_index_string += str(sol_map[encoding.move_variables[0][i]])
      y_index = int(y_index_string, 2)
      # x_index is mapped to character starting from 'a' and
      # y index is increased by 1 to match the indexes:
      winning_move = chr(ord('a')+x_index) + str(y_index + 1)
      print("First winning move:",winning_move)

    elif (encoding.parsed.args.game_type == 'general'):
      action_string = ''
      for i in range(encoding.num_black_action_variables):
        action_string += str(sol_map[encoding.move_variables[0][0][i]])
      action_index = int(action_string, 2)
      winning_action = encoding.parsed.black_action_list[action_index].action_name
      x_index_string = ''
      # computing x index value:
      for i in range(encoding.num_x_index_variables):
        # looking at the 0 time step, x variables:
        x_index_string += str(sol_map[encoding.move_variables[0][1][i]])
      x_index = int(x_index_string, 2)
      y_index_string = ''
      # computing y index value:
      for i in range(encoding.num_y_index_variables):
        # looking at the 0 time step, and y variables:
        y_index_string += str(sol_map[encoding.move_variables[0][2][i]])
      y_index = int(y_index_string, 2)
      # x_index is mapped to character starting from 'a' and
      # y index is increased by 1 to match the indexes:
      winning_move = chr(ord('a')+x_index) + str(y_index + 1)
      print("First winning move: " + str(winning_action) + "(" + str(winning_move) + ")")

    else:
      # if already solved, just print any open position:
      if encoding.parsed.solved == 1:
        print("The problem already solved")
        print(encoding.parsed.black_initial_positions, encoding.parsed.white_initial_positions)
        for i in range(len(encoding.parsed.rearranged_positions)):
          if (i not in encoding.parsed.black_initial_positions and i not in encoding.parsed.white_initial_positions):
            print("First winning move:", encoding.parsed.rearranged_positions[i])
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
