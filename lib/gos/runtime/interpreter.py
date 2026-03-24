import os
from typing import Any, List

try:
    import requests
except ModuleNotFoundError:
    requests = None

from lib.gos.lexer.lexer import Lexer
from lib.gos.lexer.token import Token, TokenType
from lib.gos.objects.instance import GosInstance
from lib.gos.parser.ast import (
    BinaryExpr,
    BlockStmt,
    CallExpr,
    ConstStmt,
    DictExpr,
    ExpressionStmt,
    FunctionStmt,
    GetExpr,
    GroupingExpr,
    IfStmt,
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
from lib.gos.parser.parser import Parser
from lib.gos.runtime.builtins import BUILTINS
from lib.gos.runtime.environment import Environment
from lib.gos.runtime.errors import GOSPropertyError, GOSRuntimeError
from lib.gos.stdlib import get_stdlib_extensions


class Interpreter:
    """Interprete principal de GOS."""

    def __init__(self, script_path: str | None = None):
        self.script_path = script_path
        self.current_function = None
        self.globals = Environment()
        self.environment = self.globals
        self._load_builtins()

    def _load_builtins(self):
        for name, func in BUILTINS.items():
            self.globals.define(name, func, is_const=True)

        for name, func in get_stdlib_extensions().items():
            self.globals.define(name, func, is_const=True)

    def run(self, statements: List):
        for stmt in statements:
            self._execute(stmt)

    def call_function(self, func_name: str, args: List[Any] | None = None) -> Any:
        args = args or []
        try:
            callee = self.globals.get(Token(TokenType.IDENTIFIER, func_name, None, 0))
        except GOSRuntimeError:
            return None

        if not isinstance(callee, FunctionStmt):
            return None

        return self._invoke_function(callee, args, override_name=func_name)

    def _execute(self, stmt):
        if isinstance(stmt, ExpressionStmt):
            self._evaluate(stmt.expression)
        elif isinstance(stmt, VarStmt):
            value = self._evaluate(stmt.initializer) if stmt.initializer else None
            self.environment.define(stmt.name.lexeme, value)
        elif isinstance(stmt, ConstStmt):
            value = self._evaluate(stmt.initializer)
            self.environment.define(stmt.name.lexeme, value, is_const=True)
        elif isinstance(stmt, BlockStmt):
            self._execute_block(stmt.statements, Environment(self.environment))
        elif isinstance(stmt, IfStmt):
            if self._is_truthy(self._evaluate(stmt.condition)):
                self._execute(stmt.then_branch)
            elif stmt.else_branch:
                self._execute(stmt.else_branch)
        elif isinstance(stmt, WhileStmt):
            while self._is_truthy(self._evaluate(stmt.condition)):
                self._execute(stmt.body)
        elif isinstance(stmt, FunctionStmt):
            self.environment.define(stmt.name.lexeme, stmt, is_const=True)
        elif isinstance(stmt, ReturnStmt):
            raise ReturnException(self._evaluate(stmt.value) if stmt.value else None)
        elif isinstance(stmt, ImportStmt):
            self._execute_import(stmt)

    def _execute_import(self, stmt: ImportStmt):
        source_path = self._evaluate(stmt.path)
        source_code = ""

        if source_path.startswith("http://") or source_path.startswith("https://"):
            if requests is None:
                raise GOSRuntimeError("El soporte HTTP requiere instalar 'requests'.")
            response = requests.get(source_path, timeout=10)
            if response.status_code != 200:
                raise GOSRuntimeError(f"Error HTTP {response.status_code} al importar '{source_path}'.")
            source_code = response.text
        elif source_path.startswith("res://"):
            clean_path = source_path.replace("res://", "")
            absolute_path = os.path.join(os.getcwd(), clean_path)
            if not os.path.exists(absolute_path):
                raise GOSRuntimeError(f"El archivo local '{source_path}' no existe.")
            with open(absolute_path, "r", encoding="utf-8") as file_handle:
                source_code = file_handle.read()
        else:
            raise GOSRuntimeError(f"Prefijo de ruta desconocido '{source_path}'. Usa res:// o http://")

        parser = Parser(Lexer(source_code).tokenize())
        for module_stmt in parser.parse():
            self._execute(module_stmt)

    def _execute_block(self, statements: List, new_env: Environment):
        previous_env = self.environment
        try:
            self.environment = new_env
            for statement in statements:
                self._execute(statement)
        finally:
            self.environment = previous_env

    def _evaluate(self, expr):
        if isinstance(expr, LiteralExpr):
            return expr.value
        if isinstance(expr, GroupingExpr):
            return self._evaluate(expr.expression)
        if isinstance(expr, VariableExpr):
            return self.environment.get(expr.name)
        if isinstance(expr, UnaryExpr):
            return self._evaluate_unary(expr)
        if isinstance(expr, BinaryExpr):
            return self._evaluate_binary(expr)
        if isinstance(expr, CallExpr):
            return self._evaluate_call(expr)
        if isinstance(expr, GetExpr):
            return self._get_property(self._evaluate(expr.obj), expr.name)
        if isinstance(expr, SetExpr):
            return self._evaluate_set(expr)
        if isinstance(expr, ListExpr):
            return [self._evaluate(item) for item in expr.items]
        if isinstance(expr, DictExpr):
            return {self._evaluate(key): self._evaluate(value) for key, value in expr.items}
        return None

    def _evaluate_unary(self, expr: UnaryExpr):
        right = self._evaluate(expr.right)
        if expr.operator.type == TokenType.MINUS:
            return -right
        if expr.operator.type in (TokenType.NOT, TokenType.BANG):
            return not self._is_truthy(right)
        raise GOSRuntimeError(f"Operador unario no soportado '{expr.operator.lexeme}'.", line=expr.operator.line)

    def _evaluate_binary(self, expr: BinaryExpr):
        if expr.operator.type in (TokenType.OR, TokenType.PIPE):
            left = self._evaluate(expr.left)
            return left if self._is_truthy(left) else self._evaluate(expr.right)

        if expr.operator.type == TokenType.AND:
            left = self._evaluate(expr.left)
            return self._evaluate(expr.right) if self._is_truthy(left) else left

        left = self._evaluate(expr.left)
        if expr.operator.lexeme == "is":
            right_class_name = expr.right.name.lexeme if isinstance(expr.right, VariableExpr) else str(self._evaluate(expr.right))
            return left is not None and left.__class__.__name__ == right_class_name

        right = self._evaluate(expr.right)
        operator = expr.operator.type

        try:
            if operator == TokenType.PLUS:
                if isinstance(left, str) or isinstance(right, str):
                    return f"{left}{right}"
                return left + right
            if operator == TokenType.MINUS:
                return left - right
            if operator == TokenType.STAR:
                return left * right
            if operator == TokenType.SLASH:
                if right == 0:
                    raise GOSRuntimeError("Division por cero.", line=expr.operator.line)
                return left / right
            if operator == TokenType.GREATER:
                return left > right
            if operator == TokenType.GREATER_EQUALS:
                return left >= right
            if operator == TokenType.LESS:
                return left < right
            if operator == TokenType.LESS_EQUALS:
                return left <= right
            if operator == TokenType.EQUALS_EQUALS:
                return left == right
            if operator == TokenType.BANG_EQUALS:
                return left != right
        except TypeError as exc:
            raise GOSRuntimeError(
                f"Operacion invalida '{expr.operator.lexeme}' entre {type(left).__name__} y {type(right).__name__}: {exc}",
                line=expr.operator.line,
            )

        raise GOSRuntimeError(f"Operador no soportado '{expr.operator.lexeme}'.", line=expr.operator.line)

    def _evaluate_call(self, expr: CallExpr):
        callee = self._evaluate(expr.callee)
        args = [self._evaluate(arg) for arg in expr.arguments]

        if callable(callee):
            try:
                return callee(*args)
            except Exception as exc:
                raise GOSRuntimeError(f"Error llamando a builtin: {exc}", line=expr.paren.line)

        if isinstance(callee, FunctionStmt):
            return self._invoke_function(callee, args)

        raise GOSRuntimeError("El objeto no es invocable.", line=expr.paren.line)

    def _invoke_function(self, callee: FunctionStmt, args: List[Any], override_name: str | None = None):
        env_function = Environment(self.globals)
        for index, param in enumerate(callee.params):
            if index < len(args):
                env_function.define(param.lexeme, args[index])
            else:
                env_function.define(param.lexeme, None)

        previous_function = self.current_function
        self.current_function = override_name or callee.name.lexeme
        try:
            self._execute_block(callee.body, env_function)
        except ReturnException as result:
            return result.value
        except GOSRuntimeError as exc:
            raise exc.with_context(script_path=self.script_path, function_name=self.current_function)
        finally:
            self.current_function = previous_function
        return None

    def _evaluate_set(self, expr: SetExpr):
        value = self._evaluate(expr.value)
        if isinstance(expr.obj, VariableExpr) and expr.obj.name.lexeme == expr.name.lexeme:
            self.environment.assign(expr.name, value)
            return value
        return self._set_property(self._evaluate(expr.obj), expr.name, value)

    def _get_property(self, obj: Any, name_token: Token) -> Any:
        property_name = name_token.lexeme

        if isinstance(obj, GosInstance):
            return obj.get(name_token)

        alias_value = self._get_python_property_alias(obj, property_name)
        if alias_value is not _PROPERTY_NOT_FOUND:
            return alias_value

        if isinstance(obj, dict):
            if property_name in obj:
                return obj[property_name]
            raise GOSPropertyError(f"Clave '{property_name}' no encontrada en el diccionario.", line=name_token.line)

        if isinstance(obj, list) and property_name == "length":
            return len(obj)

        if hasattr(obj, property_name):
            return getattr(obj, property_name)

        raise GOSPropertyError(f"Propiedad '{property_name}' no encontrada.", line=name_token.line)

    def _set_property(self, obj: Any, name_token: Token, value: Any) -> Any:
        property_name = name_token.lexeme

        if isinstance(obj, GosInstance):
            obj.set(name_token, value)
            return value

        if self._set_python_property_alias(obj, property_name, value):
            return value

        if isinstance(obj, dict):
            obj[property_name] = value
            return value

        if hasattr(obj, property_name):
            setattr(obj, property_name, value)
            return value

        try:
            setattr(obj, property_name, value)
            return value
        except (AttributeError, TypeError):
            raise GOSPropertyError(f"No se puede asignar la propiedad '{property_name}'.", line=name_token.line)

    def _get_python_property_alias(self, obj: Any, property_name: str) -> Any:
        if property_name in ("position_x", "position_y") and hasattr(obj, "get_position"):
            position = obj.get_position()
            axis = "x" if property_name.endswith("_x") else "y"
            if hasattr(position, axis):
                return getattr(position, axis)

        if property_name in ("scale_x", "scale_y") and hasattr(obj, "get_scale"):
            scale = obj.get_scale()
            axis = "x" if property_name.endswith("_x") else "y"
            if hasattr(scale, axis):
                return getattr(scale, axis)

        return _PROPERTY_NOT_FOUND

    def _set_python_property_alias(self, obj: Any, property_name: str, value: Any) -> bool:
        if property_name in ("position_x", "position_y") and hasattr(obj, "get_position") and hasattr(obj, "set_position"):
            position = obj.get_position()
            x = value if property_name == "position_x" else getattr(position, "x", 0.0)
            y = value if property_name == "position_y" else getattr(position, "y", 0.0)
            obj.set_position(x, y)
            return True

        if property_name in ("scale_x", "scale_y") and hasattr(obj, "get_scale") and hasattr(obj, "set_scale"):
            scale = obj.get_scale()
            x = value if property_name == "scale_x" else getattr(scale, "x", 1.0)
            y = value if property_name == "scale_y" else getattr(scale, "y", 1.0)
            obj.set_scale(x, y)
            return True

        return False

    @staticmethod
    def _is_truthy(value: Any) -> bool:
        return bool(value)


_PROPERTY_NOT_FOUND = object()


class ReturnException(Exception):
    def __init__(self, value):
        self.value = value
