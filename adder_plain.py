# adder_plain.py
# Cuccaro ripple-carry não-modular, |b⟩ --> |b + const⟩
from qiskit import QuantumCircuit, QuantumRegister

def adder_n(n_bits, const):
    """Adder XOR-in-place (Cuccaro 2004) - Toffoli ~ 2*n_bits"""
    a = QuantumRegister(n_bits, "b")
    cin = QuantumRegister(1,     "cin")   ### carry-in/out (extra qubit)
    qc = QuantumCircuit(a, cin, name=f"add{const}")

    ### Propagate
    for i in range(n_bits-1):
        qc.ccx(a[i], cin[0], a[i+1])
        qc.cx(a[i], cin[0])
    ### Add constant bits
    for i in range(n_bits):
        if (const >> i) & 1:
            qc.cx(cin[0], a[i])
    ### Un-propagate
    for i in reversed(range(n_bits-1)):
        qc.cx(a[i], cin[0])
        qc.ccx(a[i], cin[0], a[i+1])
    return qc
