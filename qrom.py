# qrom.py 
# XOR-lookup T[a] - versão 4L-4 Toffolis, 2 ancillas, saída em |out⟩
# address  -->  bits mais SIGNIFICATIVOS primeiro (endianness little-endian)

from qiskit import QuantumCircuit, QuantumRegister
from math import ceil, log2

def qrom(table, w_bits):
    """
    XOR (⊕) do valor table[a] num registrador-alvo com w_bits qubits.
    table: lista de inteiros    0 ≤ t < 2**w_bits
    w_bits: tam do registrador alvo
    Regs na chamada .append():
        addr (⌈log2 L⌉ qubits) | out (w_bits) | anc (2 qubits)
    """
    L  = len(table)
    nA = ceil(log2(L))               #### bits de endereço
    addr = QuantumRegister(nA,  "addr")
    out  = QuantumRegister(w_bits, "out")
    anc  = QuantumRegister(2,   "anc")   #### a0, a1 resetados)

    qc = QuantumCircuit(addr, out, anc, name=f"QROM{L}")

    ### unary-iteration à la Babbush (4L-4 Toffolis)

    ### optei por gerar um circuito mais compacto e direto em vez de gastar tempo (e complicar o código) pra 
    ##  fazer a versão ultrareduzida que seria relevante só pra L muito grande (tipo 2^5, 2^10 ou mais).
    ### 
    
    ### L até 256 como provavelmente vamos usar "c_mul = 2,3,4", o custo extra é muito pequeno 
    ### e o circuito fica mais fácil de gerar em python. Ganhamos tempo de transpile e simulação tbm
 
    
    
    for j, val in enumerate(table):
        bin_j = [(j >> k) & 1 for k in range(nA)]   # little-endian
        ## Construir máscara de controles (ON/OFF) sobre anc[0]
        ## anc[0] = 1  se  addr == j
        for k, bit in enumerate(bin_j):
            if bit == 0:
                qc.x(addr[k])
        qc.mcx(addr, anc[0])          ### nA-control Toffoli
        for k, bit in enumerate(bin_j):
            if bit == 0:
                qc.x(addr[k])

        ### XOR val (w_bits) em out controlado por anc[0]
        for b in range(w_bits):
            if (val >> b) & 1:
                qc.cx(anc[0], out[b])

        qc.mcx(addr, anc[1])          ### anc[1] = AND(addr)  (para des-Toffoli)
        qc.cx(anc[1], anc[0])
        qc.mcx(addr, anc[1])
        qc.barrier()

    return qc
