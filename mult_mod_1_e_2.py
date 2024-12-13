from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from mult_rev_1_arg import mult_rev_1_arg
from div_rev_1_arg import div_1_arg
from math import log2

def mult_mod_1(a_bits, b, b_bits, N, n_bits):
    reg_a = QuantumRegister(a_bits, "a")

    # registradores 0 mult
    reg_01 = QuantumRegister(b_bits - 1, "01")
    reg_0 = QuantumRegister(a_bits + b_bits, "0")
    reg_0_div = QuantumRegister(a_bits + b_bits - n_bits + 2, "0_div")
    reg_0_cout_div = QuantumRegister(1, "0_cout")

    # registrador 0 para armazenar o resultado
    reg_0_mod = QuantumRegister(n_bits, "0_mod")

    circuito = QuantumCircuit(reg_01, reg_a, reg_0_div, reg_0, reg_0_cout_div, reg_0_mod)

    circuito.append(mult_rev_1_arg(b_bits, b, a_bits), reg_01[:] + reg_a[:] + reg_0[:])
    circuito.append(div_1_arg(a_bits + b_bits, N, n_bits), reg_0_div[:] + reg_0[:] + reg_0_cout_div[:])

    for i in range(n_bits):
        circuito.cx(reg_0[i], reg_0_mod[i])

    circuito.append(div_1_arg(a_bits + b_bits, N, n_bits).inverse(), reg_0_div[:] + reg_0[:] + reg_0_cout_div[:])
    circuito.append(mult_rev_1_arg(b_bits, b, a_bits).inverse(), reg_01[:] + reg_a[:] + reg_0[:])

    return circuito

def mult_mod_2(a, b, N, n_bits):
    n_bits = int(log2(N))+1
    A_mod = a % N
    b_mod = b % N
    b_bits = int(log2(b))+1


    for i in range(N):
        if ((A_mod*b_mod)%N)*i % N == b_mod:
            x = i
            break

    reg_b = QuantumRegister(n_bits, "b")

    # registradores 0 mult
    reg_01 = QuantumRegister(n_bits - 1, "01")
    reg_0 = QuantumRegister(2*n_bits, "0")
    reg_0_div = QuantumRegister(n_bits + 2, "0_div")
    reg_0_cout_div = QuantumRegister(1, "0_cout")

    # registrador 0 para armazenar o resultado
    reg_0_mod = QuantumRegister(n_bits, "0_mod")


    # numero de bits = 7*n_bits
    circuito = QuantumCircuit(reg_01, reg_b, reg_0_div, reg_0, reg_0_cout_div, reg_0_mod, name=str(a))

    circuito.append(mult_mod_1(n_bits, A_mod, n_bits, N, n_bits), reg_01[:] + reg_b[:] + reg_0_div[:] + reg_0[:] + reg_0_cout_div[:] + reg_0_mod[:])

    circuito.append(mult_mod_1(n_bits, x, n_bits, N, n_bits).inverse(), reg_01[:] + reg_0_mod[:] + reg_0_div[:] + reg_0[:] + reg_0_cout_div[:] + reg_b[:])

    return circuito



'''
A = 1
a_bits = int(log2(A))+1
b = 7
b_bits = int(log2(b))+1
N = 5
n_bits = int(log2(N))+1

n_bits = int(log2(N))+1
A_mod = A % N
b_mod = b % N
b_bits = int(log2(b))+1


for i in range(N):
        if ((A_mod*b_mod)%N)*i % N == b_mod:
            x = i
            break

reg_b = QuantumRegister(n_bits, "b")
number_b = QuantumCircuit(reg_b)
number_b.initialize(A%N)

# registradores 0 mult
reg_01 = QuantumRegister(n_bits - 1, "01")
reg_0 = QuantumRegister(2*n_bits, "0")
reg_0_div = QuantumRegister(n_bits + 2, "0_div")
reg_0_cout_div = QuantumRegister(1, "0_cout")

# registrador 0 para armazenar o resultado
reg_0_mod = QuantumRegister(n_bits, "0_mod")


reg_result_mod = ClassicalRegister(n_bits, "resultadoMOD")
reg_result_B = ClassicalRegister(n_bits, "resultadoB")


# numero de bits = 7*n_bits
circuito = QuantumCircuit(reg_01, reg_b, reg_0_div, reg_0, reg_0_cout_div, reg_0_mod, reg_result_B, reg_result_mod)

circuito = (
    circuito.compose(number_b, qubits=reg_b)
)

listaQubits = reg_01[:] + reg_b[:] + reg_0_div[:] + reg_0[:] + reg_0_cout_div[:] + reg_0_mod[:]
circuito.append(mult_mod_2(b, A % N, N, n_bits), listaQubits)

#circuito.append(mult_mod_1(n_bits, A_mod, n_bits, N, n_bits), reg_01[:] + reg_b[:] + reg_0_div[:] + reg_0[:] + reg_0_cout_div[:] + reg_0_mod[:])

#circuito.append(mult_mod_1(n_bits, x, n_bits, N, n_bits).inverse(), reg_01[:] + reg_0_mod[:] + reg_0_div[:] + reg_0[:] + reg_0_cout_div[:] + reg_b[:])

circuito.measure(reg_b, reg_result_B)
circuito.measure(reg_0_mod, reg_result_mod)

# simulação
from qiskit_aer import AerSimulator
from qiskit import transpile

backend1 = AerSimulator()
qc1 = transpile(circuito, backend=backend1)

from qiskit.primitives import StatevectorSampler

statevectorsampler = StatevectorSampler()
pub = (qc1)
job = statevectorsampler.run([pub], shots=1)
print(job.result()[0].data.resultadoB.get_int_counts())
print(job.result()[0].data.resultadoMOD.get_int_counts())

print(circuito)
'''