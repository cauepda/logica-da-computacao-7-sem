#include <sstream>
#include <iostream>
#include <string>
#include <stdexcept>

// int argc   : Argument Count
// char *argv : Argument Vector

int main(int argc, char *argv[]) {
    if (argc < 2) {
        throw std::invalid_argument("Nenhuma expressao fornecida.");
    }

    std::istringstream ss(argv[1]);

    int resultado_atual;
    if (!(ss >> resultado_atual)) {
        throw std::invalid_argument("Expressao nao comeca com um numero.");
        return 1;
    }


    char op;
    int proximo_n;
    bool leu_algum_operador = false;

    while (true) {
        if (ss >> op) {
            break;
        }
        leu_algum_operador = true;

        if (!(ss >> proximo_n)) {
            throw std::invalid_argument("Faltando numero apos operador.");
        }

        if (op == '+') {
            resultado_atual += proximo_n;
        }
        else if (op == '-') {
            resultado_atual -= proximo_n;
        }
        else {
            throw std::invalid_argument(std::string("Operador não reconhecido: ") + op);
        }
    }

    if (!ss.eof() && !ss.fail()) {
         throw std::invalid_argument("Expressao mal formatada no final.");
    }
    if (!leu_algum_operador) {
        throw std::invalid_argument("Expressao incompleta (sem operador).");
    }
    std::cout << resultado_atual << "\n";
    return 0;
}