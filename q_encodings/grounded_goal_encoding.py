# Irfansha Shaik, 14.08.2021, Aarhus.

from utils.variables_dispatcher import VarDispatcher as vd
from utils.gates import GatesGen as ggen
import math
import utils.lessthen_cir as lsc



class GroundedGoalEncoding:

  def print_gate_tofile(self, gate, f):
    if len(gate) == 1:
      f.write(gate[0] + '\n')
    else:
      f.write(str(gate[1]) + ' = ' + gate[0] + '(' + ', '.join(str(x) for x in gate[2]) + ')\n')

  def print_encoding_tofile(self, file_path):
    f = open(file_path, 'w')
    for gate in self.quantifier_block:
      self.print_gate_tofile(gate, f)
    f.write('output(' + str(self.final_output_gate) + ')\n')
    for gate in self.encoding:
      self.print_gate_tofile(gate, f)

  # Generates quanifier blocks:
  def generate_quantifier_blocks(self):
    # Action and parameter variables are first existential layer:
    self.encoding.append(["# ------------------------------------------------------------------------"])
    self.encoding.append(['# Quantifier alternations: '])


  def generate_k_transitions(self):
    self.encoding.append(["# ------------------------------------------------------------------------"])
    self.encoding.append(['# Transitions: '])


  # TODO: Testing is needed
  def generate_initial_gate(self):
    initial_step_output_gates = []

    self.encoding.append(["# ------------------------------------------------------------------------"])
    self.encoding.append(['# Initial state: '])


  # Generating goal constraints:
  def generate_goal_gate(self):
    goal_step_output_gates = []
    self.encoding.append(["# ------------------------------------------------------------------------"])
    self.encoding.append(['# Goal state: '])


  def generate_simple_restricted_forall_constraints(self):

    self.encoding.append(["# ------------------------------------------------------------------------"])
    self.encoding.append(['# Conditional forall constraints: '])



  # Final output gate is an and-gate with inital, goal and transition gates:
  def generate_final_gate(self):
    self.encoding.append(["# ------------------------------------------------------------------------"])
    self.encoding.append(['# Final gate: '])

  def __init__(self, parsed):
    self.parsed = parsed
    self.encoding_variables = vd()
    self.quantifier_block = []
    self.encoding = []
    self.initial_output_gate = 0 # initial output gate can never be 0
    self.goal_output_gate = 0 # goal output gate can never be 0
    self.transition_step_output_gates = []
    self.conditional_final_output_gate = 0 # Can never be 0
    self.final_output_gate = 0 # Can never be 0



    # Generating quantifer blocks:
    self.generate_quantifier_blocks()
    # Generating k steps i.e., plan length number of transitions:
    self.generate_k_transitions()

    self.gates_generator = ggen(self.encoding_variables, self.encoding)

    self.generate_initial_gate()

    self.generate_goal_gate()

    self.generate_final_gate()
