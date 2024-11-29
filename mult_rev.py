from qiskit import QuantumCircuit, QuantumRegister
from c_adder import c_adder as c_adder

def mult_rev(n_bits):
    
    # registrador B
    reg_b = QuantumRegister(n_bits, "b")

    # registrador A
    reg_a = QuantumRegister(n_bits, "a")

    # registrador carryin e carryout
    reg_cin = QuantumRegister(1, "cin")

    #registradores de 0s
    reg_01 = QuantumRegister(n_bits, "01")

    reg_0adder = QuantumRegister(2*n_bits-1, "0adder")

    reg_02 = QuantumRegister(n_bits, "02")

    #registradores carry out
    reg_cout = QuantumRegister(n_bits, "cout")

    # montagem do circuito com os registradores
    circuito = QuantumCircuit(reg_b, reg_01, reg_cin, reg_a, reg_0adder, reg_02, reg_cout, name="mult_rev")

    # loop para a construçao do circuito utilizando o adder controlado
    for i in range(n_bits):
        circuito.cx(reg_b[i], reg_01[-1 - i])
        circuito.append(c_adder(n_bits + i), reg_01[n_bits - 1 - i:n_bits - i] + reg_cin[:] + reg_01[n_bits - i:] + reg_a[:] + reg_0adder[:n_bits + i] + reg_02[:] + reg_cout[0:i+1])
        circuito.cx(reg_b[i], reg_01[-1 - i])

    return circuito
