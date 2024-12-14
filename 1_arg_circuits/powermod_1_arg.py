from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from mult_mod_1_e_2 import mult_mod_2
from math import log2

A = 7
a_bits = int(log2(A))+1
b = 1
b_bits = int(log2(b))+2
N = 5
n_bits = int(log2(N))+1
x = 5
x_bits = int(log2(x))+1

reg_x = QuantumRegister(x_bits, "x")
number_x = QuantumCircuit(reg_x)
#number_x.initialize(x)

reg_b = QuantumRegister(n_bits, "b")
number_b = QuantumCircuit(reg_b)
number_b.initialize(b)

# registradores 0 mult
reg_01 = QuantumRegister(n_bits - 1, "01")
reg_0 = QuantumRegister(2*n_bits, "0")
reg_0_div = QuantumRegister(n_bits + 2, "0_div")
reg_0_cout_div = QuantumRegister(1, "0_cout")

# registrador 0 para armazenar o resultado
reg_0_mod = QuantumRegister(n_bits, "0_mod")

reg_result = ClassicalRegister(x_bits + n_bits, "resultadopowermod")

circuito = QuantumCircuit(reg_x, reg_01, reg_b, reg_0_div, reg_0, reg_0_cout_div, reg_0_mod, reg_result)

circuito.h(reg_x)

circuito = (
    circuito.compose(number_b, qubits=reg_b)
    .compose(number_x, qubits=reg_x)
)

listaQubits = reg_01[:] + reg_b[:] + reg_0_div[:] + reg_0[:] + reg_0_cout_div[:] + reg_0_mod[:]

for i in range(x_bits):
    circuito.append(mult_mod_2(A**(2**i) % N, N, n_bits, controlado=True), reg_x[i:i+1]  + listaQubits)



circuito.measure(reg_x[:] + reg_b[:], reg_result)

# simulação
from qiskit_aer import AerSimulator
from qiskit import transpile

backend1 = AerSimulator()
qc1 = transpile(circuito, backend=backend1)

from qiskit.primitives import StatevectorSampler

statevectorsampler = StatevectorSampler()
pub = (qc1)
job = statevectorsampler.run([pub])
print(job.result()[0].data.resultadopowermod.get_int_counts())

for i in job.result()[0].data.resultadopowermod.get_int_counts():
    res = f"{i:9b}".strip()
    resB = "0b0" + res[:-x_bits]
    resA = "0b" + res[-x_bits:]
    print("|x>:", eval(resA),"|b*A^x mod N>:",eval(resB))

#print(circuito)
circuito.draw("mpl")
