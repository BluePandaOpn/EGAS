from typing import List, Optional

from lib.gos.lexer.token import Token, TokenType
from lib.gos.parser.ast import (
    BinaryExpr,
    BreakStmt,
    BlockStmt,
    CallExpr,
    ContinueStmt,
    ConstStmt,
    DictExpr,
    ExpressionStmt,
    ForEachStmt,
    FunctionStmt,
    GetExpr,
    GroupingExpr,
    IfStmt,
    IndexExpr,
    IndexSetExpr,
    ImportStmt,
    ListExpr,
    LiteralExpr,
    ReturnStmt,
    SetExpr,
    UnaryExpr,
    VarStmt,
    VariableExpr,
    WhileStmt,
)
from lib.gos.runtime.errors import GOSParserError


class Parser:
    """Parser de GOS con operadores logicos y literales de coleccion."""

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0

    def parse(self) -> List:
        statements = []
        while not self._is_at_end():
            stmt = self._declaration()
            if stmt is not None:
                statements.append(stmt)
        return statements

    def _declaration(self) -> Optional:
        if self._match(TokenType.IMPORT):
            return self._import_declaration()
        if self._match(TokenType.FUNC):
            return self._function_declaration()
        if self._match(TokenType.CONST):
            return self._const_declaration()
        if self._match(TokenType.VAR):
            return self._var_declaration()
        return self._statement()

    def _import_declaration(self):
        return ImportStmt(self._expression())

    def _function_declaration(self):
        name = self._consume(TokenType.IDENTIFIER, "Se esperaba el nombre de la funcion.")
        self._consume(TokenType.LPAREN, "Se esperaba '(' despues del nombre de la funcion.")

        parameters: List[Token] = []
        if not self._check(TokenType.RPAREN):
            while True:
                parameters.append(self._consume(TokenType.IDENTIFIER, "Se esperaba el nombre del parametro."))
                if not self._match(TokenType.COMMA):
                    break

        self._consume(TokenType.RPAREN, "Se esperaba ')' despues de los parametros.")
        self._consume(TokenType.LBRACE, "Se esperaba '{' antes del cuerpo de la funcion.")
        return FunctionStmt(name, parameters, self._block())

    def _const_declaration(self):
        name = self._consume(TokenType.IDENTIFIER, "Se esperaba el nombre de la constante.")
        self._consume(TokenType.EQUALS, "Se esperaba '=' en la declaracion const.")
        return ConstStmt(name, self._expression())

    def _var_declaration(self):
        name = self._consume(TokenType.IDENTIFIER, "Se esperaba el nombre de la variable.")
        initializer = self._expression() if self._match(TokenType.EQUALS) else None
        return VarStmt(name, initializer)

    def _statement(self):
        if self._match(TokenType.IF):
            return self._if_statement()
        if self._match(TokenType.WHILE):
            return self._while_statement()
        if self._match(TokenType.FOR):
            return self._for_statement()
        if self._match(TokenType.BREAK):
            return BreakStmt(self._previous())
        if self._match(TokenType.CONTINUE):
            return ContinueStmt(self._previous())
        if self._match(TokenType.RETURN):
            return self._return_statement()
        if self._match(TokenType.LBRACE):
            return BlockStmt(self._block())
        return self._expression_statement()

    def _if_statement(self):
        self._consume(TokenType.LPAREN, "Se esperaba '(' despues de 'if'.")
        condition = self._expression()
        self._consume(TokenType.RPAREN, "Se esperaba ')' despues de la condicion.")
        then_branch = self._statement()
        else_branch = None

        if self._match(TokenType.ELIF):
            else_branch = self._elif_statement()
        elif self._match(TokenType.ELSE):
            else_branch = self._statement()

        return IfStmt(condition, then_branch, else_branch)

    def _elif_statement(self):
        self._consume(TokenType.LPAREN, "Se esperaba '(' despues de 'elif'.")
        condition = self._expression()
        self._consume(TokenType.RPAREN, "Se esperaba ')' despues de la condicion.")
        then_branch = self._statement()
        else_branch = None

        if self._match(TokenType.ELIF):
            else_branch = self._elif_statement()
        elif self._match(TokenType.ELSE):
            else_branch = self._statement()

        return IfStmt(condition, then_branch, else_branch)

    def _while_statement(self):
        self._consume(TokenType.LPAREN, "Se esperaba '(' despues de 'while'.")
        condition = self._expression()
        self._consume(TokenType.RPAREN, "Se esperaba ')' despues de la condicion.")
        return WhileStmt(condition, self._statement())

    def _for_statement(self):
        self._consume(TokenType.LPAREN, "Se esperaba '(' despues de 'for'.")
        iterator = self._consume(TokenType.IDENTIFIER, "Se esperaba el nombre de la variable iteradora.")
        self._consume(TokenType.IN, "Se esperaba 'in' dentro del for.")
        iterable = self._expression()
        self._consume(TokenType.RPAREN, "Se esperaba ')' despues del iterable.")
        return ForEachStmt(iterator, iterable, self._statement())

    def _return_statement(self):
        keyword = self._previous()
        value = None
        if not self._check(TokenType.RBRACE) and not self._is_at_end():
            value = self._expression()
        return ReturnStmt(keyword, value)

    def _block(self) -> List:
        statements = []
        while not self._check(TokenType.RBRACE) and not self._is_at_end():
            statements.append(self._declaration())
        self._consume(TokenType.RBRACE, "Se esperaba '}' despues del bloque.")
        return [stmt for stmt in statements if stmt is not None]

    def _expression_statement(self):
        return ExpressionStmt(self._expression())

    def _expression(self):
        return self._assignment()

    def _assignment(self):
        expr = self._or()

        if self._match(TokenType.EQUALS):
            equals = self._previous()
            value = self._assignment()

            if isinstance(expr, VariableExpr):
                return SetExpr(VariableExpr(expr.name), expr.name, value)
            if isinstance(expr, GetExpr):
                return SetExpr(expr.obj, expr.name, value)
            if isinstance(expr, IndexExpr):
                return IndexSetExpr(expr.obj, expr.index, value, expr.bracket)

            raise GOSParserError("Objetivo de asignacion invalido.", line=equals.line)

        return expr

    def _or(self):
        expr = self._and()
        while self._match(TokenType.OR, TokenType.PIPE):
            expr = BinaryExpr(expr, self._previous(), self._and())
        return expr

    def _and(self):
        expr = self._equality()
        while self._match(TokenType.AND):
            expr = BinaryExpr(expr, self._previous(), self._equality())
        return expr

    def _equality(self):
        expr = self._comparison()
        while self._match(TokenType.BANG_EQUALS, TokenType.EQUALS_EQUALS):
            expr = BinaryExpr(expr, self._previous(), self._comparison())
        return expr

    def _comparison(self):
        expr = self._term()
        while self._match(TokenType.GREATER, TokenType.GREATER_EQUALS, TokenType.LESS, TokenType.LESS_EQUALS, TokenType.IS):
            expr = BinaryExpr(expr, self._previous(), self._term())
        return expr

    def _term(self):
        expr = self._factor()
        while self._match(TokenType.PLUS, TokenType.MINUS):
            expr = BinaryExpr(expr, self._previous(), self._factor())
        return expr

    def _factor(self):
        expr = self._unary()
        while self._match(TokenType.SLASH, TokenType.STAR, TokenType.PERCENT):
            expr = BinaryExpr(expr, self._previous(), self._unary())
        return expr

    def _unary(self):
        if self._match(TokenType.NOT, TokenType.BANG, TokenType.MINUS):
            return UnaryExpr(self._previous(), self._unary())
        return self._call()

    def _call(self):
        expr = self._primary()

        while True:
            if self._match(TokenType.LPAREN):
                expr = self._finish_call(expr)
            elif self._match(TokenType.DOT):
                name = self._consume(TokenType.IDENTIFIER, "Se esperaba un nombre de propiedad despues de '.'.")
                expr = GetExpr(expr, name)
            elif self._match(TokenType.LBRACKET):
                index = self._expression()
                bracket = self._consume(TokenType.RBRACKET, "Se esperaba ']' despues del indice.")
                expr = IndexExpr(expr, index, bracket)
            else:
                break
        return expr

    def _finish_call(self, callee):
        arguments = []
        if not self._check(TokenType.RPAREN):
            while True:
                arguments.append(self._expression())
                if not self._match(TokenType.COMMA):
                    break
        paren = self._consume(TokenType.RPAREN, "Se esperaba ')' despues de los argumentos.")
        return CallExpr(callee, paren, arguments)

    def _primary(self):
        if self._match(TokenType.FALSE):
            return LiteralExpr(False)
        if self._match(TokenType.TRUE):
            return LiteralExpr(True)
        if self._match(TokenType.NIL):
            return LiteralExpr(None)
        if self._match(TokenType.NUMBER, TokenType.STRING):
            return LiteralExpr(self._previous().literal)
        if self._match(TokenType.SELF):
            return VariableExpr(self._previous())
        if self._match(TokenType.IDENTIFIER):
            return VariableExpr(self._previous())
        if self._match(TokenType.LPAREN):
            expr = self._expression()
            self._consume(TokenType.RPAREN, "Se esperaba ')' despues de la expresion.")
            return GroupingExpr(expr)
        if self._match(TokenType.LBRACKET):
            return self._list_literal()
        if self._match(TokenType.LBRACE):
            return self._dict_literal()

        raise GOSParserError("Se esperaba una expresion valida.", line=self._peek().line)

    def _list_literal(self):
        items = []
        if not self._check(TokenType.RBRACKET):
            while True:
                items.append(self._expression())
                if not self._match(TokenType.COMMA):
                    break
        self._consume(TokenType.RBRACKET, "Se esperaba ']' al cerrar la lista.")
        return ListExpr(items)

    def _dict_literal(self):
        items = []
        if not self._check(TokenType.RBRACE):
            while True:
                key = self._expression()
                self._consume(TokenType.COLON, "Se esperaba ':' entre clave y valor.")
                value = self._expression()
                items.append((key, value))
                if not self._match(TokenType.COMMA):
                    break
        self._consume(TokenType.RBRACE, "Se esperaba '}' al cerrar el diccionario.")
        return DictExpr(items)

    def _match(self, *types) -> bool:
        for token_type in types:
            if self._check(token_type):
                self._advance()
                return True
        return False

    def _check(self, token_type: TokenType) -> bool:
        if self._is_at_end():
            return False
        return self._peek().type == token_type

    def _advance(self) -> Token:
        if not self._is_at_end():
            self.current += 1
        return self._previous()

    def _is_at_end(self) -> bool:
        return self._peek().type == TokenType.EOF

    def _peek(self) -> Token:
        return self.tokens[self.current]

    def _previous(self) -> Token:
        return self.tokens[self.current - 1]

    def _consume(self, token_type: TokenType, message: str) -> Token:
        if self._check(token_type):
            return self._advance()
        raise GOSParserError(message, line=self._peek().line)
