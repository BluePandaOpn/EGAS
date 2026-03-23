from typing import Optional
from thirdparty.nodes.base.node import Node
from thirdparty.math2d import Vector2


class Node2D(Node):
    """
    Nodo base para todas las entidades que poseen una representación espacial en 2D.
    Hereda de Node y añade Posición, Rotación y Escala.
    """

    def __init__(self, name: str = "Node2D"):
        super().__init__(name)
        
        # Atributos de transformación (Locales respecto a su Padre)
        self.position: Vector2 = Vector2.ZERO()
        self.rotation: float = 0.0  # En grados (0° a 360°)
        self.scale: Vector2 = Vector2(1.0, 1.0)
        
        self.z_index: int = 0  # Profundidad de dibujado (Capas)

    # --- 📐 Gestión de Posiciones (Locales y Globales) ---

    def get_position(self) -> Vector2:
        """Retorna la posición local respecto a su padre."""
        return self.position

    def set_position(self, x: float, y: float):
        self.position.x = float(x)
        self.position.y = float(y)

    def get_global_position(self) -> Vector2:
        """
        Calcula la posición real en el mundo sumando recursivamente 
        las posiciones de todos sus padres hacia arriba en el árbol.
        """
        global_pos = Vector2(self.position.x, self.position.y)
        current_parent = self.get_parent()

        while current_parent is not None:
            # Solo sumamos si el padre también tiene posición espacial (es un Node2D)
            if isinstance(current_parent, Node2D):
                global_pos += current_parent.get_position()
            current_parent = current_parent.get_parent()

        return global_pos

    # --- 🔄 Gestión de Rotaciones ---

    def get_rotation(self) -> float:
        """Retorna la rotación local en grados."""
        return self.rotation

    def set_rotation(self, degrees: float):
        self.rotation = float(degrees) % 360.0

    def get_global_rotation(self) -> float:
        """Calcula la rotación acumulada de los padres."""
        global_rot = self.rotation
        current_parent = self.get_parent()

        while current_parent is not None:
            if isinstance(current_parent, Node2D):
                global_rot += current_parent.get_rotation()
            current_parent = current_parent.get_parent()

        return global_rot % 360.0

    # --- ⚖️ Gestión de Escalas ---

    def get_scale(self) -> Vector2:
        return self.scale

    def set_scale(self, x: float, y: float):
        self.scale.x = float(x)
        self.scale.y = float(y)

    # --- 🧭 Utilidades de Movimiento ---

    def look_at(self, target: Vector2):
        """Hace que el nodo apunte rotacionalmente hacia un objetivo Vector2."""
        import math
        global_pos = self.get_global_position()
        dx = target.x - global_pos.x
        dy = target.y - global_pos.y
        # math.atan2 devuelve radianes, pasamos a grados
        angle_radians = math.atan2(dy, dx)
        self.set_rotation(math.degrees(angle_radians))

    def translate(self, offset: Vector2):
        """Desplaza el nodo sumando un desplazamiento."""
        self.position += offset

    def __str__(self) -> str:
        pos = self.get_position()
        return f"[{self.__class__.__name__}:{self._name} en (X: {pos.x:.1f}, Y: {pos.y:.1f})]"