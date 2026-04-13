import sys
from abc import ABC, abstractmethod
import re

class Token():
    def __init__(self, type: str, value):
        """
            type: string. É o tipo do token
            value: integer | string. É o valor do token
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

    def get_value(self, variable):
        if variable in self.table.keys():
            return self.table[variable]
        else:
            raise Exception("[Semantic] Variable not defined: " + variable)

    def set_value(self, variable, value):
        self.table[variable] = value


RESERVED = {
    "print": "PRINT",
    "if": "IF",
    "else": "ELSE",
    "while": "WHILE",
    "read": "READ",
    "then": "OPEN_IF_BRA",
    "do": "OPEN_BRA",
    "end": "CLOSE_BRA",
    "and": "AND",
    "or": "OR",
    "not": "NOT",
}


class Lexer():
    def __init__(self, source: str, position: int, next: Token):
        self.source = source
        self.position = position
        self.next = next

    def select_next(self):
        while self.position < len(self.source):
            caracter = self.source[self.position]

            if caracter == ' ' or caracter == '\t':
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
                if variable_str in RESERVED:
                    self.next = Token(RESERVED[variable_str], variable_str)
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
                    if self.position + 1 < len(self.source) and self.source[self.position + 1] == '=':
                        self.next = Token("EQ", '==')
                        self.position += 2
                        return
                    self.next = Token("ASSIGN", '=')
                elif caracter == '<':
                    self.next = Token("LT", '<')
                elif caracter == '>':
                    self.next = Token("GT", '>')
                elif caracter == '\n':
                    self.next = Token("END", '\n')
                else:
                    raise Exception("[Lexer] Invalid character: " + caracter)
                self.position += 1
                return
        self.next = Token("EOF", "")


class Parser():
    lexer = None

    def parse_bool_expression():
        node = Parser.parse_bool_term()

        while Parser.lexer.next.type == "OR":
            Parser.lexer.select_next()
            right = Parser.parse_bool_term()
            node = BinOp("OR", [node, right])

        return node

    def parse_bool_term():
        node = Parser.parse_rel_expression()

        while Parser.lexer.next.type == "AND":
            Parser.lexer.select_next()
            right = Parser.parse_rel_expression()
            node = BinOp("AND", [node, right])

        return node

    def parse_rel_expression():
        node = Parser.parse_expression()

        if Parser.lexer.next.type in ("EQ", "GT", "LT"):
            op = Parser.lexer.next.type
            Parser.lexer.select_next()
            right = Parser.parse_expression()
            node = BinOp(op, [node, right])

        return node

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

        elif Parser.lexer.next.type in ("PLUS", "MINUS", "NOT"):
            op = Parser.lexer.next.type
            Parser.lexer.select_next()
            child = Parser.parse_factor()
            return UnOp(op, [child])

        elif Parser.lexer.next.type == "OPEN_PAR":
            Parser.lexer.select_next()

            expr = Parser.parse_bool_expression()

            if Parser.lexer.next.type != "CLOSE_PAR":
                raise Exception("[Parser] Unexpected token: " + Parser.lexer.next.type + ", expected CLOSE_PAR")

            Parser.lexer.select_next()
            return expr

        elif Parser.lexer.next.type == "IDEN":
            node = Identifier(Parser.lexer.next.value)
            Parser.lexer.select_next()
            return node

        elif Parser.lexer.next.type == "READ":
            Parser.lexer.select_next()
            if Parser.lexer.next.type != "OPEN_PAR":
                raise Exception("[Parser] Unexpected token: " + Parser.lexer.next.type + ", expected OPEN_PAR")
            Parser.lexer.select_next()
            if Parser.lexer.next.type != "CLOSE_PAR":
                raise Exception("[Parser] Unexpected token: " + Parser.lexer.next.type + ", expected CLOSE_PAR")
            Parser.lexer.select_next()
            return Read()

        else:
            raise Exception("[Parser] Unexpected token: " + Parser.lexer.next.type + ", expected INT, PLUS, MINUS, NOT, OPEN_PAR, IDEN or READ")

    def parse_block():
        statements = []
        while Parser.lexer.next.type not in ("ELSE", "CLOSE_BRA", "EOF"):
            statements.append(Parser.parse_statement())
        return Block(statements)

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
                node = Assignment([indent_node, Parser.parse_bool_expression()])
            else:
                raise Exception("[Parser] Unexpected token: " + Parser.lexer.next.type + ", expected ASSIGN")

        elif Parser.lexer.next.type == "PRINT":
            Parser.lexer.select_next()

            if Parser.lexer.next.type != "OPEN_PAR":
                raise Exception("[Parser] Unexpected token: " + Parser.lexer.next.type + ", expected OPEN_PAR")
            else:
                Parser.lexer.select_next()
                expr = Parser.parse_bool_expression()

            if Parser.lexer.next.type != "CLOSE_PAR":
                raise Exception("[Parser] Unexpected token: " + Parser.lexer.next.type + ", expected CLOSE_PAR")

            Parser.lexer.select_next()
            node = Print(expr)

        elif Parser.lexer.next.type == "IF":
            Parser.lexer.select_next()

            if Parser.lexer.next.type != "OPEN_PAR":
                raise Exception("[Parser] Unexpected token: " + Parser.lexer.next.type + ", expected OPEN_PAR")
            Parser.lexer.select_next()

            cond = Parser.parse_bool_expression()

            if Parser.lexer.next.type != "CLOSE_PAR":
                raise Exception("[Parser] Unexpected token: " + Parser.lexer.next.type + ", expected CLOSE_PAR")
            Parser.lexer.select_next()

            if Parser.lexer.next.type != "OPEN_IF_BRA":
                raise Exception("[Parser] Unexpected token: " + Parser.lexer.next.type + ", expected then")
            Parser.lexer.select_next()

            then_block = Parser.parse_block()

            if Parser.lexer.next.type == "ELSE":
                Parser.lexer.select_next()
                else_block = Parser.parse_block()

                if Parser.lexer.next.type != "CLOSE_BRA":
                    raise Exception("[Parser] Unexpected token: " + Parser.lexer.next.type + ", expected end")
                Parser.lexer.select_next()
                node = If([cond, then_block, else_block])
            else:
                if Parser.lexer.next.type != "CLOSE_BRA":
                    raise Exception("[Parser] Unexpected token: " + Parser.lexer.next.type + ", expected end")
                Parser.lexer.select_next()
                node = If([cond, then_block])

        elif Parser.lexer.next.type == "WHILE":
            Parser.lexer.select_next()

            if Parser.lexer.next.type != "OPEN_PAR":
                raise Exception("[Parser] Unexpected token: " + Parser.lexer.next.type + ", expected OPEN_PAR")
            Parser.lexer.select_next()

            cond = Parser.parse_bool_expression()

            if Parser.lexer.next.type != "CLOSE_PAR":
                raise Exception("[Parser] Unexpected token: " + Parser.lexer.next.type + ", expected CLOSE_PAR")
            Parser.lexer.select_next()

            if Parser.lexer.next.type != "OPEN_BRA":
                raise Exception("[Parser] Unexpected token: " + Parser.lexer.next.type + ", expected do")
            Parser.lexer.select_next()

            body = Parser.parse_block()

            if Parser.lexer.next.type != "CLOSE_BRA":
                raise Exception("[Parser] Unexpected token: " + Parser.lexer.next.type + ", expected end")
            Parser.lexer.select_next()
            node = While([cond, body])

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
    def __init__(self, value, children: list):
        self.value = value
        self.children = children

    @abstractmethod
    def evaluate(self, st: SymbolTable):
        pass


class BinOp(Node):
    def __init__(self, value: str, children):
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
        elif value == "AND":
            if left_value != 0 and right_value != 0:
                return 1
            else:
                return 0
        elif value == "OR":
            if left_value != 0 or right_value != 0:
                return 1
            else:
                return 0
        elif value == "EQ":
            if left_value == right_value:
                return 1
            else:
                return 0
        elif value == "GT":
            if left_value > right_value:
                return 1
            else:
                return 0
        elif value == "LT":
            if left_value < right_value:
                return 1
            else:
                return 0
        else:
            raise Exception("[Semantic] Invalid operator: " + value)


class UnOp(Node):
    def __init__(self, value: str, children):
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
        elif value == "NOT":
            if central_value == 0:
                return 1
            else:
                return 0
        else:
            raise Exception("[Semantic] Invalid operator: " + value)


class IntVal(Node):
    def __init__(self, value: int, children):
        super().__init__(value, [])

    def evaluate(self, st: SymbolTable):
        return int(self.value)


class Identifier(Node):
    def __init__(self, value: str, children=[]):
        super().__init__(value, children)

    def evaluate(self, st: SymbolTable):
        return st.get_value(self.value)


class Print(Node):
    def __init__(self, children, value=None):
        super().__init__(None, [children])

    def evaluate(self, st: SymbolTable):
        resultado = self.children[0].evaluate(st)
        print(resultado)


class Assignment(Node):
    def __init__(self, children, value=None):
        super().__init__(None, children)

    def evaluate(self, st: SymbolTable):
        nome_da_variavel = self.children[0].value
        resultado_da_expressao = self.children[1].evaluate(st)
        st.set_value(nome_da_variavel, resultado_da_expressao)


class Block(Node):
    def __init__(self, children, value=None):
        super().__init__(None, children)

    def evaluate(self, st: SymbolTable):
        for child in self.children:
            child.evaluate(st)


class If(Node):
    def __init__(self, children, value=None):
        super().__init__(None, children)

    def evaluate(self, st: SymbolTable):
        cond = self.children[0].evaluate(st)
        if cond != 0:
            self.children[1].evaluate(st)
        else:
            if len(self.children) == 3:
                self.children[2].evaluate(st)


class While(Node):
    def __init__(self, children, value=None):
        super().__init__(None, children)

    def evaluate(self, st: SymbolTable):
        while self.children[0].evaluate(st) != 0:
            self.children[1].evaluate(st)


class Read(Node):
    def __init__(self, value=None, children=None):
        super().__init__(None, [])

    def evaluate(self, st: SymbolTable):
        return int(input())


class NoOp(Node):
    def __init__(self, value=None, children=None):
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
