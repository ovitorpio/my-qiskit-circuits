from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit.library import QFT, CPhaseGate
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
        circuito = QuantumCircuit(reg_b, reg_cout, name="adapt_drap_adder")

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

        circuito = QuantumCircuit(reg_c, reg_b, reg_cout, name="c_adapt_drap_adder")

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




