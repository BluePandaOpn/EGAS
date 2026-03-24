from typing import List

from egas.core.logger import Logger
from lib.gos.lexer.token import Token, TokenType


class Lexer:
    """Analizador lexico del lenguaje GOS."""

    KEYWORDS = {
        "var": TokenType.VAR,
        "const": TokenType.CONST,
        "func": TokenType.FUNC,
        "if": TokenType.IF,
        "elif": TokenType.ELIF,
        "else": TokenType.ELSE,
        "while": TokenType.WHILE,
        "for": TokenType.FOR,
        "return": TokenType.RETURN,
        "and": TokenType.AND,
        "or": TokenType.OR,
        "not": TokenType.NOT,
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
        while not self._is_at_end():
            self.start = self.current
            self._scan_token()

        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens

    def _scan_token(self):
        c = self._advance()

        if c in (" ", "\r", "\t"):
            return
        if c == "\n":
            self.line += 1
            return

        if c == "(":
            self._add_token(TokenType.LPAREN)
        elif c == ")":
            self._add_token(TokenType.RPAREN)
        elif c == "{":
            self._add_token(TokenType.LBRACE)
        elif c == "}":
            self._add_token(TokenType.RBRACE)
        elif c == "[":
            self._add_token(TokenType.LBRACKET)
        elif c == "]":
            self._add_token(TokenType.RBRACKET)
        elif c == ",":
            self._add_token(TokenType.COMMA)
        elif c == ".":
            self._add_token(TokenType.DOT)
        elif c == ":":
            self._add_token(TokenType.COLON)
        elif c == "+":
            self._add_token(TokenType.PLUS)
        elif c == "-":
            self._add_token(TokenType.MINUS)
        elif c == "*":
            self._add_token(TokenType.STAR)
        elif c == "|":
            self._add_token(TokenType.PIPE)
        elif c == "!":
            if self._match("="):
                self._add_token(TokenType.BANG_EQUALS)
            else:
                self._add_token(TokenType.BANG)
        elif c == "=":
            if self._match("="):
                self._add_token(TokenType.EQUALS_EQUALS)
            else:
                self._add_token(TokenType.EQUALS)
        elif c == "<":
            if self._match("="):
                self._add_token(TokenType.LESS_EQUALS)
            else:
                self._add_token(TokenType.LESS)
        elif c == ">":
            if self._match("="):
                self._add_token(TokenType.GREATER_EQUALS)
            else:
                self._add_token(TokenType.GREATER)
        elif c == "/":
            if self._match("/"):
                while self._peek() != "\n" and not self._is_at_end():
                    self._advance()
            elif self._match("*"):
                self._multiline_comment()
            else:
                self._add_token(TokenType.SLASH)
        elif c == '"':
            self._string()
        elif c.isdigit():
            self._number()
        elif c.isalpha() or c == "_":
            self._identifier()
        else:
            Logger.error("GOS Lexer", f"Caracter inesperado '{c}' en la linea {self.line}")

    def _multiline_comment(self):
        while not self._is_at_end():
            if self._peek() == "\n":
                self.line += 1
            if self._peek() == "*":
                self._advance()
                if self._match("/"):
                    return
                continue
            self._advance()

        Logger.error("GOS Lexer", f"Comentario de bloque sin cerrar en la linea {self.line}")

    def _advance(self) -> str:
        self.current += 1
        return self.source[self.current - 1]

    def _match(self, expected: str) -> bool:
        if self._is_at_end():
            return False
        if self.source[self.current] != expected:
            return False
        self.current += 1
        return True

    def _peek(self) -> str:
        if self._is_at_end():
            return "\0"
        return self.source[self.current]

    def _peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return "\0"
        return self.source[self.current + 1]

    def _is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def _add_token(self, token_type: TokenType, literal: object = None):
        text = self.source[self.start:self.current]
        self.tokens.append(Token(token_type, text, literal, self.line))

    def _string(self):
        while self._peek() != '"' and not self._is_at_end():
            if self._peek() == "\n":
                self.line += 1
            self._advance()

        if self._is_at_end():
            Logger.error("GOS Lexer", f"Cadena sin cerrar en la linea {self.line}")
            return

        self._advance()
        value = self.source[self.start + 1:self.current - 1]
        self._add_token(TokenType.STRING, value)

    def _number(self):
        while self._peek().isdigit():
            self._advance()

        if self._peek() == "." and self._peek_next().isdigit():
            self._advance()
            while self._peek().isdigit():
                self._advance()

        value = float(self.source[self.start:self.current])
        self._add_token(TokenType.NUMBER, value)

    def _identifier(self):
        while self._peek().isalnum() or self._peek() == "_":
            self._advance()

        text = self.source[self.start:self.current]
        token_type = self.KEYWORDS.get(text, TokenType.IDENTIFIER)
        self._add_token(token_type)
