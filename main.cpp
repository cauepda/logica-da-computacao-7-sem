#include <sstream>
#include <iostream>
#include <string>

// int argc   : Argument Count
// char *argv : Argument Vector

int main(int argc, char *argv[]) {
    std::istringstream ss(argv[1]);

    int resultado_atual;
    char op;
    int proximo_n;

    if (!(ss >> resultado_atual)) {
        throw std::invalid_argument("Expressao nao comeca com um numero.");
        return 1;
    }
    
    while (ss >> op >> proximo_n) {
        if (op == '+') {
            resultado_atual += proximo_n;
        }
        else if (op == '-') {
            resultado_atual -= proximo_n;
        }
        else {
            std::cerr << "Erro de sintaxe: Operador '" << op << "' não reconhecido.\n";
            return 1;
        }
    }

    std::cout << "O resultado de '" << argv[1] << "' é: " << resultado_atual << "\n";
    return 0;
}