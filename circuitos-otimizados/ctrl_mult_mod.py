from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from draperqftadder_adapt import adder_mod
from math import log2

def ctrl_mult_mod(n_bits, a, N):
    # a * b mod N

    reg_control = QuantumRegister(1, "c")
    
    reg_b = QuantumRegister(n_bits, "b")

    reg_c_aux = QuantumRegister(1, "c_aux")

    reg_0 = QuantumRegister(n_bits + 1, "0")

    reg_help = QuantumRegister(1, "help")

    circuito = QuantumCircuit(reg_control, reg_b, reg_c_aux, reg_0, reg_help, name="mult_mod")

    for i in range(n_bits):
        circuito.ccx(reg_control[0], reg_b[i], reg_c_aux[0])

        circuito.append(adder_mod(n_bits, ((2**i) * a) % N, N, controlado=True), reg_c_aux[:] + reg_0[:] + reg_help[:])

        circuito.ccx(reg_control[0], reg_b[i], reg_c_aux[0])

    return circuito

'''
n_bits = 4
N = 11
a = 7
b = 10

reg_c = QuantumRegister(1, "c")

reg_b = QuantumRegister(n_bits, "b")
number_b = QuantumCircuit(reg_b)
number_b.initialize(b)

reg_c_aux = QuantumRegister(1, "c_aux")

reg_0 = QuantumRegister(n_bits + 1, "0")
    
reg_help = QuantumRegister(1, "help")

reg_result = ClassicalRegister(n_bits + 1, "resultado")

circuito = QuantumCircuit(reg_c, reg_b, reg_c_aux, reg_0, reg_help, reg_result)

circuito.x(reg_c[0])

circuito.append(number_b, reg_b)

circuito.append(ctrl_mult_mod(n_bits, a, N), reg_c[:] + reg_b[:] + reg_c_aux[:] + reg_0[:] + reg_help[:])

circuito.measure(reg_0, reg_result)

from qiskit_aer import AerSimulator
from qiskit import transpile

backend1 = AerSimulator()
qc1 = transpile(circuito, backend=backend1)

from qiskit.primitives import StatevectorSampler

statevectorsampler = StatevectorSampler()
pub = (qc1)
job = statevectorsampler.run([pub], shots=1)
print(job.result()[0].data.resultado.get_int_counts())

#ctrl_mult_mod(4, 5, 11).draw("mpl")
circuito.draw("mpl")
'''