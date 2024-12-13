from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from mult_mod_1_e_2 import mult_mod_2
from math import log2

A = 7
a_bits = int(log2(A))+1
b = 1
b_bits = int(log2(b))+2
N = 5
n_bits = int(log2(N))+1
x = 4
x_bits = int(log2(x))+1

s = bin(x)[2:]
s = s[::-1]

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

reg_result = ClassicalRegister(a_bits, "resultadopowermod")

circuito = QuantumCircuit(reg_01, reg_b, reg_0_div, reg_0, reg_0_cout_div, reg_0_mod, reg_result)

circuito = (
    circuito.compose(number_b, qubits=reg_b)
)

listaQubits = reg_01[:] + reg_b[:] + reg_0_div[:] + reg_0[:] + reg_0_cout_div[:] + reg_0_mod[:]
lista = True
for i in range(x_bits):
    if s[i] == '1':
        if i == 0:
            print(i)
            circuito.append(mult_mod_2(A % N, b, N, n_bits), listaQubits)
            listaQubits = reg_01[:] + reg_0_mod[:] + reg_0_div[:] + reg_0[:] + reg_0_cout_div[:] + reg_b[:] #inverte a posição dos registradores 0_mod e b
            lista = False
        else:
            print(i)
            circuito.append(mult_mod_2(A**(2**i) % N, A**(2**(i-1)) % N, N, n_bits), listaQubits)
            if lista:
                listaQubits = reg_01[:] + reg_0_mod[:] + reg_0_div[:] + reg_0[:] + reg_0_cout_div[:] + reg_b[:]
                lista = False
            else:
                listaQubits = reg_01[:] + reg_b[:] + reg_0_div[:] + reg_0[:] + reg_0_cout_div[:] + reg_0_mod[:]
                lista = True

if s.count("1") % 2 == 1:
    circuito.measure(reg_0_mod, reg_result)
else:
    circuito.measure(reg_b, reg_result)

# simulação
from qiskit_aer import AerSimulator
from qiskit import transpile

backend1 = AerSimulator()
qc1 = transpile(circuito, backend=backend1)

from qiskit.primitives import StatevectorSampler

statevectorsampler = StatevectorSampler()
pub = (qc1)
job = statevectorsampler.run([pub], shots=1)
print(job.result()[0].data.resultadopowermod.get_int_counts())

print(circuito)
#circuito.draw("mpl")
