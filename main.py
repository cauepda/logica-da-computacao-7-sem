import sys

def main():
    if len(sys.argv) < 2:
        raise ValueError("Nenhuma expressao fornecida.")
    
    expr = sys.argv[1].split()
    
    if not expr:
        raise ValueError("Expressao nao comeca com um numero.")
    
    try:
        resultado_atual = int(expr[0])
    except ValueError:
        raise ValueError("Expressao nao comeca com um numero.")
    
    leu_algum_operador = False
    i = 1
    
    while i < len(expr):
        if i >= len(expr):
            break
        
        op = expr[i]
        leu_algum_operador = True
        
        if i + 1 >= len(expr):
            raise ValueError("Faltando numero apos operador.")
        
        try:
            proximo_n = int(expr[i + 1])
        except ValueError:
            raise ValueError("Faltando numero apos operador.")
        
        if op == '+':
            resultado_atual += proximo_n
        elif op == '-':
            resultado_atual -= proximo_n
        else:
            raise ValueError(f"Operador não reconhecido: {op}")
        
        i += 2
    
    if not leu_algum_operador:
        raise ValueError("Expressao incompleta (sem operador).")
    
    print(resultado_atual)

if __name__ == "__main__":
    main()
