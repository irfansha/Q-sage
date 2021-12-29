# Irfansha Shaik, 29.12.2021, Aarhus

def add_circuit(gg, vars, num):
    num_variables = len(vars)
    # Representation in binary requires number of variables:
    rep_string = '0' + str(num_variables) + 'b'
    bin_string = format(num, rep_string)

    # First generating all carry gates:
    carry_output_gates = [0]*num_variables # gates cannot be 0, we can add an assertion at the end

    # in qcir-14, the empty or gate is equal to 0 and we use this for a 0 gate:
    # empty circuit for the last carry bit:
    gg.or_gate([])
    carry_output_gates[num_variables-1] = gg.output_gate

    for i in range(1,num_variables):
      # First carry is updated:
      index = num_variables - i - 1
      #print(index, index +1)
      if (bin_string[index + 1] == '0'):
        # The carry bit is equal to the conjunction of previous X bit and previous carry bit:
        gg.and_gate([carry_output_gates[index + 1], vars[index + 1]])
        carry_output_gates[index] = gg.output_gate
      else:
        # The carry bit is equal to the disjunction of previous X bit and previous carry bit:
        gg.or_gate([carry_output_gates[index + 1], vars[index + 1]])
        carry_output_gates[index] = gg.output_gate

    sum_output_gates = [0]*num_variables # gates cannot be 0, we can add an assertion at the end

    for i in range(num_variables):
      # Sum is updated:
      index = num_variables - i - 1
      gg.single_equality_gate(carry_output_gates[index], vars[index])
      #print(index, index +1)
      if (bin_string[index] == '0'):
        # The sum bit is the negation of equality gate of current carry bit and current X bit:
        sum_output_gates[index] = -gg.output_gate
      else:
        # The sum bit is the equality gate of current carry bit and current X bit:
        sum_output_gates[index] = gg.output_gate



    return sum_output_gates