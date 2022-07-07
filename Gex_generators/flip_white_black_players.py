# Irfansha Shaik, 30.06.2022, Aarhus

import argparse

# Main:
if __name__ == '__main__':
  text = "Takes a B-Gex input and generate Flipped B-Gex file"
  parser = argparse.ArgumentParser(description=text,formatter_class=argparse.RawTextHelpFormatter)
  parser.add_argument("--problem", help="problem file path")
  args = parser.parse_args()

    #=====================================================================================================================================
  # parsing:

  problem_path = args.problem
  f = open(problem_path, 'r')
  lines = f.readlines()

  parsed_dict = {}

  for line in lines:
    stripped_line = line.strip("\n").strip(" ").split(" ")
    # we ignore if it is a comment:
    if ('%' == line[0] or line == '\n'):
      continue
    if ("#" in line):
      new_key = line.strip("\n")
      parsed_dict[new_key] = []
    else:
      parsed_dict[new_key].append(stripped_line)

  #=====================================================================================================================================

  #=====================================================================================================================================
  # printing input files:
  # flipping the positions:
  print("#blackinitials")
  for pos in parsed_dict['#whiteinitials']:
    print(pos[0])
  print("#whiteinitials")
  for pos in parsed_dict['#blackinitials']:
    print(pos[0])
  print("#times")
  print(' '.join(parsed_dict["#times"][0]))
  print("#blackturns")
  print(' '.join(parsed_dict["#blackturns"][0]))
  print('#positions')
  print(' '.join(parsed_dict['#positions'][0]))
  print("#neighbours")
  for neighbour_list in parsed_dict['#neighbours']:
    print(' '.join(neighbour_list))
  # board size must be same as the length of the start boarder in B-Gex format:
  board_size = len(parsed_dict['#startboarder'][0])
  input_start_boarder_string = ' '.join(parsed_dict['#startboarder'][0])
  # using the standard boarder positions for the white player:
  print("#startboarder")
  first_player_start_list = []
  for i in range(board_size):
    first_player_start_list.append('a' + str(i+1))
  first_player_start_boarder_string = ' '.join(first_player_start_list)

  second_player_start_list = []
  for i in range(board_size):
    second_player_start_list.append(chr(ord('a') + i) + '1')
  second_player_start_boarder_string = ' '.join(second_player_start_list)

  # now we allow both player inputs, so we handle two cases when flipping:
  if (input_start_boarder_string == first_player_start_boarder_string):
    print(second_player_start_boarder_string)
  else:
    print(first_player_start_boarder_string)

  print("#endboarder")
  input_end_boarder_string = ' '.join(parsed_dict['#endboarder'][0])
  first_player_end_list = []
  for i in range(board_size):
    first_player_end_list.append('s' + str(i+1))
  first_player_end_boarder_string = ' '.join(first_player_end_list)

  second_player_end_list = []
  for i in range(board_size):
    second_player_end_list.append(chr(ord('a') + i) + str(board_size))
  second_player_end_boarder_string = ' '.join(second_player_end_list)

  # now we allow both player inputs, so we handle two cases when flipping:
  if (input_end_boarder_string == first_player_end_boarder_string):
    print(second_player_end_boarder_string)
  else:
    print(first_player_end_boarder_string)

  #=====================================================================================================================================
