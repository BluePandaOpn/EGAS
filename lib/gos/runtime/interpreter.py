import os
from typing import List, Any

try:
    import requests
except ModuleNotFoundError:
    requests = None
from lib.gos.lexer.lexer import Lexer
from lib.gos.parser.parser import Parser
from lib.gos.parser.ast import *
from lib.gos.lexer.token import TokenType
from lib.gos.runtime.environment import Environment
from lib.gos.runtime.builtins import BUILTINS
from lib.gos.stdlib import get_stdlib_extensions
from lib.gos.objects.instance import GosInstance


class Interpreter:
    """
    El Intérprete final de GOS. Recorre el AST y ejecuta la lógica real en la computadora.
    Conecta los scripts .gs con el motor EGAS y la Librería Estándar (stdlib).
    """
    def __init__(self):
        self.globals = Environment()
        self.environment = self.globals
        self._load_builtins()

    def _load_builtins(self):
        """Inyecta las funciones matemáticas y de sistema por defecto (Python y stdlib)."""
        # 1. Cargar funciones nativas básicas (print, sin, cos, etc.)
        for name, func in BUILTINS.items():
            self.globals.define(name, func)

        # 2. 🚀 Cargar las extensiones de la Librería Estándar (IO, JSON, etc.)
        stdlib_py = get_stdlib_extensions()
        for name, func in stdlib_py.items():
            self.globals.define(name, func)

    def run(self, statements: List[Stmt]):
        """Punto de entrada para ejecutar una lista de sentencias de un script."""
        try:
            for stmt in statements:
                self._execute(stmt)
        except Exception as e:
            print(f"[GOS Interpreter] Error de ejecución: {e}")

    # --- 🔥 NUEVOS MÉTODOS PARA EL CICLO DE VIDA (Engine / SceneTree) ---

    def call_function(self, func_name: str, args: List[Any] = None) -> Any:
        """
        Permite al motor llamar funciones de GOS directamente (ej: _process, _input).
        Busca la función en el entorno global y la ejecuta.
        """
        if args is None:
            args = []

        try:
            # Buscamos la función en el entorno
            # Como Environment no tiene un método directo de 'has' sin lanzar error, lo intentamos capturar
            try:
                # Usamos una expresión falsa para buscarlo
                from lib.gos.lexer.token import Token
                dummy_token = Token(TokenType.IDENTIFIER, func_name, None, 0)
                callee = self.globals.get(dummy_token)
            except RuntimeError:
                return None # La función no existe en el script (ej: el usuario no programó _input)

            # Si la encontramos y es una declaración de función de GOS
            if isinstance(callee, FunctionStmt):
                env_funcion = Environment(self.globals)
                
                for i, param in enumerate(callee.params):
                    if i < len(args):
                        env_funcion.define(param.lexeme, args[i])

                try:
                    self._execute_block(callee.body, env_funcion)
                except ReturnException as r:
                    return r.value
                
                return None
                
        except Exception as e:
            print(f"[GOS Interpreter] Error llamando a la función '{func_name}': {e}")
        
        return None


    # --- 🏗️ EJECUTOR DE SENTENCIAS (Acciones / Statements) ---

    def _execute(self, stmt: Stmt):
        if isinstance(stmt, ExpressionStmt): 
            self._evaluate(stmt.expression)
        elif isinstance(stmt, VarStmt): 
            self._execute_var(stmt)
        elif isinstance(stmt, BlockStmt): 
            self._execute_block(stmt.statements, Environment(self.environment))
        elif isinstance(stmt, IfStmt): 
            self._execute_if(stmt)
        elif isinstance(stmt, WhileStmt): 
            self._execute_while(stmt)
        elif isinstance(stmt, FunctionStmt): 
            self._execute_function(stmt)
        elif isinstance(stmt, ReturnStmt):
            self._execute_return(stmt)
        elif isinstance(stmt, ImportStmt):
            self._execute_import(stmt)

    def _execute_var(self, stmt: VarStmt):
        value = self._evaluate(stmt.initializer) if stmt.initializer else None
        self.environment.define(stmt.name.lexeme, value)
    
    def _execute_import(self, stmt: ImportStmt):
        """
        Resuelve la importación de archivos locales (res://) 
        o remotos (http://, https://) y combina las funciones/variables.
        """
        ruta_original = self._evaluate(stmt.path) # Evaluamos el String del path
        codigo_fuente = ""

        # 🌐 CASO 1: Es una URL de Internet
        if ruta_original.startswith("http://") or ruta_original.startswith("https://"):
            if requests is None:
                print("[GOS Import ERROR] El soporte HTTP requiere instalar 'requests'.")
                return
            print(f"[GOS Import INFO] Descargando módulo remoto: {ruta_original}")
            try:
                respuesta = requests.get(ruta_original)
                if respuesta.status_code == 200:
                    codigo_fuente = respuesta.text
                else:
                    print(f"[GOS Import ERROR] Error al descargar URL. Código HTTP: {respuesta.status_code}")
                    return
            except Exception as e:
                print(f"[GOS Import ERROR] Error de red intentando importar: {e}")
                return

        # 🏠 CASO 2: Es un recurso local del proyecto (res://)
        elif ruta_original.startswith("res://"):
            # Traducimos "res://" a la carpeta raíz donde se ejecuta run.py en tu PC
            ruta_limpia = ruta_original.replace("res://", "")
            ruta_absoluta = os.path.join(os.getcwd(), ruta_limpia)

            print(f"[GOS Import INFO] Cargando módulo local: {ruta_absoluta}")
            
            if not os.path.exists(ruta_absoluta):
                print(f"[GOS Import ERROR] El archivo local '{ruta_original}' no existe.")
                return

            try:
                with open(ruta_absoluta, 'r', encoding='utf-8') as f:
                    codigo_fuente = f.read()
            except Exception as e:
                print(f"[GOS Import ERROR] Error leyendo archivo local: {e}")
                return

        else:
            print(f"[GOS Import ERROR] Prefijo de ruta desconocido '{ruta_original}'. Usa res:// o http://")
            return

        # 🧠 PROCESAMIENTO DEL NUEVO CÓDIGO
        if codigo_fuente:
            # 1. Pasamos el texto descargado/leído al Lexer para sacar tokens
            lexer = Lexer(codigo_fuente)
            tokens = lexer.tokenize()

            # 2. Pasamos los tokens al Parser para sacar el Árbol Sintáctico (AST)
            parser = Parser(tokens)
            sentencias_del_modulo = parser.parse()

            # 3. Ejecutamos el módulo usando el MISMO entorno del intérprete actual para heredar funciones
            for modulo_stmt in sentencias_del_modulo:
                self._execute(modulo_stmt)
                
            print(f"[GOS Import SUCCESS] ¡Módulo '{ruta_original}' importado y combinado con éxito!")

    def _execute_block(self, statements: List[Stmt], new_env: Environment):
        previous_env = self.environment
        try:
            self.environment = new_env
            for statement in statements:
                self._execute(statement)
        finally:
            self.environment = previous_env # Restablecer el Scope al salir de la llave }

    def _execute_if(self, stmt: IfStmt):
        if self._evaluate(stmt.condition):
            self._execute(stmt.then_branch)
        elif stmt.else_branch:
            self._execute(stmt.else_branch)

    def _execute_while(self, stmt: WhileStmt):
        while self._evaluate(stmt.condition):
            self._execute(stmt.body)

    def _execute_function(self, stmt: FunctionStmt):
        # Guardamos la declaración de la función en la memoria del entorno
        self.environment.define(stmt.name.lexeme, stmt)

    def _execute_return(self, stmt: ReturnStmt):
        value = self._evaluate(stmt.value) if stmt.value else None
        # Para salir inmediatamente de la ejecución de una función, Python utiliza Excepciones de control.
        # Crearemos una excepción interna para romper el flujo.
        raise ReturnException(value)


    # --- 📐 EVALUADOR DE EXPRESIONES (Valores matemáticos / Expressions) ---

    def _evaluate(self, expr: Expr) -> Any:
        if isinstance(expr, LiteralExpr): return expr.value
        elif isinstance(expr, GroupingExpr): return self._evaluate(expr.expression)
        elif isinstance(expr, VariableExpr): return self.environment.get(expr.name)
        elif isinstance(expr, BinaryExpr): return self._evaluate_binary(expr)
        elif isinstance(expr, CallExpr): return self._evaluate_call(expr)
        elif isinstance(expr, GetExpr): return self._evaluate_get(expr)
        elif isinstance(expr, SetExpr): return self._evaluate_set(expr)
        return None

    def _evaluate_binary(self, expr: BinaryExpr) -> Any:
        left = self._evaluate(expr.left)
        
        # 🆕 SOPORTE PARA EL OPERADOR 'is' (Comparación de Clases de Eventos)
        if expr.operator.lexeme == "is":
            right_class_name = expr.right.name.lexeme if isinstance(expr.right, VariableExpr) else str(self._evaluate(expr.right))
            if left is None: return False
            return left.__class__.__name__ == right_class_name

        right = self._evaluate(expr.right)
        op = expr.operator.type

        if op == TokenType.PLUS: return left + right
        if op == TokenType.MINUS: return left - right
        if op == TokenType.STAR: return left * right
        if op == TokenType.SLASH: 
            if right == 0: raise ZeroDivisionError("División por cero en GOS.")
            return left / right
        
        # Comparaciones lógicas
        if op == TokenType.GREATER: return left > right
        if op == TokenType.GREATER_EQUALS: return left >= right
        if op == TokenType.LESS: return left < right
        if op == TokenType.LESS_EQUALS: return left <= right
        if op == TokenType.EQUALS_EQUALS: return left == right
        if op == TokenType.BANG_EQUALS: return left != right
        return None

    def _evaluate_call(self, expr: CallExpr) -> Any:
        callee = self._evaluate(expr.callee)
        args = [self._evaluate(arg) for arg in expr.arguments]

        # 1. ¿Es una función de Python nativa (Builtin o STDLIB)?
        if callable(callee): 
            return callee(*args)
        
        # 2. ¿Es una función GOS definida por el usuario?
        if isinstance(callee, FunctionStmt):
            env_funcion = Environment(self.globals) # Scope fresco para la función
            
            # Mapeamos argumentos a parámetros
            for i, param in enumerate(callee.params):
                if i < len(args):
                    env_funcion.define(param.lexeme, args[i])

            # Ejecutamos el cuerpo capturando el ReturnException
            try:
                self._execute_block(callee.body, env_funcion)
            except ReturnException as r:
                return r.value
                
            return None

        raise RuntimeError(f"El objeto no es llamable (callable).")

    def _evaluate_get(self, expr: GetExpr) -> Any:
        obj = self._evaluate(expr.obj)
        return self._get_property(obj, expr.name)

    def _evaluate_set(self, expr: SetExpr) -> Any:
        value = self._evaluate(expr.value)
        if isinstance(expr.obj, VariableExpr) and expr.obj.name.lexeme == expr.name.lexeme:
            self.environment.assign(expr.name, value)
            return value

        obj = self._evaluate(expr.obj)
        return self._set_property(obj, expr.name, value)

    def _get_property(self, obj: Any, name_token) -> Any:
        property_name = name_token.lexeme

        if isinstance(obj, GosInstance):
            return obj.get(name_token)

        alias_value = self._get_python_property_alias(obj, property_name)
        if alias_value is not _PROPERTY_NOT_FOUND:
            return alias_value

        if isinstance(obj, dict) and property_name in obj:
            return obj[property_name]

        if hasattr(obj, property_name):
            return getattr(obj, property_name)

        raise RuntimeError(f"Propiedad '{property_name}' no encontrada en el objeto.")

    def _set_property(self, obj: Any, name_token, value: Any) -> Any:
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
            raise RuntimeError(f"No se puede asignar la propiedad '{property_name}' al objeto.")


    # Compatibilidad entre propiedades estilo escena y nodos Python.
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


_PROPERTY_NOT_FOUND = object()


# --- 🛑 EXCEPCIÓN DE CONTROL PARA RETURNS ---
class ReturnException(Exception):
    """Excepción de control para romper la ejecución secuencial y devolver un valor de una función."""
    def __init__(self, value):
        self.value = value
