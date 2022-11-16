# Irfansha Shaik, 16.11.2022, Aarhus

import argparse


# Main:
if __name__ == '__main__':
  text = "Takes a hex board"
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

  #for key,value in parsed_dict.items():
  #  print(key, value)

#=====================================================================================================================================
# printing input files:


print("#boardsize")
print(str(int(len(parsed_dict['#positions'][0]))) + " 1")
#print(str(int(math.sqrt(len(parsed_dict['#positions'][0])))) + " " + str(int(math.sqrt(len(parsed_dict['#positions'][0])))))
print("#blackinitials")
for var in parsed_dict['#blackinitials']:
  print(var[0])
print("#whiteinitials")
for var in parsed_dict['#whiteinitials']:
  print(var[0])
print("#depth")
print(len(parsed_dict['#times'][0]))
#print("#blackactions\n%action 1\n:action occupy\n:parameters (?x, ?y)\n:indexbounds (ge(?x, xmin) le(?x,xmax) ge(?y,ymin) le(?y,ymax))\n:precondition (open(?x,?y))\n:effect (black(?x,?y))\n#whiteactions\n%action 1\n:action occupy\n:parameters (?x, ?y)\n:indexbounds (ge(?x, xmin) le(?x,xmax) ge(?y,ymin) le(?y,ymax))\n:precondition (open(?x,?y))\n:effect (white(?x,?y))\n#blackgoal")
print("#blackgoal")
for win in parsed_dict['#blackwins']:
  cur_string = ''
  for pos in win:
    ind = parsed_dict['#positions'][0].index(pos)
    cur_string += 'black('+ str(ind+1) + ",1) "
  print(cur_string)
print("#whitegoal")
#for win in parsed_dict['#whitewins']:
#  cur_string = ''
#  for pos in win:
#    x = ord(pos[0])-96
#    y = int(pos[1:])
#    cur_string += 'white('+ str(x) + "," + str(y) + ") "
#  print(cur_string) #=====================================================================================================================================
