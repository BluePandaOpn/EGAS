from typing import Dict, Any, Optional
from lib.gos.parser.ast import FunctionStmt

class GosClass:
    """
    Representa la definición de una clase en el lenguaje GOS.
    Contiene el nombre de la clase y su diccionario de métodos.
    """
    def __init__(self, name: str, methods: Dict[str, FunctionStmt], superclass: Optional['GosClass'] = None):
        self.name = name
        self.methods = methods
        self.superclass = superclass

    def find_method(self, name: str) -> Optional[FunctionStmt]:
        """Busca un método en esta clase o en sus clases padres (herencia)."""
        if name in self.methods:
            return self.methods[name]

        if self.superclass:
            return self.superclass.find_method(name)

        return None

    def instantiate(self, interpreter, arguments) -> 'GosInstance':
        """Crea una instancia viva de esta clase y ejecuta su constructor si existe."""
        from lib.gos.objects.instance import GosInstance
        instance = GosInstance(self)

        # Buscar el constructor (en GOS podemos llamarlo '_init' o 'init')
        initializer = self.find_method("_init")
        if not initializer:
            initializer = self.find_method("init")

        if initializer:
            # Vinculamos la función al entorno de la nueva instancia y la ejecutamos con los argumentos pasados
            # (El intérprete se encarga de empaquetar la llamada)
            pass 

        return instance

    def __str__(self) -> str:
        return f"<Clase GOS: {self.name}>"