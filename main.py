# Gabriel Coradin Cordeiro
# Gustavo Coradin Guadagnin
import sys


ESTADO_INICIAL = 'INICIAL'
ESTADO_LENDO_NUMERO = 'LENDO_NUMERO'
ESTADO_LENDO_PROPOSICAO = 'LENDO_PROPOSICAO'
ESTADO_LENDO_COMANDO = 'LENDO_COMANDO'
ESTADO_LENDO_PALAVRA = 'LENDO_PALAVRA'

class Token:
    def __init__(self, tipo, valor):
        self.tipo = tipo
        self.valor = valor

    def __str__(self):
        return f'Token({self.tipo}, {self.valor})'

class Lexer:
    def __init__(self, texto):
        self.texto = texto
        self.pos = 0
        self.char_atual = self.texto[0] if texto else None
        self.estado = ESTADO_INICIAL

    def avancar(self):
        self.pos += 1
        if self.pos >= len(self.texto):
            self.char_atual = None
        else:
            self.char_atual = self.texto[self.pos]

    def pular_espacos(self):
        while self.char_atual and self.char_atual.isspace():
            self.avancar()

    def ler_comando_latex(self):
        self.estado = ESTADO_LENDO_COMANDO
        comando = '\\'
        self.avancar()
        
        while self.char_atual and self.char_atual.isalpha():
            comando += self.char_atual
            self.avancar()

        self.estado = ESTADO_INICIAL
        if comando == '\\neg':
            return Token('OPERADORUNARIO', comando)
        elif comando in ['\\wedge', '\\vee', '\\rightarrow', '\\leftrightarrow']:
            return Token('OPERADORBINARIO', comando)
        else:
            raise ValueError(f'Comando LaTeX inválido: {comando}')

    def ler_proposicao(self):
        self.estado = ESTADO_LENDO_NUMERO
        numero = ''
        while self.char_atual and self.char_atual.isdigit():
            numero += self.char_atual
            self.avancar()
        
        self.estado = ESTADO_LENDO_PROPOSICAO    
        identificador = numero
        while self.char_atual and (self.char_atual.isdigit() or self.char_atual.islower()):
            identificador += self.char_atual
            self.avancar()
        
        self.estado = ESTADO_INICIAL
        return Token('PROPOSICAO', identificador)

    def ler_palavra(self):
        self.estado = ESTADO_LENDO_PALAVRA
        palavra = ''
        while self.char_atual and self.char_atual.isalpha():
            palavra += self.char_atual
            self.avancar()
        
        self.estado = ESTADO_INICIAL
        if palavra in ['true', 'false']:
            return Token('CONSTANTE', palavra)
        raise ValueError(f'Palavra inválida: {palavra}')

    def get_next_token(self):
        while self.char_atual is not None:
            if self.char_atual.isspace():
                self.pular_espacos()
                continue

            self.estado = ESTADO_INICIAL
            
            if self.char_atual == '(':
                self.avancar()
                return Token('ABREPAREN', '(')

            if self.char_atual == ')':
                self.avancar()
                return Token('FECHAPAREN', ')')

            if self.char_atual == '\\':
                return self.ler_comando_latex()

            if self.char_atual.isdigit():
                return self.ler_proposicao()

            if self.char_atual.isalpha():
                return self.ler_palavra()

            raise ValueError(f'Caractere inválido: {self.char_atual}')

        return Token('EOF', None)

    def get_estado_atual(self):
        return self.estado

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.token_atual = self.lexer.get_next_token()

    def erro(self, mensagem=""):
        raise Exception(f'Erro de sintaxe: {mensagem}')

    def consumir(self, tipo_token):
        if self.token_atual.tipo == tipo_token:
            self.token_atual = self.lexer.get_next_token()
        else:
            self.erro(f'Esperado {tipo_token}, encontrado {self.token_atual.tipo}')

    def formula(self):
        if self.token_atual.tipo == 'CONSTANTE':
            self.consumir('CONSTANTE')
            return True
            
        elif self.token_atual.tipo == 'PROPOSICAO':
            self.consumir('PROPOSICAO')
            return True
            
        elif self.token_atual.tipo == 'ABREPAREN':
            self.consumir('ABREPAREN')
            
            if self.token_atual.tipo == 'OPERADORUNARIO':
                self.consumir('OPERADORUNARIO')
                if not self.formula():
                    return False
                self.consumir('FECHAPAREN')
                return True
                
            elif self.token_atual.tipo == 'OPERADORBINARIO':
                self.consumir('OPERADORBINARIO')
                if not self.formula():
                    return False
                if not self.formula():
                    return False
                self.consumir('FECHAPAREN')
                return True
                
            else:
                return False
                
        return False

    def parse(self):
        try:
            resultado = self.formula()
            if self.token_atual.tipo != 'EOF':
                return False
            return resultado
        except Exception:
            return False

def validar_expressao(expressao):
    try:
        lexer = Lexer(expressao)
        parser = Parser(lexer)
        return parser.parse()
    except Exception:
        return False

def debug_lexer(expressao):
    lexer = Lexer(expressao)
    while True:
        estado_atual = lexer.get_estado_atual()
        token = lexer.get_next_token()
        print(f"Estado: {estado_atual}, Token: {token}")
        if token.tipo == 'EOF':
            break

def main():
    try:
        nome_arquivo = sys.argv[1]
        with open(nome_arquivo, 'r') as arquivo:
            num_expressoes = int(arquivo.readline())
            
            for _ in range(num_expressoes):
                expressao = arquivo.readline().strip()
                if validar_expressao(expressao):
                    print("valida")
                else:
                    print("invalida")
                    
    except Exception as e:
        print(f"Erro ao processar arquivo: {e}")
        exit(1)

if __name__ == "__main__":
    main()
