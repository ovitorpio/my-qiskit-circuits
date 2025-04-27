# expmod_windowed.py
# 
# Modular exponentiation  |x⟩⨂|0⟩   -->   |x⟩⨂|base^x  (mod N)|
#
#  “double–and–square” realizado com windowed arithmetic
#   como nas seções 3.2–3.5 de Gidney & Ekerå (2019).
#   dois níveis de janelas
#       c_exp  --> janela sobre expoente  (nº de multiplicações)
#       c_mul  --> janela sobre multiplicação (nº de somas)
#   multiplicação modular constante implementada no
#   arquivo mult_mod_windowed.py


from math import ceil, log2, prod
from qiskit import QuantumCircuit, QuantumRegister
from mult_mod_windowed import mult_mod_windowed


def expmod_windowed(N: int,
                    base: int,
                    n_exp: int,
                    c_exp: int = 3,
                    c_mul: int = 3):
    """
    Modular exponentiation  |e⟩|0⟩  ->  |e⟩|base**e mod N⟩
    ------------------------------------------------------
        N      - módulo (clássico, ímpar)
        base   - inteiro base  (coprimo de N)
        n_exp  - qubits do expoente |e⟩
        c_exp  - largura da janela no expoente (default 3)
        c_mul  - largura da janela dentro das multiplicações

    Registradores de trabalho:
        e      : n_exp    - expoente (input)
        acc    : n_bits+1 - acumulador / resultado
        tmp    : n_bits+1 - workspace (para multiplicações)
        anc    :     2    - ancillas (QROM)
    """
    ## tamanhos 
    n_bits = int(log2(N)) + 1                ## tamanho de N
    w_exp  = ceil(n_exp / c_exp)             ## nº de janelas no expoente

    ## registradores
    reg_e   = QuantumRegister(n_exp,   "e")      ## expoente
    acc     = QuantumRegister(n_bits + 1, "acc") ## acumulador
    tmp     = QuantumRegister(n_bits + 1, "tmp") ## workspace (sobra  |0>)
    anc     = QuantumRegister(2,         "anc")  ## ancillas QROM

    qc = QuantumCircuit(reg_e, acc, tmp, anc, name="expmodW")

    ## inicializa acumulador em 1  (|001…⟩)
    qc.x(acc[0])




    ## Percorre janelas do expoente:  menos significativo --> MSB
    for w in range(w_exp):
        lo  = w * c_exp
        hi  = min((w + 1) * c_exp, n_exp)
        width = hi - lo

        ### calcula k = base^(2^(lo)) (mod N)
        k_pow = pow(base, 1 << lo, N)   # base^(2^lo)  mod N

        ### tabela dos 2^width fatores
        factors = [ pow(k_pow, j, N) for j in range(1 << width) ]

        ### qubits da janela de expoente que indexam a lookup-multiplicação
        addr_exp = [reg_e[q] for q in range(lo, hi)]

        ###  multiplicação modular (acc *= factor)
        ###  multiplicação é NÃO-controlada, o controle se reflete
        ###  no lookup que devolve 1 quando a sub-janela vale 0.
        mul_gate = mult_mod_windowed(n_bits, 1, N, c_mul) 

        ###   Para cada possível valor da janela, precisamos multiplicar
        ###   o acumulador pela constante "factors[val]".
        ###   Fazemos isso como um cascade de lookups no estilo
        ###   “select-swap”. Pra clareza e simplicidade usei
        ###   multiplicações constantes controladas por "addr_exp".
        for val, const in enumerate(factors):
            if const == 1:
                continue                     
            const_mul = mult_mod_windowed(n_bits, const, N, c_mul)
            ### controles, todos os qubits de addr_exp em estado correspondente a "val"


            ### qubit auxiliar
            ctrl_aux = tmp[-1]
            ### argumentos esperados por const_mul
            wire_list = [ctrl_aux] + tmp[:-1] + acc[:] + anc[:]

            bin_val = [(val >> b) & 1 for b in range(width)]
            conds   = []
            for qb, bit in zip(addr_exp, bin_val):
                if bit == 0:
                    qc.x(qb)
                conds.append(qb)
            qc.mcx(conds, ctrl_aux)          ### usa tmp[-1] como controle auxiliar
            qc.append(const_mul, wire_list)
            qc.mcx(conds, ctrl_aux)
            qc.reset(ctrl_aux)
            for qb, bit in zip(addr_exp, bin_val):
                if bit == 0:
                    qc.x(qb)

    #resultado em |acc⟩
    return qc
