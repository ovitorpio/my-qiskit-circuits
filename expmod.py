from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit.library import QFT
from ctrl_mult_mod import ctrl_mult_mod
from math import log2

def expmod(N, base, bits_expoente):
    n_bits = int(log2(N))+1

    reg_x = QuantumRegister(bits_expoente, "x")

    reg_b = QuantumRegister(n_bits, "b")

    reg_c_aux = QuantumRegister(1, "c_aux")

    reg_0 = QuantumRegister(n_bits, "0")

    reg_cout = QuantumRegister(1, "cout")

    reg_help = QuantumRegister(1, "help")

    #reg_result = ClassicalRegister(x_bits, "resultado")

    #x_bits + 3*n_bits
    expmod = QuantumCircuit(reg_x, reg_b, reg_0, reg_cout, reg_help, name="expmod")

    for i in range(bits_expoente):
        expmod.append(ctrl_mult_mod(n_bits, (base**(2**i)) % N, N), reg_x[i:i+1] + reg_b[:] + reg_0[:] + reg_cout[:] + reg_help[:])

        for j in range(N):
            if (base**(2**i) * j) % N == 1:
                a_inv = j
                break

        expmod.append(ctrl_mult_mod(n_bits, a_inv, N).inverse(), reg_x[i:i+1] + reg_0[:] + reg_b[:] + reg_cout[:] + reg_help[:])

        for j in range(n_bits):
            expmod.cswap(reg_x[i], reg_0[j], reg_b[j])

    return expmod
