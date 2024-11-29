from qiskit import QuantumCircuit, QuantumRegister
from mult_rev import mult_rev as mult_rev
from div_rev import div_rev as div_rev

def mult_mod(n_bits):

    mult = mult_rev(n_bits)
    div = div_rev(2*n_bits, n_bits)

    reg_a = QuantumRegister(n_bits, "a")

    reg_b = QuantumRegister(n_bits, "b")

    reg_cin = QuantumRegister(1, "cin")

    reg_cout = QuantumRegister(1, "cout")

    reg_help = QuantumRegister(2, "help")

    reg_n = QuantumRegister(n_bits, "N")

    reg_0_op = QuantumRegister(2*n_bits, "0op")

    reg_0_mod = QuantumRegister(n_bits, "0mod")

    reg_01 = QuantumRegister(n_bits, "01")

    reg_0_div = QuantumRegister(n_bits + 2, "0div")

    reg_0_adder = QuantumRegister(2*n_bits, "0adder")

    circuito = QuantumCircuit(reg_b, reg_01, reg_cin, reg_0_adder, reg_0_div, reg_a, reg_cout, reg_help, reg_n, reg_0_op, reg_0_mod)

    circuito.append(mult, reg_b[:] + reg_01[:] + reg_cin[:] + reg_a[:] + reg_0_adder[1:] + reg_0_op[:])
    circuito.append(div, reg_0_div[:] + reg_n[:] + reg_0_adder[:] + reg_0_op[:] + reg_cout[:] + reg_help[:])
    for i in range(n_bits):
        circuito.cx(reg_0_op[i], reg_0_mod[i])
    circuito.append(div.inverse(), reg_0_div[:] + reg_n[:] + reg_0_adder[:] + reg_0_op[:] + reg_cout[:] + reg_help[:])
    circuito.append(mult.inverse(), reg_b[:] + reg_01[:] + reg_cin[:] + reg_a[:] + reg_0_adder[1:] + reg_0_op[:])

    return circuito
