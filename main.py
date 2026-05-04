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
    def __init__(self, value, type: str, shift=0):
        self.value = value
        self.type = type
        self.shift = shift


class SymbolTable():
    def __init__(self, table):
        self.table = table
        self.shift_total = 0  # quantos bytes ja foram alocados na pilha

    def get_value(self, variable):
        if variable in self.table.keys():
            return self.table[variable]
        else:
            raise Exception("[Semantic] Variable not defined: " + variable)

    def set_value(self, variable, value):
        if variable not in self.table.keys():
            raise Exception("[Semantic] Variable not declared: " + variable)
        variavel_existente = self.table[variable]
        if variavel_existente.type != value.type:
            raise Exception("[Semantic] Type mismatch on assignment of " + variable + ": expected " + variavel_existente.type + ", got " + value.type)
        # mantem o shift original que ja foi atribuido na criacao
        value.shift = variavel_existente.shift
        self.table[variable] = value

    def create_variable(self, variable, value):
        if variable in self.table.keys():
            raise Exception("[Semantic] Variable already declared: " + variable)
        self.shift_total += 4
        value.shift = self.shift_total
        self.table[variable] = value


class Code():
    instructions = []

    def append(code: str):
        Code.instructions.append(code)

    def dump(filename: str):
        cabecalho = (
            'section .data\n'
            '  format_out: db "%d", 10, 0 ; format do printf\n'
            '  format_in: db "%d", 0 ; format do scanf\n'
            '  scan_int: dd 0 ; 32-bits integer\n'
            '\n'
            'section .text\n'
            '\n'
            '  extern printf ; usar _printf para Windows\n'
            '  extern scanf ; usar _scanf para Windows\n'
            '  ; extern _ExitProcess@4 ; usar para Windows\n'
            '  global _start ; inicio do programa\n'
            '\n'
            '_start:\n'
            '  push ebp ; guarda o EBP\n'
            '  mov ebp, esp ; zera a pilha\n'
            '\n'
            '  ; aqui comeca o codigo gerado:\n'
            '\n'
        )
        rodape = (
            '\n'
            '  ; aqui termina o codigo gerado\n'
            '\n'
            '  mov esp, ebp ; reestabelece a pilha\n'
            '  pop ebp\n'
            '\n'
            '  ; chamada da interrupcao de saida (Linux)\n'
            '  mov eax, 1\n'
            '  xor ebx, ebx\n'
            '  int 0x80\n'
            '  ; Para Windows:\n'
            '  ; push dword 0\n'
            '  ; call _ExitProcess@4\n'
        )
        with open(filename, 'w') as file:
            file.write(cabecalho)
            file.write("\n".join(Code.instructions))
            file.write(rodape)


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
    "local": "VAR",
    "true": "BOOL",
    "false": "BOOL",
    "string": "TYPE",
    "number": "TYPE",
    "boolean": "TYPE",
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

            elif caracter == '"':
                self.position += 1
                string_str = ""
                while self.position < len(self.source) and self.source[self.position] != '"':
                    string_str += self.source[self.position]
                    self.position += 1
                if self.position >= len(self.source):
                    raise Exception("[Lexer] Unterminated string literal")
                self.position += 1
                self.next = Token("STR", string_str)
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
                elif caracter == '.':
                    if self.position + 1 < len(self.source) and self.source[self.position + 1] == '.':
                        self.next = Token("CONCAT", '..')
                        self.position += 2
                        return
                    raise Exception("[Lexer] Invalid character: " + caracter)
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

        while Parser.lexer.next.type in ("PLUS", "MINUS", "CONCAT"):
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

        elif Parser.lexer.next.type == "STR":
            node = StringVal(Parser.lexer.next.value, [])
            Parser.lexer.select_next()
            return node

        elif Parser.lexer.next.type == "BOOL":
            valor_bool = True if Parser.lexer.next.value == "true" else False
            node = BoolVal(valor_bool, [])
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
            raise Exception("[Parser] Unexpected token: " + Parser.lexer.next.type + ", expected INT, STR, BOOL, PLUS, MINUS, NOT, OPEN_PAR, IDEN or READ")

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

        elif Parser.lexer.next.type == "OPEN_BRA":
            Parser.lexer.select_next()
            node = Parser.parse_block()
            if Parser.lexer.next.type != "CLOSE_BRA":
                raise Exception("[Parser] Unexpected token: " + Parser.lexer.next.type + ", expected end")
            Parser.lexer.select_next()

        elif Parser.lexer.next.type == "VAR":
            Parser.lexer.select_next()

            if Parser.lexer.next.type != "IDEN":
                raise Exception("[Parser] Unexpected token: " + Parser.lexer.next.type + ", expected IDEN")
            iden_node = Identifier(Parser.lexer.next.value)
            Parser.lexer.select_next()

            if Parser.lexer.next.type != "TYPE":
                raise Exception("[Parser] Unexpected token: " + Parser.lexer.next.type + ", expected TYPE")
            tipo_variavel = Parser.lexer.next.value
            Parser.lexer.select_next()

            if Parser.lexer.next.type == "ASSIGN":
                Parser.lexer.select_next()
                expr = Parser.parse_bool_expression()
                node = VarDec(tipo_variavel, [iden_node, expr])
            else:
                node = VarDec(tipo_variavel, [iden_node])

        else:
            node = NoOp()

        # consome o END (newline) se tiver, ou aceita um terminador de bloco
        if Parser.lexer.next.type == "END":
            Parser.lexer.select_next()
        elif Parser.lexer.next.type not in ("CLOSE_BRA", "EOF", "ELSE"):
            raise Exception("[Parser] Unexpected token: " + Parser.lexer.next.type + ", expected END")
        return node

    def run(code: str):

        Parser.lexer = Lexer(code, 0, None)
        Parser.lexer.select_next()
        resultado = Parser.parse_program()

        if Parser.lexer.next.type != "EOF":
            raise Exception("[Parser] Unexpected token after expression: " + Parser.lexer.next.type)
        return resultado


