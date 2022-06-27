import requests

'''
# For creating the hex (11 board size) players list with ids:
player_with_id_list = []

# looping through 11 pages:
for i in range(1,12):
  page_link = 'https://www.littlegolem.net/jsp/info/player_list.jsp?gtvar=hex_HEX19&filter=&countryid=&page=' + str(i)
  #print(page_link)
  res = requests.get(page_link)
  if res.status_code == 200: # check that the request went through

    lines = str(res.text)
    split_lines = lines.split("\n")
    for line in split_lines:
      new_line = line.strip("\n").strip(" ").strip('\r')
      if new_line != '' and 'plid' in new_line:
        # finding the plyaer id and player name:
        split_new_line = new_line.split('">')
        plid_line = split_new_line[0]
        player_name_line = split_new_line[1]
        
        # the id is after plid, so splitting there:
        plid = plid_line.split("plid=")[-1]

        # the player name is before </a>, so splitting it there:
        player_name = player_name_line.split("</a>")[0]

        player_with_id_list.append((player_name, plid))
        #print( "player id: ", plid)
        #print("player name: ", player_name)

'''

f = open("players_list_19.R", 'r')

player_with_id_list = []

lines = f.readlines()
header = lines.pop(0)
# Looping through all the player games:
for line in lines:
  split_line = line.strip("\n").split(" ")
  #print(split_line)
  player_with_id_list.append(split_line)
f.close()



f_b_resign = open("first_player_resigned_games.txt", 'w')
f_w_resign = open("second_player_resigned_games.txt", 'w')

f_b_won = open("first_player_won_games.txt", 'w')
f_w_won = open("second_player_won_games.txt", 'w')

# Looping through player ids and gathering the games:

total_games_count = 0
total_resigned_games = 0

max_resigned_game_length = 0
max_completed_game_length = 0

game_id_list = []


for line in player_with_id_list:
  plid = line[-1]
  #plid = 13355
  count_games = 0
  resigned_games = 0
  games_list = []
  player_game_list_command = "https://www.littlegolem.net/jsp/info/player_game_list_txt.jsp?plid=" + str(plid) + "&gtid=hex"
  print(player_game_list_command)
  res = requests.get(player_game_list_command)
  if res.status_code == 200: # check that the request went through
    lines = str(res.text)
    split_lines = lines.split("\n")
    for line in split_lines:
      new_line = line.strip("\n").strip(" ").strip('\r')
      # We only look at the board sizes 11, and we only look at the completed games:
      if new_line != '' and "SZ[19]" in new_line and "RE" in new_line:
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
        # we do not need empty games:
        if (game_moves != [')'] and len(game_moves) >= 35):
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
            new_w_move = 'W[' + first_b_move[3] + first_b_move[2] + ']'
            game_moves.insert(0,new_b_move)
            swap_string = 'swapped'
          count_games = count_games + 1
          # IF either of the player resinged:
          # If first player resigned:
          if ('B' in game_moves[0] and 'B[resign]' in game_moves) or ('W' in game_moves[0] and 'W[resign]' in game_moves) :
            resigned_games = resigned_games + 1
            f_b_resign.write(str(game_id)  + " " + swap_string + " " + str(len(game_moves)) + " " + ' '.join(game_moves) + "\n")
            #print("Game resigned:", game_id, "game length", len(game_moves))
            if (len(game_moves) > max_resigned_game_length ):
              max_resigned_game_length = len(game_moves)
          elif ('W[resign]' in game_moves) or ('B[resign]' in game_moves) :
            # the rest of the resigned games are second player resigned:
            resigned_games = resigned_games + 1
            f_w_resign.write(str(game_id) + " " + swap_string + " " + str(len(game_moves)) + " " + ' '.join(game_moves) + "\n")
            #print("Game resigned:", game_id, "game length", len(game_moves))
            if (len(game_moves) > max_resigned_game_length ):
              max_resigned_game_length = len(game_moves)
          elif ("W" in game_moves[0] and "W" in game_moves[-1]) or ("B" in game_moves[0] and "B" in game_moves[-1]):
            # first player won games:
            f_b_won.write(str(game_id)  + " " + swap_string + " " + str(len(game_moves)) + " " + ' '.join(game_moves) + "\n")
            #print("Game complete:", game_id, "game length", len(game_moves))
            if (len(game_moves) > max_completed_game_length ):
              max_completed_game_length = len(game_moves)
          else:
            # remaining games must be second player won games:
            f_w_won.write(str(game_id) + " " + swap_string + " " + str(len(game_moves)) + " " + ' '.join(game_moves) + "\n")
            #print("Game complete:", game_id, "game length", len(game_moves))
            if (len(game_moves) > max_completed_game_length ):
              max_completed_game_length = len(game_moves)

          #print(game_id, len(game_moves), game_moves)

  print(count_games, resigned_games)
  total_games_count = total_games_count + count_games
  total_resigned_games = total_resigned_games + resigned_games
  #break
# Perhaps json format printing would be easier:


print("Total games: ", total_games_count)
print("Total Resigned games: ", total_resigned_games , "max game length", max_resigned_game_length)
print( "Total completed games" , total_games_count - total_resigned_games, "max game length", max_completed_game_length)

f_w_resign.close()
f_b_resign.close()

f_b_won.close()
f_w_won.close()


























