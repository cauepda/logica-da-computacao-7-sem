import sys
from abc import ABC, abstractmethod
import re

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


class PrePro():
    def filter(codigo_fonte):
        codigo_limpo = re.sub(r'--.*\n', '\n', codigo_fonte)
        return codigo_limpo

class Variable():
    def __init__(self, value: int):
        self.value = value
    

class SymbolTable():
    def __init__(self, table):
        self.table = table

    def get_value(self, variable: Variable):
        if variable in self.table.keys():
            return self.table[variable]
        else:
            raise Exception("[Semantic] Variable not defined: " + variable)

    def set_value(self, variable: Variable, value):
        self.table[variable] = value


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

            elif caracter.isalpha():
                variable_str = ""
                while self.position < len(self.source) and (self.source[self.position].isalpha() or self.source[self.position].isdigit() or self.source[self.position] == "_"):
                    variable_str += self.source[self.position]
                    self.position += 1
                if variable_str == "print":
                    self.next = Token("PRINT", variable_str)
                else:
                    self.next = Token("IDEN", variable_str)
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
                elif caracter == '=':
                    self.next = Token("ASSIGN", '=')
                elif caracter == '\n':
                    self.next = Token("END", '\n')
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
        
        elif Parser.lexer.next.type == "IDEN":
            node = Identifier(Parser.lexer.next.value)
            Parser.lexer.select_next()
            return node
        else:
            raise Exception("[Parser] Unexpected token: " + Parser.lexer.next.type + ", expected INT, PLUS, MINUS or OPEN_PAR")
        
    def parse_program():

        statements = []
        while Parser.lexer.next.type != "EOF":
            statements.append(Parser.parse_statement())

        return Block(statements)

        
    def parse_statement():
        if Parser.lexer.next.type == "IDEN":
            indent_node = Identifier(Parser.lexer.next.value)
            Parser.lexer.select_next()

            if Parser.lexer.next.type == "ASSIGN":
                Parser.lexer.select_next()
                node = Assignment([indent_node, Parser.parse_expression()])
            else:
                raise Exception("[Parser] Unexpected token: " + Parser.lexer.next.type + ", expected ASSIGN")
        
        elif Parser.lexer.next.type == "PRINT":
            Parser.lexer.select_next()

            if Parser.lexer.next.type != "OPEN_PAR":
                raise Exception("[Parser] Unexpected token: " + Parser.lexer.next.type + ", expected OPEN_PAR")
            else:
                Parser.lexer.select_next()
                expr = Parser.parse_expression()

            if Parser.lexer.next.type != "CLOSE_PAR":
                raise Exception("[Parser] Unexpected token: " + Parser.lexer.next.type + ", expected CLOSE_PAR")
                
            Parser.lexer.select_next()
            node = Print(expr)

        else:
            node = NoOp()

        if Parser.lexer.next.type != "END":
            raise Exception("[Parser] Unexpected token: " + Parser.lexer.next.type + ", expected END")
        else:
            Parser.lexer.select_next()
            return node
        
    def run(code: str):

        Parser.lexer = Lexer(code, 0, None)
        Parser.lexer.select_next()
        resultado = Parser.parse_program()

        if Parser.lexer.next.type != "EOF":
            raise Exception("[Parser] Unexpected token after expression: " + Parser.lexer.next.type)
        return resultado
    
class Node(ABC):
    def __init__(self, value: int | str, children: list):
        self.value = value
        self.children = children

    @abstractmethod
    def evaluate(self, st: SymbolTable):
        pass


class BinOp(Node):
    def __init__(self, value: str, children: Node):
        if len(children) != 2:
            raise Exception("[Semantic] BinOp must have exactly 2 children")
        super().__init__(value, children)
    
    def evaluate(self, st: SymbolTable):
        value = self.value
        left_value = self.children[0].evaluate(st)
        right_value = self.children[1].evaluate(st)

        if value == "PLUS":
             return left_value + right_value
        elif value == "MINUS":
            return left_value - right_value
        elif value == "MULT":
            return left_value * right_value
        elif value == "DIV":
            if right_value == 0:
                raise Exception("[Semantic] Division by zero")
            return left_value // right_value
        else:
            raise Exception("[Semantic] Invalid operator: " + value)
    
class UnOp(Node):
    def __init__(self, value: str, children: Node):
        if len(children) != 1:
            raise Exception("[Semantic] UnOp must have exactly 1 child")
        super().__init__(value, children)

    def evaluate(self, st: SymbolTable):
        value = self.value
        central_value = self.children[0].evaluate(st)

        if value == "PLUS":
            return central_value
        elif value == "MINUS":
            return -central_value
        else:
            raise Exception("[Semantic] Invalid operator: " + value)

    
class IntVal(Node):
    def __init__(self, value: int, children):
        super().__init__(value, [])
    
    def evaluate(self, st: SymbolTable):
        return int(self.value)
    

class Identifier(Node):
    def __init__(self, value: str, children = []):
        super().__init__(value, children)

    def evaluate(self, st: SymbolTable):
        return st.get_value(self.value)
    

class Print(Node):
    def __init__(self, children, value = None):
        super().__init__(None, [children])

    def evaluate(self, st: SymbolTable):
        resultado = self.children[0].evaluate(st)
        print(resultado)


class Assignment(Node):
    def __init__(self, children, value = None):
        super().__init__(None, children)

    def evaluate(self, st: SymbolTable):
        nome_da_variavel = self.children[0].value
        resultado_da_expressao = self.children[1].evaluate(st)
        st.set_value(nome_da_variavel, resultado_da_expressao)


class Block(Node):
    def __init__(self, children, value = None):
        super().__init__(None, children)

    def evaluate(self, st: SymbolTable):
        for child in self.children:
            child.evaluate(st)


class NoOp(Node):
    def __init__(self, value = None, children = None):
        super().__init__(value, children)

    def evaluate(self, st: SymbolTable):
        pass


if __name__ == "__main__":
    fil_name = sys.argv[1]
    with open(fil_name, "r") as f:
        code = f.read()
        code += "\n"
    codigo_limpo = PrePro.filter(code)

    dictionary = {}
    st = SymbolTable(dictionary)
    ast_root = Parser.run(codigo_limpo)
    resultado = ast_root.evaluate(st)    