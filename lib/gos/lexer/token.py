from enum import Enum, auto

class TokenType(Enum):
    # --- Tipos Primitivos y Literales ---
    NUMBER = auto()     # 10, 3.14
    STRING = auto()     # "Hola nave"
    IDENTIFIER = auto() # nombres de variables, funciones, nodos
    
    # --- Operadores y Símbolos Matemáticos ---
    PLUS = auto()       # +
    MINUS = auto()      # -
    STAR = auto()       # *
    SLASH = auto()      # /
    EQUALS = auto()     # =
    EQUALS_EQUALS = auto() # ==
    BANG_EQUALS = auto()   # !=
    LESS = auto()       # <
    LESS_EQUALS = auto() # <=
    GREATER = auto()    # >
    GREATER_EQUALS = auto() # >=

    # --- Símbolos de Estructura ---
    LPAREN = auto()     # (
    RPAREN = auto()     # )
    LBRACE = auto()     # {
    RBRACE = auto()     # }
    COMMA = auto()      # ,
    DOT = auto()        # .
    COLON = auto()      # :

    # --- Palabras Clave Reservadas de GOS ---
    VAR = auto()        # var
    FUNC = auto()       # func
    IF = auto()         # if
    ELSE = auto()       # else
    WHILE = auto()      # while
    FOR = auto()        # for
    RETURN = auto()     # return
    TRUE = auto()       # true
    FALSE = auto()      # false
    NIL = auto()        # nil (vacío)
    
    # --- Palabras Clave Nativas de EGAS Engine ---
    SELF = auto()       # self (referencia al nodo dueño)
    IMPORT = auto()     # import

    EOF = auto()        # Fin del archivo (End of File)


class Token:
    """Representa una unidad léxica procesada por el Lexer."""
    def __init__(self, token_type: TokenType, lexeme: str, literal: object, line: int):
        self.type = token_type
        self.lexeme = lexeme   # El texto exacto del código
        self.literal = literal # El valor real (ej: si lexeme es "3" el literal es 3 de tipo int)
        self.line = line

    def __str__(self) -> str:
        return f"Token({self.type.name}, Lexeme: '{self.lexeme}', Line: {self.line})"