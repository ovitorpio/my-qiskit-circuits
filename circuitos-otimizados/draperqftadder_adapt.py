from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit.library import QFT, CPhaseGate
import numpy as np
from math import pi

def QFT_correction(qc,reg):
    n = len(reg)

    # Innitial supperposition
    qc.h(reg[0])
    for i in range(2, n):
        qc.rz(((2**(i) - 1) * pi)/(2**i),reg[i-1])
    qc.rz(((2**n - 1) * pi)/(2**(n + 1)), reg[-1])
    qc.barrier()

    for i in range(n-1):
        if i%2 == 0:
            # Adding the CNOTs layers
            for j in range(1, i+1, 2):
                qc.cx(reg[j],reg[j + 1])



            for j in range(0, i+1, 2):
                qc.cx(reg[j + 1],reg[j])
            qc.barrier()

            # Adding the rotations
            for j in range(0, i + 1, 2):
                qc.rz(-pi/(2**(j + 2)), reg[j])
            qc.barrier()

        else:
            # Adding the CNOTs layers
            for j in range(0, i+1, 2):
                qc.cx(reg[j],reg[j + 1])


            for j in range(1, i+1, 2):
                qc.cx(reg[j + 1],reg[j])
            qc.barrier()

            # Adding the rotations
            if i != 0:
                qc.rx(pi/2, reg[0])
            for j in range(1, i + 1, 2):
                qc.rz(-pi/(2**(j + 2)), reg[j])
            qc.barrier()

    # Adding the middle CNOTs layers
    for j in range(n%2, i+1, 2): # The initial position is defined by the parity if n
        qc.cx(reg[j],reg[j + 1])

    for j in range((n+1)%2, i+1, 2):
        qc.cx(reg[j + 1],reg[j])

    qc.barrier()

    for i in range(n-2, -1, -1):
        if i%2 == 0:
            # Adding the rotations
            if i != 0:
                qc.rx(pi/2, reg[0])
            for j in range(1, i + 1, 2):
                qc.rz(-pi/(2**(j + 2)), reg[j])
            qc.barrier()


            # Adding the CNOTs layers
            for j in range(1, i+1, 2):
                qc.cx(reg[j],reg[j + 1])

            for j in range(0, i+1, 2):
                qc.cx(reg[j + 1],reg[j])
            qc.barrier()


        else:
            # Adding the rotations
            for j in range(0, i, 2):
                qc.rz(-pi/(2**(j + 2)), reg[j])
            qc.barrier()

            # Adding the CNOTs layers
            for j in range(0, i+1, 2):
                qc.cx(reg[j],reg[j + 1])

            for j in range(1, i+1, 2):
                qc.cx(reg[j + 1],reg[j])
            qc.barrier()

    # Removing the supperposition
    qc.h(reg[0])
    for i in range(2, n):
        qc.rz(((2**(i) - 1) * pi)/(2**i),reg[i-1])
    qc.rz(((2**n - 1) * pi)/(2**(n + 1)), reg[-1])
    qc.barrier()

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
        circuito = QuantumCircuit(reg_b, reg_cout, name="adapt_drap_adder")

        # QFT
        circuito.append(QFT(n_bits + 1, do_swaps=False), reg_b[:] + reg_cout[:])
        #QFT_correction(circuito, reg_b[:] + reg_cout[:])

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

        circuito = QuantumCircuit(reg_c, reg_b, reg_cout, name="c_adapt_drap_adder")

        # QFT
        circuito.append(QFT(n_bits + 1, do_swaps=False), reg_b[:] + reg_cout[:])
        #QFT_correction(circuito, reg_b[:] + reg_cout[:])

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

