from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit.library import QFT
import numpy as np

def draper_adder(n_bits, a, controlado=False, div=False):
    # registradores principais
    reg_b = QuantumRegister(n_bits, "b")
    reg_cout = QuantumRegister(1, "cout")

    if div: # se for divisão, *2 até ficar com n_bits
        s = bin(a)[2:] + ("0" * (n_bits - len(bin(a)) + 2))
    else: # se não for divisão, igualar o numero de bits sem alterar o valor
        s = bin(a)[2:].zfill(n_bits)
    s = s[::-1]

    if not controlado:
        circuito = QuantumCircuit(reg_b, reg_cout)

        # QFT
        circuito.append(QFT(n_bits + 1, do_swaps=False), reg_b[:] + reg_cout[:])

        # Portas controladas por A
        for j in range(n_bits):
            for k in range(n_bits - j):
                if s[j] == "1":
                    lam = np.pi / (2**k)
                    circuito.p(lam, reg_b[j + k])

        for j in range(n_bits):
            if s[n_bits - j - 1] == "1":
                lam = np.pi / (2 ** (j + 1))
                circuito.p(lam, reg_cout[0])

        # QFT inversa
        circuito.append(QFT(n_bits + 1, do_swaps=False).inverse(), reg_b[:] + reg_cout[:])

    else:
        # registrador de controle
        reg_c = QuantumRegister(1, "c")

        circuito = QuantumCircuit(reg_c, reg_b, reg_cout)

        # QFT
        circuito.append(QFT(n_bits + 1, do_swaps=False), reg_b[:] + reg_cout[:])

        # Portas controladas por A e pelo registrador de controle
        for j in range(n_bits):
            for k in range(n_bits - j):
                if s[j] == "1":
                    lam = np.pi / (2**k)
                    circuito.cp(lam, reg_c[0], reg_b[j + k])

        for j in range(n_bits):
            if s[n_bits - j - 1] == "1":
                lam = np.pi / (2 ** (j + 1))
                circuito.cp(lam, reg_c[0], reg_cout[0])

        # QFT inversa
        circuito.append(QFT(n_bits + 1, do_swaps=False).inverse(), reg_b[:] + reg_cout[:])

    return circuito

'''
adder = draper_adder(4, 3, controlado=True)

reg_c = QuantumRegister(1, "c")

reg_b = QuantumRegister(4, "b")
number_b = QuantumCircuit(reg_b)
number_b.initialize(9)

reg_cout = QuantumRegister(1, "cout")

reg_result = ClassicalRegister(5, "resultado")

circuito = QuantumCircuit(reg_c, reg_b, reg_cout, reg_result)

circuito.x(reg_c[0])
circuito.append(number_b, reg_b)
circuito.append(adder, reg_c[:] + reg_b[:] + reg_cout[:])

circuito.measure(reg_b[:] + reg_cout[:], reg_result)

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
'''