class Node(ABC):
    id = 0

    def new_id():
        Node.id += 1
        return Node.id

    def __init__(self, value, children: list):
        self.value = value
        self.children = children
        self.id = Node.new_id()

    @abstractmethod
    def evaluate(self, st: SymbolTable):
        pass

    def generate(self, st: SymbolTable):
        pass


class BinOp(Node):
    def __init__(self, value: str, children):
        if len(children) != 2:
            raise Exception("[Semantic] BinOp must have exactly 2 children")
        super().__init__(value, children)

    def evaluate(self, st: SymbolTable):
        value = self.value
        left = self.children[0].evaluate(st)
        right = self.children[1].evaluate(st)

        if value == "PLUS":
            if left.type != "number" or right.type != "number":
                raise Exception("[Semantic] PLUS requires number operands, got " + left.type + " and " + right.type)
            return Variable(left.value + right.value, "number")
        elif value == "MINUS":
            if left.type != "number" or right.type != "number":
                raise Exception("[Semantic] MINUS requires number operands, got " + left.type + " and " + right.type)
            return Variable(left.value - right.value, "number")
        elif value == "MULT":
            if left.type != "number" or right.type != "number":
                raise Exception("[Semantic] MULT requires number operands, got " + left.type + " and " + right.type)
            return Variable(left.value * right.value, "number")
        elif value == "DIV":
            if left.type != "number" or right.type != "number":
                raise Exception("[Semantic] DIV requires number operands, got " + left.type + " and " + right.type)
            if right.value == 0:
                raise Exception("[Semantic] Division by zero")
            return Variable(left.value // right.value, "number")
        elif value == "CONCAT":
            if left.type == "string":
                left_str = left.value
            elif left.type == "number":
                left_str = str(left.value)
            elif left.type == "boolean":
                left_str = "true" if left.value else "false"
            else:
                raise Exception("[Semantic] CONCAT invalid left operand type: " + left.type)
            if right.type == "string":
                right_str = right.value
            elif right.type == "number":
                right_str = str(right.value)
            elif right.type == "boolean":
                right_str = "true" if right.value else "false"
            else:
                raise Exception("[Semantic] CONCAT invalid right operand type: " + right.type)
            return Variable(left_str + right_str, "string")
        elif value == "AND":
            if left.type != "boolean" or right.type != "boolean":
                raise Exception("[Semantic] AND requires boolean operands, got " + left.type + " and " + right.type)
            return Variable(left.value and right.value, "boolean")
        elif value == "OR":
            if left.type != "boolean" or right.type != "boolean":
                raise Exception("[Semantic] OR requires boolean operands, got " + left.type + " and " + right.type)
            return Variable(left.value or right.value, "boolean")
        elif value == "EQ":
            if left.type != right.type:
                raise Exception("[Semantic] EQ requires operands of the same type, got " + left.type + " and " + right.type)
            return Variable(left.value == right.value, "boolean")
        elif value == "GT":
            if left.type != right.type:
                raise Exception("[Semantic] GT requires operands of the same type, got " + left.type + " and " + right.type)
            return Variable(left.value > right.value, "boolean")
        elif value == "LT":
            if left.type != right.type:
                raise Exception("[Semantic] LT requires operands of the same type, got " + left.type + " and " + right.type)
            return Variable(left.value < right.value, "boolean")
        else:
            raise Exception("[Semantic] Invalid operator: " + value)

    def generate(self, st: SymbolTable):
        # avalia o lado direito primeiro e empilha
        self.children[1].generate(st)
        Code.append("  push eax")
        # avalia o lado esquerdo (resultado em EAX)
        self.children[0].generate(st)
        Code.append("  pop ecx")

        if self.value == "PLUS":
            Code.append("  add eax, ecx")
        elif self.value == "MINUS":
            Code.append("  sub eax, ecx")
        elif self.value == "MULT":
            Code.append("  imul ecx")
        elif self.value == "DIV":
            Code.append("  cdq")
            Code.append("  idiv ecx")
        elif self.value == "AND":
            Code.append("  and eax, ecx")
        elif self.value == "OR":
            Code.append("  or eax, ecx")
        elif self.value == "EQ":
            Code.append("  cmp eax, ecx")
            Code.append("  mov eax, 0")
            Code.append("  mov ecx, 1")
            Code.append("  cmove eax, ecx")
        elif self.value == "LT":
            Code.append("  cmp eax, ecx")
            Code.append("  mov eax, 0")
            Code.append("  mov ecx, 1")
            Code.append("  cmovl eax, ecx")
        elif self.value == "GT":
            Code.append("  cmp eax, ecx")
            Code.append("  mov eax, 0")
            Code.append("  mov ecx, 1")
            Code.append("  cmovg eax, ecx")
        # CONCAT nao gera codigo (strings)


class UnOp(Node):
    def __init__(self, value: str, children):
        if len(children) != 1:
            raise Exception("[Semantic] UnOp must have exactly 1 child")
        super().__init__(value, children)

    def evaluate(self, st: SymbolTable):
        value = self.value
        central = self.children[0].evaluate(st)

        if value == "PLUS":
            if central.type != "number":
                raise Exception("[Semantic] Unary PLUS requires a number operand, got " + central.type)
            return Variable(central.value, "number")
        elif value == "MINUS":
            if central.type != "number":
                raise Exception("[Semantic] Unary MINUS requires a number operand, got " + central.type)
            return Variable(-central.value, "number")
        elif value == "NOT":
            if central.type != "boolean":
                raise Exception("[Semantic] NOT requires a boolean operand, got " + central.type)
            return Variable(not central.value, "boolean")
        else:
            raise Exception("[Semantic] Invalid operator: " + value)

    def generate(self, st: SymbolTable):
        self.children[0].generate(st)
        if self.value == "PLUS":
            # nao precisa fazer nada
            pass
        elif self.value == "MINUS":
            Code.append("  neg eax")
        elif self.value == "NOT":
            Code.append("  xor eax, 1")


class IntVal(Node):
    def __init__(self, value: int, children):
        super().__init__(value, [])

    def evaluate(self, st: SymbolTable):
        return Variable(int(self.value), "number")

    def generate(self, st: SymbolTable):
        Code.append("  mov eax, " + str(self.value))


class BoolVal(Node):
    def __init__(self, value: bool, children):
        super().__init__(value, [])

    def evaluate(self, st: SymbolTable):
        return Variable(bool(self.value), "boolean")

    def generate(self, st: SymbolTable):
        valor_int = 1 if self.value else 0
        Code.append("  mov eax, " + str(valor_int))


class StringVal(Node):
    def __init__(self, value: str, children):
        super().__init__(value, [])

    def evaluate(self, st: SymbolTable):
        return Variable(str(self.value), "string")

    def generate(self, st: SymbolTable):
        # nao gera codigo para strings
        pass


class Identifier(Node):
    def __init__(self, value: str, children=[]):
        super().__init__(value, children)

    def evaluate(self, st: SymbolTable):
        return st.get_value(self.value)

    def generate(self, st: SymbolTable):
        var = st.get_value(self.value)
        Code.append("  mov eax, [ebp-" + str(var.shift) + "] ; recupera " + self.value)


class Print(Node):
    def __init__(self, children, value=None):
        super().__init__(None, [children])

    def evaluate(self, st: SymbolTable):
        resultado = self.children[0].evaluate(st)
        if resultado.type == "boolean":
            if resultado.value:
                print("true")
            else:
                print("false")
        else:
            print(resultado.value)

    def generate(self, st: SymbolTable):
        self.children[0].generate(st)
        Code.append("  push eax")
        Code.append("  push format_out")
        Code.append("  call printf")
        Code.append("  add esp, 8")


class Assignment(Node):
    def __init__(self, children, value=None):
        super().__init__(None, children)

    def evaluate(self, st: SymbolTable):
        nome_da_variavel = self.children[0].value
        resultado_da_expressao = self.children[1].evaluate(st)
        st.set_value(nome_da_variavel, resultado_da_expressao)

    def generate(self, st: SymbolTable):
        nome_da_variavel = self.children[0].value
        var = st.get_value(nome_da_variavel)
        # gera o codigo da expressao primeiro (resultado em EAX)
        self.children[1].generate(st)
        Code.append("  mov [ebp-" + str(var.shift) + "], eax ; " + nome_da_variavel + " =")


class VarDec(Node):
    def __init__(self, value: str, children):
        super().__init__(value, children)

    def evaluate(self, st: SymbolTable):
        nome_da_variavel = self.children[0].value
        tipo_declarado = self.value

        if len(self.children) == 2:
            resultado = self.children[1].evaluate(st)
            if resultado.type != tipo_declarado:
                raise Exception("[Semantic] Type mismatch on declaration of " + nome_da_variavel + ": expected " + tipo_declarado + ", got " + resultado.type)
            st.create_variable(nome_da_variavel, resultado)
        else:
            if tipo_declarado == "number":
                valor_padrao = Variable(0, "number")
            elif tipo_declarado == "string":
                valor_padrao = Variable("", "string")
            elif tipo_declarado == "boolean":
                valor_padrao = Variable(False, "boolean")
            else:
                raise Exception("[Semantic] Unknown type: " + tipo_declarado)
            st.create_variable(nome_da_variavel, valor_padrao)

    def generate(self, st: SymbolTable):
        nome_da_variavel = self.children[0].value
        tipo_declarado = self.value

        # cria a variavel na tabela com valor padrao
        if tipo_declarado == "number":
            nova_var = Variable(0, "number")
        elif tipo_declarado == "boolean":
            nova_var = Variable(False, "boolean")
        else:
            nova_var = Variable("", "string")
        st.create_variable(nome_da_variavel, nova_var)

        # nao gera espaco na pilha pra string
        if tipo_declarado == "string":
            return

        Code.append("  sub esp, 4 ; var " + nome_da_variavel + " [EBP-" + str(nova_var.shift) + "]")

        # se tiver inicializacao, gera o codigo da expressao e atribui
        if len(self.children) == 2:
            self.children[1].generate(st)
            Code.append("  mov [ebp-" + str(nova_var.shift) + "], eax ; " + nome_da_variavel + " =")


class Block(Node):
    def __init__(self, children, value=None):
        super().__init__(None, children)

    def evaluate(self, st: SymbolTable):
        for child in self.children:
            child.evaluate(st)

    def generate(self, st: SymbolTable):
        for child in self.children:
            child.generate(st)


class If(Node):
    def __init__(self, children, value=None):
        super().__init__(None, children)

    def evaluate(self, st: SymbolTable):
        cond = self.children[0].evaluate(st)
        if cond.type != "boolean":
            raise Exception("[Semantic] IF condition must be boolean, got " + cond.type)
        if cond.value:
            self.children[1].evaluate(st)
        else:
            if len(self.children) == 3:
                self.children[2].evaluate(st)

    def generate(self, st: SymbolTable):
        meu_id = str(self.id)
        # avalia a condicao
        self.children[0].generate(st)
        Code.append("  cmp eax, 0")

        if len(self.children) == 3:
            # tem else
            Code.append("  je else_" + meu_id)
            self.children[1].generate(st)
            Code.append("  jmp end_" + meu_id)
            Code.append("else_" + meu_id + ":")
            self.children[2].generate(st)
            Code.append("end_" + meu_id + ":")
        else:
            Code.append("  je end_" + meu_id)
            self.children[1].generate(st)
            Code.append("end_" + meu_id + ":")


class While(Node):
    def __init__(self, children, value=None):
        super().__init__(None, children)

    def evaluate(self, st: SymbolTable):
        cond = self.children[0].evaluate(st)
        if cond.type != "boolean":
            raise Exception("[Semantic] WHILE condition must be boolean, got " + cond.type)
        while cond.value:
            self.children[1].evaluate(st)
            cond = self.children[0].evaluate(st)
            if cond.type != "boolean":
                raise Exception("[Semantic] WHILE condition must be boolean, got " + cond.type)

    def generate(self, st: SymbolTable):
        meu_id = str(self.id)
        Code.append("loop_" + meu_id + ":")
        # avalia a condicao
        self.children[0].generate(st)
        Code.append("  cmp eax, 0")
        Code.append("  je exit_" + meu_id)
        # corpo do loop
        self.children[1].generate(st)
        Code.append("  jmp loop_" + meu_id)
        Code.append("exit_" + meu_id + ":")


class Read(Node):
    def __init__(self, value=None, children=None):
        super().__init__(None, [])

    def evaluate(self, st: SymbolTable):
        return Variable(int(input()), "number")

    def generate(self, st: SymbolTable):
        Code.append("  push scan_int")
        Code.append("  push format_in")
        Code.append("  call scanf")
        Code.append("  add esp, 8")
        Code.append("  mov eax, dword [scan_int]")


class NoOp(Node):
    def __init__(self, value=None, children=None):
        super().__init__(value, children)

    def evaluate(self, st: SymbolTable):
        pass

    def generate(self, st: SymbolTable):
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
    ast_root.generate(st)

    # nome do arquivo de saida usa o mesmo prefixo
    nome_saida = fil_name.rsplit(".", 1)[0] + ".asm"
    Code.dump(nome_saida)
