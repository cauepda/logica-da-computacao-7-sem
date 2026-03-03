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
                else:
                    raise Exception("Caractere invalido: " + caracter)
                self.position += 1
                return
        self.next = Token("EOF", "")

class Parser():
    lexer = None

    def parse_expression():
        if Parser.lexer.next.type != "INT":
            raise Exception("[Parser] Unexpected token: " + Parser.lexer.next.type + ", expected INT")
        resultado = Parser.lexer.next.value
        Parser.lexer.select_next()
        while Parser.lexer.next.type in ("PLUS", "MINUS"):
            op = Parser.lexer.next.type
            Parser.lexer.select_next()
            if Parser.lexer.next.type != "INT":
                raise Exception("[Parser] Unexpected token: " + Parser.lexer.next.type + ", expected INT")
            if op == "PLUS":
                resultado += Parser.lexer.next.value
            elif op == "MINUS":
                resultado -= Parser.lexer.next.value
            Parser.lexer.select_next()
        return resultado

    def run(code: str) -> int:
        Parser.lexer = Lexer(code, 0, None)
        Parser.lexer.select_next()
        resultado = Parser.parse_expression()
        if Parser.lexer.next.type != "EOF":
            raise Exception("[Parser] Unexpected token after expression: " + Parser.lexer.next.type)
        return resultado


if __name__ == "__main__":
    print(Parser.run("5 + 3 - 2"))