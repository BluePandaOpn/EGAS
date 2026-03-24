from abc import ABC
from typing import List, Optional

from lib.gos.lexer.token import Token


class ASTNode(ABC):
    """Clase base para cualquier nodo del AST."""


class Expr(ASTNode):
    """Nodo que evalua y devuelve un valor."""


class Stmt(ASTNode):
    """Nodo ejecutable que no devuelve un valor directo."""


class LiteralExpr(Expr):
    def __init__(self, value):
        self.value = value


class VariableExpr(Expr):
    def __init__(self, name: Token):
        self.name = name


class BinaryExpr(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right


class UnaryExpr(Expr):
    def __init__(self, operator: Token, right: Expr):
        self.operator = operator
        self.right = right


class GroupingExpr(Expr):
    def __init__(self, expression: Expr):
        self.expression = expression


class CallExpr(Expr):
    def __init__(self, callee: Expr, paren: Token, arguments: List[Expr]):
        self.callee = callee
        self.paren = paren
        self.arguments = arguments


class GetExpr(Expr):
    def __init__(self, obj: Expr, name: Token):
        self.obj = obj
        self.name = name


class SetExpr(Expr):
    def __init__(self, obj: Expr, name: Token, value: Expr):
        self.obj = obj
        self.name = name
        self.value = value


class ListExpr(Expr):
    def __init__(self, items: List[Expr]):
        self.items = items


class DictExpr(Expr):
    def __init__(self, items: List[tuple[Expr, Expr]]):
        self.items = items


class ExpressionStmt(Stmt):
    def __init__(self, expression: Expr):
        self.expression = expression


class VarStmt(Stmt):
    def __init__(self, name: Token, initializer: Optional[Expr]):
        self.name = name
        self.initializer = initializer


class ConstStmt(Stmt):
    def __init__(self, name: Token, initializer: Expr):
        self.name = name
        self.initializer = initializer


class BlockStmt(Stmt):
    def __init__(self, statements: List[Stmt]):
        self.statements = statements


class IfStmt(Stmt):
    def __init__(self, condition: Expr, then_branch: Stmt, else_branch: Optional[Stmt]):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch


class WhileStmt(Stmt):
    def __init__(self, condition: Expr, body: Stmt):
        self.condition = condition
        self.body = body


class FunctionStmt(Stmt):
    def __init__(self, name: Token, params: List[Token], body: List[Stmt]):
        self.name = name
        self.params = params
        self.body = body


class ReturnStmt(Stmt):
    def __init__(self, keyword: Token, value: Optional[Expr]):
        self.keyword = keyword
        self.value = value


class ImportStmt(Stmt):
    def __init__(self, path: Expr):
        self.path = path
