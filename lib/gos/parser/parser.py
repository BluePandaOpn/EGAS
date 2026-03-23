from typing import List
from lib.gos.lexer.token import Token, TokenType
from lib.gos.parser.ast import *

class Parser:
    """
    Parser del Lenguaje GOS. Convierte Tokens en un Árbol de Sintaxis Abstracta (AST).
    Utiliza el método de Descenso Recurvido para priorizar la matemática y gramática.
    """
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0

    def parse(self) -> List[Stmt]:
        """Inicia el análisis gramatical del script."""
        statements: List[Stmt] = []
        
        while not self._is_at_end():
            stmt = self._declaration()
            if stmt:
                statements.append(stmt)
                
        return statements

    # --- 🏗️ REGLAS GRAMATICALES (De mayor a menor jerarquía) ---

    def _declaration(self) -> Optional[Stmt]:
        try:
            if self._match(TokenType.IMPORT): return self._import_declaration()
            if self._match(TokenType.FUNC): return self._function_declaration()
            if self._match(TokenType.VAR): return self._var_declaration()
            return self._statement()
        except Exception as e:
            self._synchronize()
            print(f"[GOS Parser] Error de sintaxis: {e}")
            return None

    def _import_declaration(self) -> Stmt:
        path_expr = self._expression()
        return ImportStmt(path_expr)

    def _function_declaration(self) -> Stmt:
        name = self._consume(TokenType.IDENTIFIER, "Se esperaba el nombre de la función.")
        self._consume(TokenType.LPAREN, "Se esperaba '(' después del nombre de la función.")
        
        parameters: List[Token] = []
        if not self._check(TokenType.RPAREN):
            while True:
                parameters.append(self._consume(TokenType.IDENTIFIER, "Se esperaba el nombre del parámetro."))
                if not self._match(TokenType.COMMA): break

        self._consume(TokenType.RPAREN, "Se esperaba ')' después de los parámetros.")
        self._consume(TokenType.LBRACE, "Se esperaba '{' antes del cuerpo de la función.")
        
        body = self._block()
        return FunctionStmt(name, parameters, body)

    def _var_declaration(self) -> Stmt:
        name = self._consume(TokenType.IDENTIFIER, "Se esperaba el nombre de la variable.")
        
        initializer = None
        if self._match(TokenType.EQUALS):
            initializer = self._expression()

        return VarStmt(name, initializer)

    def _statement(self) -> Stmt:
        if self._match(TokenType.IF): return self._if_statement()
        if self._match(TokenType.WHILE): return self._while_statement()
        if self._match(TokenType.RETURN): return self._return_statement()
        if self._match(TokenType.LBRACE): return BlockStmt(self._block())
        
        return self._expression_statement()

    def _if_statement(self) -> Stmt:
        self._consume(TokenType.LPAREN, "Se esperaba '(' después de 'if'.")
        condition = self._expression()
        self._consume(TokenType.RPAREN, "Se esperaba ')' después de la condición del if.")

        then_branch = self._statement()
        else_branch = None

        if self._match(TokenType.ELSE):
            else_branch = self._statement()

        return IfStmt(condition, then_branch, else_branch)

    def _while_statement(self) -> Stmt:
        self._consume(TokenType.LPAREN, "Se esperaba '(' después de 'while'.")
        condition = self._expression()
        self._consume(TokenType.RPAREN, "Se esperaba ')' después de la condición del while.")
        
        body = self._statement()
        return WhileStmt(condition, body)

    def _return_statement(self) -> Stmt:
        keyword = self._previous()
        value = None
        if not self._check(TokenType.RBRACE) and not self._is_at_end():
            value = self._expression()

        return ReturnStmt(keyword, value)

    def _block(self) -> List[Stmt]:
        statements = []
        while not self._check(TokenType.RBRACE) and not self._is_at_end():
            stmt = self._declaration()
            if stmt:
                statements.append(stmt)

        self._consume(TokenType.RBRACE, "Se esperaba '}' después del bloque.")
        return statements

    def _expression_statement(self) -> Stmt:
        expr = self._expression()
        return ExpressionStmt(expr)

    # --- 📐 MATEMÁTICAS (Jerarquía de Operadores) ---

    def _expression(self) -> Expr:
        return self._assignment()

    def _assignment(self) -> Expr:
        expr = self._equality()

        if self._match(TokenType.EQUALS):
            equals = self._previous()
            value = self._assignment()

            if isinstance(expr, VariableExpr):
                name = expr.name
                return SetExpr(VariableExpr(name), name, value) # Reutilizando asignación directa
            elif isinstance(expr, GetExpr):
                return SetExpr(expr.obj, expr.name, value)

            print(f"[GOS Parser] Objetivo de asignación inválido en línea {equals.line}")

        return expr

    def _equality(self) -> Expr:
        expr = self._comparison()

        while self._match(TokenType.BANG_EQUALS, TokenType.EQUALS_EQUALS):
            operator = self._previous()
            right = self._comparison()
            expr = BinaryExpr(expr, operator, right)

        return expr

    def _comparison(self) -> Expr:
        expr = self._term()

        while self._match(TokenType.GREATER, TokenType.GREATER_EQUALS, TokenType.LESS, TokenType.LESS_EQUALS):
            operator = self._previous()
            right = self._term()
            expr = BinaryExpr(expr, operator, right)

        return expr

    def _term(self) -> Expr:
        expr = self._factor()

        while self._match(TokenType.PLUS, TokenType.MINUS):
            operator = self._previous()
            right = self._factor()
            expr = BinaryExpr(expr, operator, right)

        return expr

    def _factor(self) -> Expr:
        expr = self._call()

        while self._match(TokenType.SLASH, TokenType.STAR):
            operator = self._previous()
            right = self._call()
            expr = BinaryExpr(expr, operator, right)

        return expr

    def _call(self) -> Expr:
        expr = self._primary()

        while True:
            if self._match(TokenType.LPAREN):
                expr = self._finish_call(expr)
            elif self._match(TokenType.DOT):
                name = self._consume(TokenType.IDENTIFIER, "Se esperaba un nombre de propiedad después de '.'.")
                expr = GetExpr(expr, name)
            else:
                break

        return expr

    def _finish_call(self, callee: Expr) -> Expr:
        arguments = []
        if not self._check(TokenType.RPAREN):
            while True:
                arguments.append(self._expression())
                if not self._match(TokenType.COMMA): break

        paren = self._consume(TokenType.RPAREN, "Se esperaba ')' después de los argumentos.")
        return CallExpr(callee, paren, arguments)

    def _primary(self) -> Expr:
        if self._match(TokenType.FALSE): return LiteralExpr(False)
        if self._match(TokenType.TRUE): return LiteralExpr(True)
        if self._match(TokenType.NIL): return LiteralExpr(None)

        if self._match(TokenType.NUMBER, TokenType.STRING):
            return LiteralExpr(self._previous().literal)

        if self._match(TokenType.SELF):
            return VariableExpr(self._previous())

        if self._match(TokenType.IDENTIFIER):
            return VariableExpr(self._previous())

        if self._match(TokenType.LPAREN):
            expr = self._expression()
            self._consume(TokenType.RPAREN, "Se esperaba ')' después de la expresión.")
            return GroupingExpr(expr)

        raise Exception(f"Se esperaba una expresión válida en la línea {self._peek().line}.")

    # --- 🛠️ UTILIDADES DE LECTURA ---

    def _match(self, *types) -> bool:
        for type_ in types:
            if self._check(type_):
                self._advance()
                return True
        return False

    def _check(self, token_type: TokenType) -> bool:
        if self._is_at_end(): return False
        return self._peek().type == token_type

    def _advance(self) -> Token:
        if not self._is_at_end(): self.current += 1
        return self._previous()

    def _is_at_end(self) -> bool:
        return self._peek().type == TokenType.EOF

    def _peek(self) -> Token:
        return self.tokens[self.current]

    def _previous(self) -> Token:
        return self.tokens[self.current - 1]

    def _consume(self, token_type: TokenType, message: str) -> Token:
        if self._check(token_type): return self._advance()
        raise Exception(f"{message} (Encontrado: {self._peek().type.name} en línea {self._peek().line})")

    def _synchronize(self):
        """Intenta recuperarse de un error de sintaxis saltando al siguiente bloque/línea."""
        self._advance()
        while not self._is_at_end():
            if self._previous().type == TokenType.RBRACE: return # Terminó un bloque
            if self._peek().type in (TokenType.FUNC, TokenType.VAR, TokenType.IF, TokenType.FOR, TokenType.WHILE, TokenType.RETURN):
                return
            self._advance()