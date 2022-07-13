# Irfansha Shaik, 10.09.2021, Aarhus

# Takes a board size and generates
#  - positions of the board (with some naming)
#  - specifies the neighbours of each cell in hex board
#  - specifies the black boarders (starting and ending)

import argparse
import string


# Keeping consistent with previous benchmarks naming of the board:
def print_positions(size):
  positions = []
  for i in range(1, size + 1):
    for j in range(1, size + 1):
      positions.append(string.ascii_lowercase[i-1] + str(j))
  print("#positions")
  print(' '.join(positions))


# The neighbours for (i,j) are (i-1, j), (i+1, j), (i, j-1), (i, j+1), (i-1, j+1), (i+1, j-1):
def generate_neighbours(size):
  print("#neighbours")
  print("%format: [position] [up] [right-side]")
  for i in range(1, size + 1):
    for j in range(1, size + 1):
      cur_position = string.ascii_lowercase[i-1] + str(j)
      # generating neighbours now:
      cur_neighbours = []
      # boundaries to be handled:
      # For (i, j+1):
      if ((j+1) <= size):
        cur_neighbours.append(string.ascii_lowercase[(i)-1] + str(j+1))
      else:
        cur_neighbours.append('na')
      # For (i+1, j):
      if ((i+1) <= size):
        cur_neighbours.append(string.ascii_lowercase[(i+1)-1] + str(j))
      else:
        cur_neighbours.append('na')
      print(cur_position, ' '.join(cur_neighbours))


# Main:
if __name__ == '__main__':
  text = "Takes a board size and generates positions of the board (with some naming), specifies the neighbours of each cell in ttt board"
  parser = argparse.ArgumentParser(description=text,formatter_class=argparse.RawTextHelpFormatter)
  parser.add_argument("--size", help="board size, default 3", type=int,default = 3)
  args = parser.parse_args()

  print("#blackinitials")
  print("#whiteinitials")
  print("#times\nt1")
  print("#blackturns\nt1")
  print_positions(args.size)
  generate_neighbours(args.size)
  print("#blackgoal")
