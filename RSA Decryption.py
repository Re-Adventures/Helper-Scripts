# Boilerplate code for RSA
N = 
e = 0x10001
C = 
p = 
q = 

assert N == p * q

phi = (p-1) * (q-1)
d = pow(e, -1, phi)

M = bytes.fromhex(hex(pow(C, d, N))[2:])
print(M)
