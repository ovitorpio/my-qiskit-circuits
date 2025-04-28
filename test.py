## #test.py
from qiskit import QuantumCircuit, ClassicalRegister, transpile
from qiskit_aer import AerSimulator
from expmod_windowed import expmod_windowed

### parâmetros da exponenciação
N       = 15          ## módulo
base    = 2           ## base
n_e     = 4           ## nº de qubits do expoente
c_exp   = 2           ## janela sobre o expoente
c_mul   = 2           ## janela dentro das multiplicações

## #gera o circuito unitário 
circ = expmod_windowed(N, base, n_e, c_exp, c_mul)

## #acrescenta medições em TODOS os qubits
creg = ClassicalRegister(circ.num_qubits, "meas")
circ.add_register(creg)
circ.measure(range(circ.num_qubits), range(circ.num_clbits))


## #simulacao 
backend = AerSimulator()
tcirc    = transpile(circ, backend)
result   = backend.run(tcirc).result()
counts   = result.get_counts()

print("Total de qubits :", circ.num_qubits)
print("Profundidade (after decompose):", circ.decompose().depth())
print("Counts (amostrados) :", counts)
print(circ.draw(output='text'))
