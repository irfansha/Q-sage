# Irfansha Shaik, 04.07.2022, Aarhus

f = open("intermediate_files/games_list.txt", 'r')


games_list = []

lines = f.readlines()
# Looping through all the player games:
for line in lines:
  if (line != '\n'):
    #line = line.strip("\n")
    games_list.append(line)
f.close()

all_games_file = open("intermediate_files/parsed_games.txt", 'w')

# Looping through player ids and gathering the games:

count_games = 0
resigned_games = 0

total_games_count = 0
total_resigned_games = 0

max_resigned_game_length = 0
max_completed_game_length = 0

game_id_list = []
for single_game in games_list:
  #print(single_game)
  new_line = single_game.strip("\n").strip(" ").strip('\r')
  #print(new_line)
  # considering all games, so all games are valid:
  valid_game = 1
  if valid_game == 1:
    #print(new_line)
    # we split the new_line to gather game id and game moves:
    split_new_line = new_line.split("[ game #")
    #print(split_new_line)
    second_split = split_new_line[1].split("]SO[https://www.littlegolem.net]")
    game_id = second_split[0]
    if (game_id in game_id_list):
      #print("Already looked at!")
      continue
    else:
      game_id_list.append(game_id)
    game_moves = second_split[1].strip(";").strip(")").split(";")
    #print(len(game_moves))
    #'''
    # we do not need empty games:
    if (game_moves != [')']):
      swap_string = 'no_swap'
      # Handle swap first:
      if ('B[swap]' in game_moves):
        first_w_move = game_moves.pop(0)
        # removing the swap move:
        swap_move = game_moves.pop(0)
        assert(swap_move == 'B[swap]')
        # now reverse the idexes in the white move:
        new_w_move = 'B[' + first_w_move[3] + first_w_move[2] + ']'
        game_moves.insert(0,new_w_move)
        swap_string = 'swapped'
      elif ('W[swap]' in game_moves):
        first_b_move = game_moves.pop(0)
        # removing the swap move:
        swap_move = game_moves.pop(0)
        assert(swap_move == 'W[swap]')
        # now reverse the idexes in the white move:
        new_b_move = 'W[' + first_b_move[3] + first_b_move[2] + ']'
        game_moves.insert(0,new_b_move)
        swap_string = 'swapped'
      count_games = count_games + 1
      # IF either of the player resinged:
      # If first player resigned:
      if ('B' in game_moves[0] and 'B[resign]' in game_moves) or ('W' in game_moves[0] and 'W[resign]' in game_moves) :
        resigned_games = resigned_games + 1
        all_games_file.write(str(game_id)  + " " + swap_string + " first resigned " + str(len(game_moves)) + " " + ' '.join(game_moves) + "\n")
        #print("Game resigned:", game_id, "game length", len(game_moves))
        if (len(game_moves) > max_resigned_game_length ):
          max_resigned_game_length = len(game_moves)
      elif ('W[resign]' in game_moves) or ('B[resign]' in game_moves) :
        # the rest of the resigned games are second player resigned:
        resigned_games = resigned_games + 1
        all_games_file.write(str(game_id)  + " " + swap_string + " second resigned " + str(len(game_moves)) + " " + ' '.join(game_moves) + "\n")
        #print("Game resigned:", game_id, "game length", len(game_moves))
        if (len(game_moves) > max_resigned_game_length ):
          max_resigned_game_length = len(game_moves)
      elif ("W" in game_moves[0] and "W" in game_moves[-1]) or ("B" in game_moves[0] and "B" in game_moves[-1]):
        # first player won games:
        all_games_file.write(str(game_id)  + " " + swap_string + " first finish " + str(len(game_moves)) + " " + ' '.join(game_moves) + "\n")
        #print("Game complete:", game_id, "game length", len(game_moves))
        if (len(game_moves) > max_completed_game_length ):
          max_completed_game_length = len(game_moves)
      else:
        # remaining games must be second player won games:
        all_games_file.write(str(game_id)  + " " + swap_string + " second finish " + str(len(game_moves)) + " " + ' '.join(game_moves) + "\n")
        #print("Game complete:", game_id, "game length", len(game_moves))
        if (len(game_moves) > max_completed_game_length ):
          max_completed_game_length = len(game_moves)

      #print(game_id, len(game_moves), game_moves)
    #'''


print("Total games: ", count_games)
print("Total Resigned games: ", resigned_games , "max game length", max_resigned_game_length)
print( "Total Non-resigned games: " , count_games - resigned_games, "max game length", max_completed_game_length)

all_games_file.close()

























