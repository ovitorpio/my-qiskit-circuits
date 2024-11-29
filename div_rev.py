from qiskit import QuantumCircuit, QuantumRegister
from qiskit.circuit.library import CDKMRippleCarryAdder
from c_adder import c_adder as c_adder

def div_rev(a_bits, b_bits):

    reg_a = QuantumRegister(a_bits, "a")
    
    reg_b = QuantumRegister(b_bits, "b")

    # registrador dos 0s
    reg_01 = QuantumRegister(a_bits - b_bits + 2, "0")

    reg_0_c_adder = QuantumRegister(a_bits, "0adder")

    # registrador para o carryout do CDKMRippleCarryAdder
    reg_cout = QuantumRegister(1, "cout")

    reg_help = QuantumRegister(2, "help")

    circuito = QuantumCircuit(reg_01, reg_b, reg_0_c_adder, reg_a, reg_cout, reg_help, name="div_rev")

    for i in range(a_bits - b_bits + 1):
        circuito.append(CDKMRippleCarryAdder(a_bits - i, kind="half").inverse(), reg_01[2 + i:] + reg_b[:] + reg_a[:a_bits - i] + reg_cout[:] + reg_help[0:1])
        circuito.cx(reg_help[1], reg_cout[0])
        circuito.cx(reg_cout[0], reg_01[i], ctrl_state="0")
        circuito.cx(reg_01[i], reg_01[i+1], ctrl_state="0")
        if i > 0:
            circuito.cx(reg_a[a_bits - i], reg_help[1])
        circuito.append(c_adder(a_bits - i), reg_01[1 + i:2 + i] + reg_help[0:1] + reg_01[2+i:] + reg_b[:] +  reg_0_c_adder[i:] + reg_a[:a_bits - i] + reg_cout[:])
        circuito.cx(reg_01[i], reg_01[i+1], ctrl_state="0")
        if i < a_bits - b_bits:
            circuito.cx(reg_a[a_bits - i - 1], reg_help[1])

    return circuito
