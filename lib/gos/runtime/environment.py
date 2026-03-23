from typing import Dict, Any, Optional
from lib.gos.lexer.token import Token

class Environment:
    """
    Gestiona la tabla de símbolos (variables y funciones) de GOS en tiempo de ejecución.
    Soporta ámbitos anidados (Scopes lógicos por bloques).
    """
    def __init__(self, enclosing: Optional['Environment'] = None):
        self.values: Dict[str, Any] = {}
        self.enclosing = enclosing # El entorno padre (ej: el global para un if local)

    def define(self, name: str, value: Any):
        """Crea o sobreescribe una variable en el ámbito actual."""
        self.values[name] = value

    def get(self, name_token: Token) -> Any:
        """Busca una variable en este entorno. Si no la halla, busca en el padre."""
        name = name_token.lexeme
        if name in self.values:
            return self.values[name]

        if self.enclosing is not None:
            return self.enclosing.get(name_token)

        raise RuntimeError(f"Variable '{name}' no definida en la línea {name_token.line}.")

    def assign(self, name_token: Token, value: Any):
        """Actualiza el valor de una variable existente (no la crea)."""
        name = name_token.lexeme
        if name in self.values:
            self.values[name] = value
            return

        if self.enclosing is not None:
            self.enclosing.assign(name_token, value)
            return

        raise RuntimeError(f"No se puede asignar a una variable no definida '{name}' en la línea {name_token.line}.")