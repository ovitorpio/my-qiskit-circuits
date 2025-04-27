# mult_mod_windowed.py
#
# b  -->  (a * b)   (mod N)     -  "a", "N" clássicos
# Usa windowed-additions, janela c_mul bits do fator b.
#
from math import ceil
from qiskit import QuantumCircuit, QuantumRegister
from adder_plain import adder_n
from qrom import qrom



# função mult_mod_windowed cria um circuito que multiplica um numero quântico b por uma constante a, com módulo N, usando aritmética janelada (windowed arithmetic).

# Parâmetros:
#n_bits: número de qubits que representam o número b (o fator quântico).
#a: o valor clássico fixo que queremos multiplicar
#N: o módulo clássico da operação (trabalhamos mod N)
#c_mul: tamanho da janela de bits usada dentro da multiplicação 
#
#

def mult_mod_windowed(n_bits, a, N, c_mul=4):
    ctrl   = QuantumRegister(1,        "c")      ## Cria um registrador quântico de 1 qubit, chamado "c", que é usado para controle global do circuito
                                                 ##  se desejar versão controlada
                                                 
    reg_b  = QuantumRegister(n_bits,   "b")      ## fator quântico
                                                 ## Um registrador de n_bits qubits chamado "b" que guarda o número b que será multiplicado
                                                 ## Esse é o registrador de entrada principal.   


    acc    = QuantumRegister(n_bits+1, "acc")    ## Um registrador de n_bits + 1 qubits chamado "acc" onde o resultado da multiplicação vai se acumulando.
    anc    = QuantumRegister(2,        "anc")    ## Um registrador de 2 qubits chamado "anc", QROM ancillas
    
    ## aqui criamos o circuito com os registradores
    qc = QuantumCircuit(ctrl, reg_b, acc, anc, name=f"mulW{c_mul}")

    ### QFT acc
    from qiskit.circuit.library import QFT
    qc.append(QFT(n_bits+1, do_swaps=False), acc)

    windows = ceil(n_bits / c_mul)
    for w in range(windows):
        lo   = w * c_mul
        hi   = min((w+1)*c_mul, n_bits)
        size = 1 << (hi-lo)
        addr = [reg_b[q] for q in range(lo, hi)]

        ### tabela  (k * a * 2^lo) mod N
        tbl = [ (k * a * (1<<lo)) % N for k in range(size) ]

        ### LOOKUP  (⊕) valor --> acc
        lookup = qrom(tbl, n_bits+1)
        qc.append(lookup,        addr + acc[:] + anc[:])

        ### ADD  (acc += lookup) 

        ### UNLOOKUP (clean ancillas)
        qc.append(lookup.inverse(), addr + acc[:] + anc[:])

    ### IQFT
    qc.append(QFT(n_bits+1, do_swaps=False).inverse(), acc)
    return qc
