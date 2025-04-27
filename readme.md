# Modular Exponentiation with Windowed Arithmetic (Qiskit)

Este projeto implementa uma versão otimizada da exponenciação modular \(x \mapsto \text{base}^x \bmod N\) utilizando windowed arithmetic trabalho de Gidney & Ekerå (2019). 

A técnica é aplicada em dois níveis:
- Windowing sobre o expoente (reduz o número de multiplicações modulares),
- Windowing dentro das multiplicações (reduz o número de somas modulares).

## Motivação

Em algoritmos como o de Shor a etapa de exponenciação modular é a parte mais custosa em termos de número de portas quânticas.  
Implementá-la de maneira mais eficiente é importante para reduzir o número de qubits e tempo de execução.

A abordagem tradicional (sem janela) faz uma multiplicação modular para cada bit do expoente, usando adições sequenciais que levam os circuitos a terem profundidade e T-count \(O(n^2)\).

Já com windowed arithmetic:
- Reduzimos o número de multiplicações em \(1/c_{\text{exp}}\),
- Reduzimos o número de somas dentro de cada multiplicação em \(1/c_{\text{mul}}\),
- E introduzimos apenas pequenas tabelas QROM para fazer os lookups.

Assim o custo total melhora para cerca de \(O(n^2/\log n)\) (dependendo da escolha das janelas).

## Arquivos

- `expmod_windowed.py` - implementação da exponenciação modular com duas janelas.
- `mult_mod_windowed.py` - multiplicador modular usando somas janeladas e QROM.
- `adder_plain.py` - adder quântico não-modular (baseado no adder de Cuccaro).
- `qrom.py` - implementação simplificada da técnica de unary iteration para leitura de tabelas (lookup).
- `test.py` - script para gerar um circuito de teste e simular no AerSimulator.

## Requisitos


Instale as dependências com:

```bash
pip install qiskit qiskit-aer matplotlib pylatexenc
```
# Como usar
- Clone o projeto e navegue até a pasta.
- Execute o arquivo test.py para gerar e simular um circuito de exponenciação modular.

Exemplo de parâmetros no test.py

```bash
N       = 15          # módulo
base    = 2           # base
n_e     = 4           # qubits do expoente
c_exp   = 2           # janela sobre o expoente
c_mul   = 2           # janela dentro das multiplicações
```

O script tem como saída:

- O número de qubits utilizados;
- A profundidade do circuito;

# Referências:

- Craig Gidney and Martin Ekerå, How to factor 2048 bit RSA integers in 8 hours using 20 million noisy qubits (2019). arXiv:1905.09749
- Ryan Babbush et al., Encoding Electronic Spectra in Quantum Circuits with Linear T Complexity (2018). arXiv:1805.03662
- Vlatko Vedral, Adriano Barenco, and Artur Ekert, Quantum networks for elementary arithmetic operations (1996).


