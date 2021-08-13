# Irfansha Shaik, 13.08.2021, Aarhus

import os

class Parse:

  # Parses domain and problem file:
  def __init__(self, args):
    problem_path = args.problem
    f = open(problem_path, 'r')
    lines = f.readlines()

    parsed_dict = {}

    for line in lines:
      stripped_line = line.strip("\n").strip(" ").split(" ")
      # we ignore if it is a comment:
      if ('%' == line[0]):
        continue
      if ("#" in line):
        new_key = line.strip("\n")
        parsed_dict[new_key] = []
      else:
        parsed_dict[new_key].append(stripped_line)
    
    print(parsed_dict)
    
