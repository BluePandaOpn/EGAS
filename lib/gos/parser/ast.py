from abc import ABC
from typing import List, Optional
from lib.gos.lexer.token import Token

# --- BASE ---
class ASTNode(ABC):
    """Clase base para cualquier nodo del Árbol de Sintaxis Abstracta (AST)."""
    pass

class Expr(ASTNode):
    """Representa un nodo que evalúa y devuelve un valor."""
    pass

class Stmt(ASTNode):
    """Representa un nodo de acción/sentencia que no devuelve un valor."""
    pass


# --- 📈 EXPRESIONES (Cálculos y Valores) ---

class LiteralExpr(Expr):
    """Valores fijos: números, strings, booleanos, nil."""
    def __init__(self, value):
        self.value = value

class VariableExpr(Expr):
    """Lectura de una variable por su nombre."""
    def __init__(self, name: Token):
        self.name = name

class BinaryExpr(Expr):
    """Operaciones matemáticas y lógicas bilaterales (+, -, *, ==, <, etc.)."""
    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right

class GroupingExpr(Expr):
    """Expresiones entre paréntesis (a + b)."""
    def __init__(self, expression: Expr):
        self.expression = expression

class CallExpr(Expr):
    """Llamada a una función: mover_nave(10, 20)."""
    def __init__(self, callee: Expr, paren: Token, arguments: List[Expr]):
        self.callee = callee
        self.paren = paren
        self.arguments = arguments

class GetExpr(Expr):
    """Acceso a propiedades usando el punto: self.position.x"""
    def __init__(self, obj: Expr, name: Token):
        self.obj = obj
        self.name = name

class SetExpr(Expr):
    """Asignación de propiedades: self.position.x = 100"""
    def __init__(self, obj: Expr, name: Token, value: Expr):
        self.obj = obj
        self.name = name
        self.value = value


# --- 📜 SENTENCIAS (Estructuras de Control) ---

class ExpressionStmt(Stmt):
    """Una expresión que se ejecuta como sentencia (ej: llamar una función)."""
    def __init__(self, expression: Expr):
        self.expression = expression

class VarStmt(Stmt):
    """Declaración de variable: var vida = 100"""
    def __init__(self, name: Token, initializer: Optional[Expr]):
        self.name = name
        self.initializer = initializer

class BlockStmt(Stmt):
    """Un grupo de sentencias dentro de llaves { ... }"""
    def __init__(self, statements: List[Stmt]):
        self.statements = statements

class IfStmt(Stmt):
    """Estructura condicional if-else."""
    def __init__(self, condition: Expr, then_branch: Stmt, else_branch: Optional[Stmt]):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

class WhileStmt(Stmt):
    """Bucle de repetición condicional."""
    def __init__(self, condition: Expr, body: Stmt):
        self.condition = condition
        self.body = body

class FunctionStmt(Stmt):
    """Declaración de una función: func mi_funcion(a, b) { ... }"""
    def __init__(self, name: Token, params: List[Token], body: List[Stmt]):
        self.name = name
        self.params = params
        self.body = body

class ReturnStmt(Stmt):
    """Retorno de una función."""
    def __init__(self, keyword: Token, value: Optional[Expr]):
        self.keyword = keyword
        self.value = value