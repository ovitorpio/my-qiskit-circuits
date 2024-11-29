from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit.library import CDKMRippleCarryAdder
from mult_mod import mult_mod as mult_mod

n_bits = 3
x_bits = 2

# registradores necessarios para o circuito de exp modular
reg_x = QuantumRegister(x_bits, "x")

reg_a = QuantumRegister(n_bits, "a")

reg_n = QuantumRegister(n_bits, "n")

reg_op1 = QuantumRegister(n_bits, "op1")

reg_res1 = QuantumRegister(n_bits, "res1")

reg_op2 = QuantumRegister(n_bits, "op2")

reg_op3 = QuantumRegister(n_bits, "op3")

reg_res2 = QuantumRegister(n_bits, "res2")

reg_0_guarda = QuantumRegister(n_bits, "0g")

# registradores de suporte para a multiplicacao modular
reg_cin = QuantumRegister(1, "cin")

reg_cout = QuantumRegister(1, "cout")

reg_help = QuantumRegister(2, "help")

reg_0_op = QuantumRegister(2*n_bits, "0op")

reg_0_mod = QuantumRegister(n_bits, "0mod")

reg_01 = QuantumRegister(n_bits, "01")

reg_0_div = QuantumRegister(n_bits + 2, "0div")

reg_0_adder = QuantumRegister(2*n_bits, "0adder")

reg_zera_b = QuantumRegister(x_bits*n_bits)

# registrador classico para o resultado (mesmo que não seja testável)
reg_result = ClassicalRegister(n_bits, "resultado")

circuito = QuantumCircuit(reg_x, reg_a, reg_01, reg_cin, reg_0_adder, reg_0_div, reg_n, reg_op1, reg_cout, reg_help, reg_0_op, reg_res1, reg_op2, reg_op3, reg_res2, reg_0_guarda, reg_zera_b)

for i in range(x_bits):
    if i > 0:
        circuito.cx(reg_help[1], reg_op1[0], ctrl_state="0")
        for j in range(n_bits):
            circuito.cx(reg_a[j], reg_op1[j])
    circuito.append(mult_mod(n_bits), reg_a[:] + reg_01[:] + reg_cin[:] + reg_0_adder[:] + reg_0_div[:] + reg_op1[:] + reg_cout[:] + reg_help[:] + reg_n[:] + reg_0_op[:] + reg_res1[:])
    circuito.cx(reg_x[i], reg_op2[0])
    for j in range(n_bits):
        circuito.ccx(reg_x[i], reg_res1[j], reg_op2[j])
    if i > 0:
        circuito.cx(reg_op3[j], reg_zera_b[i])
        circuito.cx(reg_zera_b[i], reg_op3[j])
    circuito.append(mult_mod(n_bits), reg_op2[:] + reg_01[:] + reg_cin[:] + reg_0_adder[:] + reg_0_div[:] + reg_op3[:] + reg_cout[:] + reg_help[:] + reg_n[:] + reg_0_op[:] + reg_res2[:])
    for j in range(n_bits):
        circuito.cx(reg_res2[j], reg_0_guarda[j])
    circuito.append(mult_mod(n_bits).inverse(), reg_op2[:] + reg_01[:] + reg_cin[:] + reg_0_adder[:] + reg_0_div[:] + reg_op3[:] + reg_cout[:] + reg_help[:] + reg_n[:] + reg_0_op[:] + reg_res2[:])
    for j in range(n_bits):
        circuito.cx(reg_0_guarda[j], reg_op3[j])
        circuito.cx(reg_op3[j], reg_0_guarda[j])
    circuito.cx(reg_x[i], reg_op2[0])
    for j in range(n_bits):
        circuito.ccx(reg_x[i], reg_res1[j], reg_op2[j])


print(circuito) 
#circuito.draw("mpl") : utilizar se for possivel desenhar
