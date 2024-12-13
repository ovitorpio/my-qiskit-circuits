from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from draperqftadder_adapt import normal_draper_adder
from math import log2

def mult_rev_1_arg(b_bits, b, a_bits):
    s = bin(b)[2:].zfill(a_bits)
    s = s[::-1]

    reg_a = QuantumRegister(a_bits, "a")

    # registrador dos 0s
    reg_01 = QuantumRegister(b_bits - 1, "01")

    reg_0 = QuantumRegister(a_bits, "0")

    # registrador para o carryout do DraperQFTAdder
    reg_cout = QuantumRegister(b_bits, "cout")

    circuito = QuantumCircuit(reg_01, reg_a, reg_0, reg_cout)

    for i in range(b_bits):
        if s[i] == '1':
            circuito.append(normal_draper_adder(a_bits + i), reg_01[b_bits - 1 - i:] + reg_a[:] + reg_0[:] + reg_cout[:i+1])

    return circuito

'''
A = 10
a_bits = int(log2(A))+1
b = 15
b_bits = int(log2(b))+1

reg_a = QuantumRegister(a_bits, "a")
number_a = QuantumCircuit(reg_a)
number_a.initialize(10)

    # registrador dos 0s
reg_01 = QuantumRegister(b_bits - 1, "01")

reg_0 = QuantumRegister(a_bits, "0")

    # registrador para o carryout do DraperQFTAdder
reg_cout = QuantumRegister(b_bits, "cout")

reg_result = ClassicalRegister(a_bits + b_bits, "resultado")

qc = QuantumCircuit(reg_01, reg_a, reg_0, reg_cout, reg_result)

qc = (
    qc.compose(number_a, qubits=reg_a)
    .compose(mult_rev_1_arg(b_bits, b, a_bits), qubits= reg_01[:] + reg_a[:] +reg_0[:] + reg_cout[:]) 
)

qc.measure(reg_0[:] + reg_cout[:], reg_result)

from qiskit_aer import AerSimulator
from qiskit import transpile

backend1 = AerSimulator()
qc1 = transpile(qc, backend=backend1)

from qiskit.primitives import StatevectorSampler

statevectorsampler = StatevectorSampler()
pub = (qc1)
job = statevectorsampler.run([pub], shots=1)
print(job.result()[0].data.resultado.get_int_counts())


print(qc)
'''
