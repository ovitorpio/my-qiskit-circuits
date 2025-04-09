from qiskit import QuantumCircuit, QuantumRegister
from draperqftadder_adapt import adder_mod
from qiskit.circuit.library import QFT

def ctrl_mult_mod(n_bits, a, N):
    """Retorna um circuito que implementa o Multiplicador Modular proposto no artigo [1],
       com 2 operandos clássicamente calculados (a e N).
       
       Utiliza o Adder Modular 
       https://github.com/kourggos/my-qiskit-circuits/blob/e261229ef1699ea813e49bc70432219047aa2ea3/draperqftadder_adapt.py

    Faz a operação a * b mod N : b é o número que está no registrador reg_b

    Exemplo de Multiplicador Modular com um operando de 4 bits
    
              ┌──────────────┐┌──────────────┐┌──────────────┐┌──────────────┐
   c: ────────┤0             ├┤0             ├┤0             ├┤0             ├─────────
              │              ││              ││              ││              │
 b_0: ────────┤1             ├┤              ├┤              ├┤              ├─────────
              │              ││              ││              ││              │
 b_1: ────────┤              ├┤1             ├┤              ├┤              ├─────────
              │              ││              ││              ││              │
 b_2: ────────┤              ├┤              ├┤1             ├┤              ├─────────
              │              ││              ││              ││              │
 b_3: ────────┤              ├┤              ├┤              ├┤1             ├─────────
      ┌──────┐│              ││              ││              ││              │┌───────┐
 0_0: ┤0     ├┤2 c_adder_mod ├┤2 c_adder_mod ├┤2 c_adder_mod ├┤2 c_adder_mod ├┤0      ├
      │      ││              ││              ││              ││              ││       │
 0_1: ┤1     ├┤3             ├┤3             ├┤3             ├┤3             ├┤1      ├
      │      ││              ││              ││              ││              ││       │
 0_2: ┤2 QFT ├┤4             ├┤4             ├┤4             ├┤4             ├┤2 IQFT ├
      │      ││              ││              ││              ││              ││       │
 0_3: ┤3     ├┤5             ├┤5             ├┤5             ├┤5             ├┤3      ├
      │      ││              ││              ││              ││              ││       │
 0_4: ┤4     ├┤6             ├┤6             ├┤6             ├┤6             ├┤4      ├
      └──────┘│              ││              ││              ││              │└───────┘
help: ────────┤7             ├┤7             ├┤7             ├┤7             ├─────────
              └──────────────┘└──────────────┘└──────────────┘└──────────────┘

    Parametros:
    n_bits : int
        Número de bits do operando.
    a : int
        Operando implícito calculado classicamente.
    N : int
        Operando implícito que controla o mod

    Retorna:
    QuantumCircuit 
    circuito montado com os registradores nessa ordem:
        2n + 3 qubits
        registrador_controle (1 bit)
        registrador_operando (n_bits)
        registrador_ancilla (n_bits + 2)

    References: 
        [1] Vlatko Vedral, Adriano Barenco, and Artur Ekert, Quantum networks for elementary arithmetic operations, quant-ph/9511018
    """    

    reg_control = QuantumRegister(1, "c")
    
    reg_b = QuantumRegister(n_bits, "b")

    reg_0 = QuantumRegister(n_bits + 1, "0")

    reg_help = QuantumRegister(1, "help")

    qc = QuantumCircuit(reg_control, reg_b, reg_0, reg_help, name="mult_mod")

    qc.append(QFT(n_bits + 1, do_swaps=False), reg_0)

    for i in range(n_bits):

        qc.append(adder_mod(n_bits, ((2**i) * a) % N, N, controlado=True, control_number=2), reg_control[:] + reg_b[i:i+1] + reg_0[:] + reg_help[:])

    qc.append(QFT(n_bits + 1, do_swaps=False).inverse(), reg_0)

    return qc