from typing import Any, Dict, Optional

from lib.gos.lexer.token import Token
from lib.gos.runtime.errors import GOSRuntimeError


class Environment:
    """Tabla de simbolos de GOS con soporte para constantes."""

    def __init__(self, enclosing: Optional["Environment"] = None):
        self.values: Dict[str, Any] = {}
        self.constants: set[str] = set()
        self.enclosing = enclosing

    def define(self, name: str, value: Any, is_const: bool = False):
        self.values[name] = value
        if is_const:
            self.constants.add(name)
        else:
            self.constants.discard(name)

    def get(self, name_token: Token) -> Any:
        name = name_token.lexeme
        if name in self.values:
            return self.values[name]

        if self.enclosing is not None:
            return self.enclosing.get(name_token)

        raise GOSRuntimeError(f"Variable '{name}' no definida.", line=name_token.line)

    def assign(self, name_token: Token, value: Any):
        name = name_token.lexeme
        if name in self.values:
            if name in self.constants:
                raise GOSRuntimeError(f"No se puede reasignar la constante '{name}'.", line=name_token.line)
            self.values[name] = value
            return

        if self.enclosing is not None:
            self.enclosing.assign(name_token, value)
            return

        raise GOSRuntimeError(f"No se puede asignar a la variable no definida '{name}'.", line=name_token.line)
