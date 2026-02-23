import sys

if len(sys.argv) < 2:
    raise Exception("Nenhuma expressao fornecida")

expression = sys.argv[1]

i = 0
n = len(expression)

# Ignora espacos iniciais
while i < n and expression[i] == ' ':
    i += 1

# Primeiro token tem que ser um numero
if i >= n or not expression[i].isdigit():
    raise Exception("Expressao invalida")

# Le o primeiro numero
num_str = ""
while i < n and expression[i].isdigit():
    num_str += expression[i]
    i += 1

resultado = int(num_str)

# Ignora espacos
while i < n and expression[i] == ' ':
    i += 1

# Le pares de (operador, numero) ate acabar a expressao
while i < n:
    # Le o operador
    if expression[i] not in ['+', '-']:
        raise Exception("Caractere invalido: " + expression[i])

    operador = expression[i]
    i += 1

    # Ignora espacos
    while i < n and expression[i] == ' ':
        i += 1

    # Apos o operador tem que vir um numero
    if i >= n or not expression[i].isdigit():
        raise Exception("Esperado numero apos operador")

    num_str = ""
    while i < n and expression[i].isdigit():
        num_str += expression[i]
        i += 1

    numero = int(num_str)

    if operador == '+':
        resultado += numero
    elif operador == '-':
        resultado -= numero

    # Ignora espacos
    while i < n and expression[i] == ' ':
        i += 1

print(resultado)
