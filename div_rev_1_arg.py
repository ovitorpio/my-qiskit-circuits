from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit.library import QFT
from draperqftadder_adapt import draper_adder
from math import log2

ModResult = True
DivResult = False

def div_1_arg(a_bits, b, b_bits):
    reg_a = QuantumRegister(a_bits, "a")

    # registrador dos 0s
    reg_0 = QuantumRegister(a_bits - b_bits + 2, "0")

    # registrador para o carryout do DraperQFTAdder
    reg_cout = QuantumRegister(1, "cout")

    circuito = QuantumCircuit(reg_0, reg_a, reg_cout)

    for i in range(a_bits - b_bits + 1):
        circuito.append(draper_adder(a_bits - i, b, div=True).inverse(), reg_a[:a_bits - i] + reg_cout[:])
        circuito.cx(reg_0[-1], reg_cout[0])
        circuito.cx(reg_cout[0], reg_0[i], ctrl_state="0")
        circuito.cx(reg_0[i], reg_0[i + 1], ctrl_state="0")
        if i > 0:
            circuito.cx(reg_a[a_bits - i], reg_0[-1])
        circuito.append(draper_adder(a_bits - i, b, controlado=True, div=True),
                        reg_0[1 + i:2 + i] + reg_a[:a_bits - i] + reg_cout[:])
        circuito.cx(reg_0[i], reg_0[i + 1], ctrl_state="0")
        if i < a_bits - b_bits:
            circuito.cx(reg_a[a_bits - i - 1], reg_0[-1])

    return circuito

def div_A_mod(a_bits, b, b_bits):
    reg_a = QuantumRegister(a_bits, "a")

    # registrador dos 0s
    reg_0 = QuantumRegister(a_bits - b_bits + 2, "0")

    # registrador para o carryout do DraperQFTAdder
    reg_cout = QuantumRegister(1, "cout")

    reg_0_mod = QuantumRegister(b_bits, "0_mod")

    circuito = QuantumCircuit(reg_0, reg_a, reg_cout, reg_0_mod)

    circuito.append(div_1_arg(a_bits, b, b_bits), reg_0[:] + reg_a[:] + reg_cout[:])

    for i in range(b_bits):
        circuito.cx(reg_a[i], reg_0_mod[i])

    circuito.append(div_1_arg(a_bits, b, b_bits).inverse(), reg_0[:] + reg_a[:] + reg_cout[:])

    return circuito


A = 30
a_bits = int(log2(A))+1
b = 11
b_bits = int(log2(b))+1


reg_a = QuantumRegister(a_bits, "a")
number_a = QuantumCircuit(reg_a)

#number_a.initialize(A)

# registrador dos 0s
reg_0 = QuantumRegister(a_bits - b_bits + 2, "0")

# registrador para o carryout do DraperQFTAdder
reg_cout = QuantumRegister(1, "cout")

reg_0_mod = QuantumRegister(b_bits, "0_mod")

reg_result = ClassicalRegister(a_bits + b_bits, "resultado")
#reg_mod = ClassicalRegister(b_bits, "MOD")
#reg_A_result = ClassicalRegister(a_bits, "ResultadoA")

circuito = QuantumCircuit(reg_0, reg_a, reg_cout, reg_0_mod, reg_result)

for i in range(a_bits):
    circuito.h(reg_a[i])

circuito = (
    circuito.compose(number_a, qubits=reg_a)
    .compose(div_A_mod(a_bits, b, b_bits), qubits=reg_0[:] + reg_a[:] + reg_cout[:] + reg_0_mod[:])
)

circuito.append(QFT(a_bits), reg_a)
'''

reg_a = QuantumRegister(a_bits, "a")
number_a = QuantumCircuit(reg_a)
number_a.initialize(A)

# registrador dos 0s
reg_0 = QuantumRegister(a_bits - b_bits + 2, "0")

# registrador para o carryout do DraperQFTAdder
reg_cout = QuantumRegister(1, "cout")



# divisão
reg_div = ClassicalRegister(a_bits - b_bits + 1, "DIV")
#mod
reg_mod = ClassicalRegister(b_bits, "MOD")

if DivResult:
    circuito = QuantumCircuit(reg_0, reg_a, reg_cout, reg_div)
else:
    circuito = QuantumCircuit(reg_0, reg_a, reg_cout, reg_mod)

circuito = (
    circuito.compose(number_a, qubits=reg_a)
)

for i in range(a_bits - b_bits + 1):
    circuito.append(draper_adder(a_bits - i, b, div=True).inverse(), reg_a[:a_bits - i] + reg_cout[:])
    circuito.cx(reg_0[-1], reg_cout[0])
    circuito.cx(reg_cout[0], reg_0[i], ctrl_state="0")
    circuito.cx(reg_0[i], reg_0[i+1], ctrl_state="0")
    if i > 0:
        circuito.cx(reg_a[a_bits - i], reg_0[-1])
    circuito.append(draper_adder(a_bits - i, b, controlado=True, div=True), reg_0[1 + i:2 + i] + reg_a[:a_bits - i] + reg_cout[:])
    circuito.cx(reg_0[i], reg_0[i+1], ctrl_state="0")
    if i < a_bits - b_bits:
        circuito.cx(reg_a[a_bits - i - 1], reg_0[-1])



# divisão
if DivResult:
    circuito.measure(reg_0[:-1][::-1], reg_div)
else:
    circuito.measure(reg_a[:b_bits], reg_mod)

'''

circuito.measure(reg_a[:] + reg_0_mod[:], reg_result)
#circuito.measure(reg_0_mod, reg_mod)
#circuito.measure(reg_a, reg_A_result)

from qiskit_aer import AerSimulator
from qiskit import transpile

backend1 = AerSimulator()
qc1 = transpile(circuito, backend=backend1)

from qiskit.primitives import StatevectorSampler

statevectorsampler = StatevectorSampler()
pub = (qc1)
job = statevectorsampler.run([pub])


print(f"H dividido por {b}")
if DivResult:
    print("DIV:",job.result()[0].data.DIV.get_int_counts())
else:
    print("|A>|A mod b>:",job.result()[0].data.resultado.get_int_counts())
    #print("A:", job.result()[0].data.ResultadoA.get_int_counts())


circuito.draw("mpl")
