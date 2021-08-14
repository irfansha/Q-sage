# Irfansha Shaik, 14.08.2021, Aarhus

def add_circuit(gg, vars, num):
    num_variables = len(vars)
    # Representation in binary requires number of variables:
    rep_string = '0' + str(num_variables) + 'b'
    bin_string = format(num, rep_string)

    #print(gg.output_gate)

    and_output_gates = []

    for i in range(num_variables):
      # Since we are considering less than,
      # we only need to look at the indexes with 1's in binary string:
      step_clause = []
      if (bin_string[i] == '1'):
        for j in range(i):
          if (bin_string[j] == '1'):
            step_clause.append(vars[j])
          else:
            step_clause.append(-vars[j])
        step_clause.append(-vars[i])
        gg.and_gate(step_clause)
        and_output_gates.append(gg.output_gate)

    # Finally an or gates for all the and gates:
    gg.or_gate(and_output_gates)