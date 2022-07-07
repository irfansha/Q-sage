# Irfansha Shaik, 07.07.2022, Aarhus
# reusing the existing code from other scripts folder

import argparse

# Main:
if __name__ == '__main__':
  text = "Takes unrolling depth and generators B-Hex input in intermediate_files/B-Hex folder"
  parser = argparse.ArgumentParser(description=text,formatter_class=argparse.RawTextHelpFormatter)
  parser.add_argument("--unrolling_depth", help="number of move to unroll the game, default 1", type=int, default = 1)
  args = parser.parse_args()

  unrolling_depth = args.unrolling_depth

  # Open the games list:
  f = open('intermediate_files/parsed_games.txt','r')
  lines = f.readlines()
  f.close()

  # First player winning file:
  f_first_player = open('19_board_neighbours/19_neighbours_first_player.txt','r')
  first_player_lines = f_first_player.readlines()
  f_first_player.close()

  # Second player winning file:
  f_second_player = open('19_board_neighbours/19_neighbours_second_player.txt','r')
  second_player_lines = f_second_player.readlines()
  f_second_player.close()


  for line in lines:
    split_line = line.strip("\n").split(" ")
    #print(split_line)
    # Getting the metadata:
    game_id = split_line.pop(0)
    swap_flag = split_line.pop(0)
    # remembering first player or second player:
    player_type = split_line.pop(0)
    # remembering whether the player finished or resigned:
    player_action = split_line.pop(0)
    # Length of game:
    game_length = int(split_line.pop(0))
    # popping the resigned position:
    if (player_action == 'resigned'):
      split_line.pop(-1)
      game_length = game_length - 1
    first_player_moves = []
    second_player_moves = []
    # asserting every consecutive games are different:
    for i in range(len(split_line)-1):
      assert(split_line[i][0] != split_line[i+1][0])
  
    # Separating first and second player moves, while converting the moves to the board indicies:
    for i in range(len(split_line)):
      assert('resign' not in split_line[i])
      cur_move = split_line[i]
      cur_move_first_index = cur_move[2]
      cur_move_second_index = cur_move[3]
      cur_move_second_int_index = ord(cur_move_second_index)-ord('a') + 1
      # We convert the second index into integer:
      if (i % 2 == 0):
        first_player_moves.append(cur_move_first_index + str(cur_move_second_int_index))
      else:
        second_player_moves.append(cur_move_first_index + str(cur_move_second_int_index))


    #print(first_player_moves)

    #print(second_player_moves)

    # Printing the player moves, with unrolling:
    # number of first player moves to unroll:
    num_black_moves_unrolled = int((unrolling_depth + 1)/2)
    # number of second player moves to unroll:
    num_white_moves_unrolled = num_black_moves_unrolled - 1
    # no need to assert for resigned players:
    #assert(num_black_moves_unrolled + num_white_moves_unrolled == unrolling_depth)



    # Opening a new file:
    # specifying which move we take a snapshot, with swap we get one more move in the original game:
    if (swap_flag == 'swapped'):
      f = open("intermediate_files/B-Hex/" + str(game_id) + "_move_" + str(int(game_length) - unrolling_depth + 1) + '.pg', 'w')
    else:
      f = open("intermediate_files/B-Hex/" + str(game_id) + "_move_" + str(int(game_length) - unrolling_depth) + '.pg', 'w')  


    # if first player resigned or second player finished, we check if second player is winning:
    # else we check if the first player is winning
    # black player is always the winning player:
    if ((player_type == "first" and player_action == "resigned") or (player_type == "second" and player_action == "finish")):
      cur_black_moves = list(second_player_moves)
      cur_white_moves = list(first_player_moves)
    else:
      cur_black_moves = list(first_player_moves)
      cur_white_moves = list(second_player_moves)

    f.write("#blackinitials\n")
    for i in range(len(cur_black_moves)):
      if (i < len(cur_black_moves) - num_black_moves_unrolled):
        f.write(str(cur_black_moves[i]) + "\n")
      else:
        f.write("%" + str(cur_black_moves[i]) + "\n")

    #print("-------------------------------------------")
    f.write("#whiteinitials\n")
    for i in range(len(cur_white_moves)):
      if (i < len(cur_white_moves) - num_white_moves_unrolled):
        f.write(str(cur_white_moves[i]) + "\n")
      else:
        f.write("%" + str(cur_white_moves[i]) + "\n")
    #print("-------------------------------------------")

    # times to be appended:
    times_string = ''
    black_times_string = ''
    for i in range(unrolling_depth):
      times_string = times_string + 't' + str(i+1) + " "
      if (i % 2 == 0):
        black_times_string = black_times_string + 't' + str(i+1) + " "

    times_string = times_string.strip(" ")
    black_times_string = black_times_string.strip(" ")


    f.write("#times\n")
    f.write(times_string + '\n')
    f.write("#blackturns\n")
    f.write(black_times_string + '\n')


    # This is for second player won games:
    # Appending the neighbor relation from files:
    #print(swap_flag)
    if (swap_flag == "no_swap"):
      if ((player_type == "first" and player_action == "resigned") or (player_type == "second" and player_action == "finish")):
        for line in second_player_lines:
          f.write(line)
      else:
        for line in first_player_lines:
          f.write(line)
    else:
      if ((player_type == "first" and player_action == "resigned") or (player_type == "second" and player_action == "finish")):
        for line in first_player_lines:
          f.write(line)
      else:
        for line in second_player_lines:
          f.write(line)


    f.close()