def normal_draper_adder(n_bits, controlado=False):
        if controlado:
            reg_control = QuantumRegister(1, "c")

        reg_a = QuantumRegister(n_bits, "a")

        reg_b = QuantumRegister(n_bits, "b")
        
        reg_cout = QuantumRegister(1, "cout")

        if controlado:
            circuito = QuantumCircuit(reg_control, reg_a, reg_b, reg_cout, name="c_drap_adder")

            circuito.append(QFT(n_bits + 1, do_swaps=False), reg_b[:] + reg_cout[:])

            for j in range(n_bits):
                for k in range(n_bits - j):
                    lam = np.pi / (2**k)
                    circuito.append(CPhaseGate(lam).control(1), reg_control[:] + reg_a[j:j+1] + reg_b[j + k:j + k + 1])
                    #circuito.cp(lam, reg_a[j], reg_b[j + k])

            for j in range(n_bits):
                lam = np.pi / (2 ** (j + 1))
                circuito.append(CPhaseGate(lam).control(1), reg_control[:] + reg_a[n_bits - j - 1:n_bits - j] + reg_cout[:])
                #circuito.cp(lam, reg_a[n_bits - j - 1], reg_cout[0])

        else: 
            circuito = QuantumCircuit(reg_a, reg_b, reg_cout)

            circuito.append(QFT(n_bits + 1, do_swaps=False), reg_b[:] + reg_cout[:])

            for j in range(n_bits):
                for k in range(n_bits - j):
                    lam = np.pi / (2**k)
                    circuito.cp(lam, reg_a[j], reg_b[j + k])

            for j in range(n_bits):
                lam = np.pi / (2 ** (j + 1))
                circuito.cp(lam, reg_a[n_bits - j - 1], reg_cout[0])

        circuito.append(QFT(n_bits + 1, do_swaps=False).inverse(), reg_b[:] + reg_cout[:])

        return circuito

def adder_mod(n_bits, a, N, controlado=False):
    # a + b mod N

    if controlado:
        reg_control = QuantumRegister(1, "c")

    reg_b = QuantumRegister(n_bits, "b")
        
    reg_cout = QuantumRegister(1, "cout")

    reg_help = QuantumRegister(1, "help")

    if controlado:
        circuito = QuantumCircuit(reg_control, reg_b, reg_cout, reg_help, name="c_adder_mod")

        circuito.append(draper_adder(n_bits, a, controlado=True), reg_control[:] + reg_b[:] + reg_cout[:])

        circuito.append(draper_adder(n_bits, N, controlado=True).inverse(), reg_control[:] + reg_b[:] + reg_cout[:])

        circuito.cx(reg_cout[0], reg_help[0])

        circuito.append(draper_adder(n_bits, N, controlado=True), reg_help[:] + reg_b[:] + reg_cout[:])
    
        circuito.append(draper_adder(n_bits, a, controlado=True).inverse(), reg_control[:] + reg_b[:] + reg_cout[:])

        circuito.x(reg_cout)
        circuito.ccx(reg_control[0], reg_cout[0], reg_help[0])
        circuito.x(reg_cout)


        circuito.append(draper_adder(n_bits, a, controlado=True), reg_control[:] + reg_b[:] + reg_cout[:])

    else:
        circuito = QuantumCircuit(reg_b, reg_cout, reg_help, name="adder_mod")

        circuito.append(draper_adder(n_bits, a), reg_b[:] + reg_cout[:])

        circuito.append(draper_adder(n_bits, N).inverse(), reg_b[:] + reg_cout[:])

        circuito.cx(reg_cout[0], reg_help[0])

        circuito.append(draper_adder(n_bits, N, controlado=True), reg_help[:] + reg_b[:] + reg_cout[:])
    
        circuito.append(draper_adder(n_bits, a).inverse(), reg_b[:] + reg_cout[:])

        circuito.cx(reg_cout[0], reg_help[0], ctrl_state="0")

        circuito.append(draper_adder(n_bits, a), reg_b[:] + reg_cout[:])

    return circuito


'''
n = 6
n_bits = 3
a = 5 % n
b = 1 % n

reg_c = QuantumRegister(1, "c")

reg_b = QuantumRegister(n_bits, "b")
number_b = QuantumCircuit(reg_b)
number_b.initialize(b)

reg_cout = QuantumRegister(1, "cout")
    
reg_help = QuantumRegister(1, "help")

reg_result = ClassicalRegister(n_bits + 2, "resultado")

circuito = QuantumCircuit(reg_c, reg_b, reg_cout, reg_help, reg_result)

circuito.x(reg_c[0])

#circuito.h(reg_b[:3])
circuito.append(number_b, reg_b[:])

circuito.append(adder_mod(n_bits, a, n, controlado=True), reg_c[:] + reg_b[:] + reg_cout[:] + reg_help[:])

circuito.measure(reg_b[:] + reg_cout[:] + reg_help[:], reg_result)

from qiskit_aer import AerSimulator
from qiskit import transpile

backend1 = AerSimulator()
qc1 = transpile(circuito, backend=backend1)

from qiskit.primitives import StatevectorSampler

statevectorsampler = StatevectorSampler()
pub = (qc1)
job = statevectorsampler.run([pub], shots=1)
print(job.result()[0].data.resultado.get_int_counts())

print(circuito)
'''
