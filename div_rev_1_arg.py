from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from draperqftadder_adapt import draper_adder

a_bits = 4
b_bits = 2
b = 3


reg_a = QuantumRegister(a_bits, "a")
number_a = QuantumCircuit(reg_a)
number_a.initialize(11)

# registrador dos 0s
reg_0 = QuantumRegister(a_bits - b_bits + 2, "0")

# registrador para o carryout do CDKMRippleCarryAdder
reg_cout = QuantumRegister(1, "cout")

#reg_help = QuantumRegister(1, "help")

reg_result = ClassicalRegister(a_bits - b_bits + 1, "resultado")

circuito = QuantumCircuit(reg_0, reg_a, reg_cout, reg_result)

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

circuito.measure(reg_0[:-1][::-1], reg_result)

from qiskit_aer import AerSimulator
from qiskit import transpile

backend1 = AerSimulator()
qc1 = transpile(circuito, backend=backend1)

from qiskit.primitives import StatevectorSampler

statevectorsampler = StatevectorSampler()
pub = (qc1)   
job = statevectorsampler.run([pub])
print(job.result()[0].data.resultado.get_int_counts())

circuito.draw("mpl")
