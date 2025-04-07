from qiskit import QuantumCircuit, QuantumRegister
from qiskit.circuit.library import QFT
import numpy as np


def draper_adder(n_bits, a, controlado=False, div=False):
    """Retorna um circuito que corresponde ao DraperQFTAdder [1], sem as QFTs e com um operando clássicamente calculado.

    Faz a operação a + b : b é o número que está no registrador reg_b.

    Parametros:
    n_bits : int
        Número de bits do operando.
    a : int
        Operando implícito calculado classicamente.
    controlado : bool
        Se o adder será controlado ou não (precisa do bit de controle).
    div : bool
        Se o adder será utilizado em uma divisão.

    Retorna:
    QuantumCircuit 
    circuito montado com os registradores nessa ordem:
        if controlado: 
            n + 2 qubits
            registrador_controle (1 bit)
            registrador_operando (n bits)
            registrador_carryout (1 bit)
        else:
            n + 1 qubits
            registrador_operando (n bits)
            registrador_carryout (1 bit)

    References: 
        [1] T. G. Draper, Addition on a Quantum Computer, 2000. arXiv:quant-ph/0008033
        https://docs.quantum.ibm.com/api/qiskit/qiskit.circuit.library.DraperQFTAdder
    """

    # Registradores principais
    reg_b = QuantumRegister(n_bits, "b")
    reg_cout = QuantumRegister(1, "cout")

    if div: # Se for divisão, *2 até ficar com n_bits
        bitstring = bin(a)[2:] + ("0" * (n_bits - len(bin(a)) + 2))
    else: # Se não for divisão, igualar o numero de bits sem alterar o valor
        bitstring = bin(a)[2:].zfill(n_bits)
    bitstring = bitstring[::-1]

    if not controlado:
        qc = QuantumCircuit(reg_b, reg_cout, name="adapt_drap_adder")

        # Portas controladas por A
        for j in range(n_bits):
            for k in range(n_bits - j):
                if bitstring[j] == "1":
                    lam = np.pi / (2**k)
                    qc.p(lam, reg_b[j + k])

        for j in range(n_bits):
            if bitstring[n_bits - j - 1] == "1":
                lam = np.pi / (2 ** (j + 1))
                qc.p(lam, reg_cout[0])

    else:
        # Registrador de controle
        reg_c = QuantumRegister(1, "c")

        qc = QuantumCircuit(reg_c, reg_b, reg_cout, name="c_adapt_drap_adder")

        # Portas controladas por A e pelo registrador de controle
        for j in range(n_bits):
            for k in range(n_bits - j):
                if bitstring[j] == "1":
                    lam = np.pi / (2**k)
                    qc.cp(lam, reg_c[0], reg_b[j + k])

        for j in range(n_bits):
            if bitstring[n_bits - j - 1] == "1":
                lam = np.pi / (2 ** (j + 1))
                qc.cp(lam, reg_c[0], reg_cout[0])

    return qc


