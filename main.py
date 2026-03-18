import sys
from abc import ABC, abstractmethod

class Token():
    def __init__(self, type: str, value: int | str):
        """
            type: string. É o tipo do token
            value: integer | string. É o valor do token
            (INT, 5) representa o número 5
            (PLUS, '+') representa o símbolo +
            (MINUS, '-') representa o símbolo -
            (EOF, '') representa o final da string de entrada
        """
        self.type = type
        self.value = value


class Lexer():
    def __init__(self, source: str, position: int, next: Token):
        """
            source: string. É o código-fonte que será tokenizado
            position: integer. É a posição atual que o Lexer está separando
            next: Token. É o último token separado
            select_next(): lê o próximo token e atualiza o atributo next
        """
        self.source = source
        self.position = position
        self.next = next

    def select_next(self):
        """
            1. realizará a tokenização
            2. irá quebrar o código fonte sob demanda, sempre analisando um caractere específico representado pelo índice position
            3. Ao achar um símbolo de interesse, irá parar e atualizar o atributo next com o token correspondente
            4. Ao ser chamada novamente, continuará a análise de onde parou (position atual).
            5. O método deverá ignorar os espaços em branco.
        """
        while self.position < len(self.source):
            caracter = self.source[self.position]

            if caracter == ' ':
                self.position += 1
                continue
            elif caracter.isdigit():
                num_str = ""
                while self.position < len(self.source) and self.source[self.position].isdigit():
                    num_str += self.source[self.position]
                    self.position += 1
                self.next = Token("INT", int(num_str))
                return
            else:
                if caracter == '+':
                    self.next = Token("PLUS", '+')
                elif caracter == '-':
                    self.next = Token("MINUS", '-')
                elif caracter == '*':
                    self.next = Token("MULT", '*')
                elif caracter == '/':
                    self.next = Token("DIV", '/')
                elif caracter == '(':
                    self.next = Token("OPEN_PAR", '(')
                elif caracter == ')':
                    self.next = Token("CLOSE_PAR", ')')
                else:
                    raise Exception("[Lexer] Invalid character: " + caracter)
                self.position += 1
                return
        self.next = Token("EOF", "")

class Parser():
    lexer = None

    def parse_expression():
        node = Parser.parse_term()

        while Parser.lexer.next.type in ("PLUS", "MINUS"):
            op = Parser.lexer.next.type
            Parser.lexer.select_next()

            next_term = Parser.parse_term()
            node = BinOp(op, [node, next_term])

        return node
    
    def parse_term():
        node = Parser.parse_factor()

        while Parser.lexer.next.type in ("MULT", "DIV"):
            op = Parser.lexer.next.type
            Parser.lexer.select_next()

            next_factor = Parser.parse_factor()
            node = BinOp(op, [node, next_factor])

        return node


    def parse_factor():
        if Parser.lexer.next.type == "INT":
            node = IntVal(Parser.lexer.next.value, [])
            Parser.lexer.select_next()
            return node

        elif Parser.lexer.next.type in ("PLUS", "MINUS"):
            op = Parser.lexer.next.type
            Parser.lexer.select_next()
            child = Parser.parse_factor()
            return UnOp(op, [child])

        
        elif Parser.lexer.next.type == "OPEN_PAR":
            Parser.lexer.select_next()

            expr = Parser.parse_expression()

            if Parser.lexer.next.type != "CLOSE_PAR":
                raise Exception("[Parser] Unexpected token: " + Parser.lexer.next.type + ", expected CLOSE_PAR")
                
            Parser.lexer.select_next()
            return expr
        else:
            raise Exception("[Parser] Unexpected token: " + Parser.lexer.next.type + ", expected INT, PLUS, MINUS or OPEN_PAR")

        
    def run(code: str):

        Parser.lexer = Lexer(code, 0, None)
        Parser.lexer.select_next()
        resultado = Parser.parse_expression()

        if Parser.lexer.next.type != "EOF":
            raise Exception("[Parser] Unexpected token after expression: " + Parser.lexer.next.type)
        return resultado
    
class Node(ABC):
    def __init__(self, value: int | str, children: list):
        self.value = value
        self.children = children

    @abstractmethod
    def evaluate(self):
        pass


class BinOp(Node):
    def __init__(self, value: str, children: Node):
        if len(children) != 2:
            raise Exception("[Semantic] BinOp must have exactly 2 children")
        super().__init__(value, children)
    
    def evaluate(self):
        value = self.value
        left_value = self.children[0].evaluate()
        right_value = self.children[1].evaluate()

        if value == "PLUS":
             return left_value + right_value
        elif value == "MINUS":
            return left_value - right_value
        elif value == "MULT":
            return left_value * right_value
        elif value == "DIV":
            return left_value // right_value
        else:
            raise Exception("[Semantic] Invalid operator: " + value)
    
class UnOp(Node):
    def __init__(self, value: str, children: Node):
        if len(children) != 1:
            raise Exception("[Semantic] UnOp must have exactly 1 child")
        super().__init__(value, children)

    def evaluate(self):
        value = self.value
        central_value = self.children[0].evaluate()

        if value == "PLUS":
            return central_value
        elif value == "MINUS":
            return -central_value
        else:
            raise Exception("[Semantic] Invalid operator: " + value)

    
class IntVal(Node):
    def __init__(self, value: int, children):
        super().__init__(value, [])
    
    def evaluate(self):
        return int(self.value)


if __name__ == "__main__":
    ast_root = Parser.run(sys.argv[1])
    resultado_final = ast_root.evaluate()
    print(resultado_final)