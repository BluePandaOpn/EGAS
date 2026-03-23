from typing import List
from lib.gos.lexer.token import Token, TokenType
from egas.core.logger import Logger

class Lexer:
    """
    Analizador Léxico del Lenguaje GOS.
    Toma una cadena de texto y la divide en una lista de Tokens válidos.
    """
    
    # Diccionario de Palabras Clave Reservadas
    KEYWORDS = {
        "var": TokenType.VAR,
        "func": TokenType.FUNC,
        "if": TokenType.IF,
        "else": TokenType.ELSE,
        "while": TokenType.WHILE,
        "for": TokenType.FOR,
        "return": TokenType.RETURN,
        "is": TokenType.IS,
        "true": TokenType.TRUE,
        "false": TokenType.FALSE,
        "nil": TokenType.NIL,
        "self": TokenType.SELF,
        "import": TokenType.IMPORT,
    }

    def __init__(self, source_code: str):
        self.source = source_code
        self.tokens: List[Token] = []
        
        self.start = 0
        self.current = 0
        self.line = 1

    def tokenize(self) -> List[Token]:
        """Recorre todo el código fuente y produce la lista de tokens."""
        while not self._is_at_end():
            self.start = self.current
            self._scan_token()

        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens

    def _scan_token(self):
        """Identifica el siguiente token del código."""
        c = self._advance()

        # Espacios en blanco y saltos de línea
        if c in (' ', '\r', '\t'):
            return
        if c == '\n':
            self.line += 1
            return

        # Símbolos de un solo caracter
        if c == '(': self._add_token(TokenType.LPAREN)
        elif c == ')': self._add_token(TokenType.RPAREN)
        elif c == '{': self._add_token(TokenType.LBRACE)
        elif c == '}': self._add_token(TokenType.RBRACE)
        elif c == ',': self._add_token(TokenType.COMMA)
        elif c == '.': self._add_token(TokenType.DOT)
        elif c == ':': self._add_token(TokenType.COLON)
        elif c == '+': self._add_token(TokenType.PLUS)
        elif c == '-': self._add_token(TokenType.MINUS)
        elif c == '*': self._add_token(TokenType.STAR)

        # Símbolos dobles o condicionales (!=, ==, <=, >=)
        elif c == '!':
            if self._match('='): self._add_token(TokenType.BANG_EQUALS)
        elif c == '=':
            if self._match('='): self._add_token(TokenType.EQUALS_EQUALS)
            else: self._add_token(TokenType.EQUALS)
        elif c == '<':
            if self._match('='): self._add_token(TokenType.LESS_EQUALS)
            else: self._add_token(TokenType.LESS)
        elif c == '>':
            if self._match('='): self._add_token(TokenType.GREATER_EQUALS)
            else: self._add_token(TokenType.GREATER)

        # --- 🚀 División y Comentarios (// y /* */) ---
        elif c == '/':
            if self._match('/'):
                # Comentario de una línea
                while self._peek() != '\n' and not self._is_at_end():
                    self._advance()
            elif self._match('*'):
                # Comentario multilínea
                self._multiline_comment()
            else:
                self._add_token(TokenType.SLASH)

        # Literales complejos (Strings, Números e Identificadores)
        elif c == '"':
            self._string()
        elif c.isdigit():
            self._number()
        elif c.isalpha() or c == '_':
            self._identifier()
        else:
            Logger.error("GOS Lexer", f"Caracter inesperado '{c}' en la línea {self.line}")

    def _multiline_comment(self):
        """Ignora los bloques de código encerrados entre /* y */."""
        while not self._is_at_end():
            if self._peek() == '\n':
                self.line += 1
            
            if self._peek() == '*':
                self._advance()
                if self._match('/'):
                    return # Cierre encontrado con éxito
                continue
            
            self._advance()

        Logger.error("GOS Lexer", f"Comentario de bloque /* sin cerrar en la línea {self.line}")

    # --- Funciones de Utilidad de Escaneo ---

    def _advance(self) -> str:
        self.current += 1
        return self.source[self.current - 1]

    def _match(self, expected: str) -> bool:
        if self._is_at_end(): return False
        if self.source[self.current] != expected: return False
        self.current += 1
        return True

    def _peek(self) -> str:
        if self._is_at_end(): return '\0'
        return self.source[self.current]

    def _peek_next(self) -> str:
        if self.current + 1 >= len(self.source): return '\0'
        return self.source[self.current + 1]

    def _is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def _add_token(self, token_type: TokenType, literal: object = None):
        text = self.source[self.start:self.current]
        self.tokens.append(Token(token_type, text, literal, self.line))

    # --- Procesamiento de Literales ---

    def _string(self):
        """Procesa una cadena de texto encerrada entre comillas ""."""
        while self._peek() != '"' and not self._is_at_end():
            if self._peek() == '\n': self.line += 1
            self._advance()

        if self._is_at_end():
            Logger.error("GOS Lexer", f"Cadena de texto sin cerrar en la línea {self.line}")
            return

        self._advance() # Cerrar comilla
        value = self.source[self.start + 1:self.current - 1]
        self._add_token(TokenType.STRING, value)

    def _number(self):
        """Procesa números enteros o decimales."""
        while self._peek().isdigit():
            self._advance()

        if self._peek() == '.' and self._peek_next().isdigit():
            self._advance() # Consumir el punto
            while self._peek().isdigit():
                self._advance()

        value = float(self.source[self.start:self.current])
        self._add_token(TokenType.NUMBER, value)

    def _identifier(self):
        """Procesa nombres de variables o palabras clave de GOS."""
        while self._peek().isalnum() or self._peek() == '_':
            self._advance()

        text = self.source[self.start:self.current]
        token_type = self.KEYWORDS.get(text, TokenType.IDENTIFIER)
        self._add_token(token_type)