def adder_mod(n_bits, a, N, controlado=False):
    """Retorna um circuito que implementa o Adder Modular proposto no artigo [1]
        usando o DraperQFTAdder com 1 operando clássicamente calculado como Adder e aplicando
        otimizações do artigo [2] quanto as QFTs.

    Faz a operação a + b mod N : b é o número que está no registrador reg_b.

    Exemplo: Adder Modular controlado, com um operando de 4 qubits. 

      ┌─────────────────────┐┌────────────────────────┐                                             ┌────────────────────────┐                                ┌─────────────────────┐
   c: ┤0                    ├┤0                       ├─────────────────────────────────────────────┤0                       ├────────────────■───────────────┤0                    ├
      │                     ││                        │┌───────┐     ┌──────┐┌─────────────────────┐│                        │┌───────┐       │       ┌──────┐│                     │
 b_0: ┤1                    ├┤1                       ├┤0      ├─────┤0     ├┤1                    ├┤1                       ├┤0      ├───────┼───────┤0     ├┤1                    ├
      │                     ││                        ││       │     │      ││                     ││                        ││       │       │       │      ││                     │
 b_1: ┤2                    ├┤2                       ├┤1      ├─────┤1     ├┤2                    ├┤2                       ├┤1      ├───────┼───────┤1     ├┤2                    ├
      │  c_adapt_drap_adder ││  c_adapt_drap_adder_dg ││       │     │      ││                     ││  c_adapt_drap_adder_dg ││       │       │       │      ││  c_adapt_drap_adder │
 b_2: ┤3                    ├┤3                       ├┤2 IQFT ├─────┤2 QFT ├┤3                    ├┤3                       ├┤2 IQFT ├───────┼───────┤2 QFT ├┤3                    ├
      │                     ││                        ││       │     │      ││  c_adapt_drap_adder ││                        ││       │       │       │      ││                     │
 b_3: ┤4                    ├┤4                       ├┤3      ├─────┤3     ├┤4                    ├┤4                       ├┤3      ├───────┼───────┤3     ├┤4                    ├
      │                     ││                        ││       │     │      ││                     ││                        ││       │┌───┐  │  ┌───┐│      ││                     │
cout: ┤5                    ├┤5                       ├┤4      ├──■──┤4     ├┤5                    ├┤5                       ├┤4      ├┤ X ├──■──┤ X ├┤4     ├┤5                    ├
      └─────────────────────┘└────────────────────────┘└───────┘┌─┴─┐└──────┘│                     │└────────────────────────┘└───────┘└───┘┌─┴─┐└───┘└──────┘└─────────────────────┘
 anc: ──────────────────────────────────────────────────────────┤ X ├────────┤0                    ├────────────────────────────────────────┤ X ├────────────────────────────────────
                                                                └───┘        └─────────────────────┘                                        └───┘

    Parametros:
    n_bits : int
        Número de bits do operando.
    a : int
        Operando implícito calculado classicamente.
    N : int
        Operando implícito que controla o mod
    controlado : bool
        Se o adder será controlado ou não (precisa do bit de controle).

    Retorna:
    QuantumCircuit 
    circuito montado com os registradores nessa ordem:
        if controlado: 
            n + 3 qubits
            registrador_controle (1 bit)
            registrador_operando (n bits)
            registrador_carryout (1 bit)
            registrador_ancilla (1 bit)
        else:
            n + 2 qubits
            registrador_operando (n bits)
            registrador_carryout (1 bit)
            registrador_ancilla (1 bit)

    References: 
        [1] Vlatko Vedral, Adriano Barenco, and Artur Ekert, Quantum networks for elementary arithmetic operations, quant-ph/9511018
        [2] Stephane Beauregard, Circuit for Shor's algorithm using 2n+3 qubits, arXiv:quant-ph/0205095
    """

    # Construção dos registradores

    if controlado:
        reg_control = QuantumRegister(1, "c")

    reg_b = QuantumRegister(n_bits, "b")
        
    reg_cout = QuantumRegister(1, "cout")

    reg_anc = QuantumRegister(1, "anc")

    if controlado:
        # Construção do circuito
        qc = QuantumCircuit(reg_control, reg_b, reg_cout, reg_anc, name="c_adder_mod") 
        
        qc.append(draper_adder(n_bits, a, controlado=True), reg_control[:] + reg_b[:] + reg_cout[:])

        qc.append(draper_adder(n_bits, N, controlado=True).inverse(), reg_control[:] + reg_b[:] + reg_cout[:])

        qc.append(QFT(n_bits + 1, do_swaps=False).inverse(), reg_b[:] + reg_cout[:])

        qc.cx(reg_cout[0], reg_anc[0])

        qc.append(QFT(n_bits + 1, do_swaps=False), reg_b[:] + reg_cout[:])

        qc.append(draper_adder(n_bits, N, controlado=True), reg_anc[:] + reg_b[:] + reg_cout[:])
    
        qc.append(draper_adder(n_bits, a, controlado=True).inverse(), reg_control[:] + reg_b[:] + reg_cout[:])

        qc.append(QFT(n_bits + 1, do_swaps=False).inverse(), reg_b[:] + reg_cout[:])

        qc.x(reg_cout)
        qc.ccx(reg_control[0], reg_cout[0], reg_anc[0])
        qc.x(reg_cout)

        qc.append(QFT(n_bits + 1, do_swaps=False), reg_b[:] + reg_cout[:])

        qc.append(draper_adder(n_bits, a, controlado=True), reg_control[:] + reg_b[:] + reg_cout[:])

    else:
        qc = QuantumCircuit(reg_b, reg_cout, reg_anc, name="adder_mod")

        qc.append(draper_adder(n_bits, a), reg_b[:] + reg_cout[:])

        qc.append(draper_adder(n_bits, N).inverse(), reg_b[:] + reg_cout[:])

        qc.append(QFT(n_bits + 1, do_swaps=False).inverse(), reg_b[:] + reg_cout[:])

        qc.cx(reg_cout[0], reg_anc[0])

        qc.append(QFT(n_bits + 1, do_swaps=False).inverse(), reg_b[:] + reg_cout[:])

        qc.append(draper_adder(n_bits, N, controlado=True), reg_anc[:] + reg_b[:] + reg_cout[:])
    
        qc.append(draper_adder(n_bits, a).inverse(), reg_b[:] + reg_cout[:])

        qc.append(QFT(n_bits + 1, do_swaps=False).inverse(), reg_b[:] + reg_cout[:])

        qc.cx(reg_cout[0], reg_anc[0], ctrl_state="0")

        qc.append(QFT(n_bits + 1, do_swaps=False).inverse(), reg_b[:] + reg_cout[:])

        qc.append(draper_adder(n_bits, a), reg_b[:] + reg_cout[:])

    return qc

