from typing import Any, Dict

class GosInstance:
    """
    Representa un objeto instanciado de una clase GOS en el Heap de memoria.
    Mapea campos (variables de estado) y métodos asociados a su clase.
    """
    def __init__(self, gos_class):
        self.gos_class = gos_class
        self.fields: Dict[str, Any] = {} # Variables de la instancia (self.vida = 100)

    def get(self, name_token):
        """Obtiene una propiedad o un método ligado a esta instancia."""
        name = name_token.lexeme

        # 1. ¿Es una variable de la instancia?
        if name in self.fields:
            return self.fields[name]

        # 2. ¿Es un método de su clase?
        method = self.gos_class.find_method(name)
        if method:
            return self._bind_method(method)

        raise RuntimeError(f"Propiedad o método '{name}' no definido en el objeto de la clase {self.gos_class.name}.")

    def set(self, name_token, value: Any):
        """Asigna o actualiza una propiedad en la instancia."""
        self.fields[name_token.lexeme] = value

    def _bind_method(self, method_stmt):
        """
        Amarra la palabra 'self' de un método a esta instancia específica 
        para que cuando se ejecute sepa a qué objeto pertenece.
        """
        # Aquí el intérprete vincula el entorno de la función al de esta instancia.
        return method_stmt

    def __str__(self) -> str:
        return f"<Instancia de {self.gos_class.name}>"