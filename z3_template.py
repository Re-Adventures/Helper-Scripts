from z3 import *

# The length of the expected output
output_len = 32 # change this

# A list of Bit Vectors, list of characters
output = [BitVec(f"output_{i}", 8) for i in range(output_len)]

# The solver engine
s = Solver()

# Adding the constraint to make the output ascii printable
for i in range(output_len):
  s.add(output[i] > 31)
  s.add(output[i] < 127)

# Add rules from here like this
# s.add((output[2] + output[16]) == (output[d] + 70))

print(f"{s.check()=}")

# If we found a solution
if sat == s.check():
  soln = s.model() # Retrieving the solution

  o = ""
  # grab each & every character in order & print it
  for i in range(output_len):
    o += chr(soln[output[i]].as_long())

  print(o)
