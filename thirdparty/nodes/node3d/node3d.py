import math
from typing import Tuple
from thirdparty.nodes.base.node import Node

class Vector3:
    """Clase auxiliar matemática para tres dimensiones (X, Y, Z)."""
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def to_tuple(self) -> Tuple[float, float, float]:
        return (self.x, self.y, self.z)

    def __add__(self, other: 'Vector3') -> 'Vector3':
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)


class Node3D(Node):
    """
    Nodo base para todas las entidades que poseen una representación espacial en 3D.
    Maneja Posición, Rotación (Euler) y Escala en los ejes X, Y, y Z.
    """

    def __init__(self, name: str = "Node3D"):
        super().__init__(name)
        
        # Transformaciones locales
        self.position: Vector3 = Vector3(0.0, 0.0, 0.0)
        self.rotation: Vector3 = Vector3(0.0, 0.0, 0.0) # Rotación en grados (Pitch, Yaw, Roll)
        self.scale: Vector3 = Vector3(1.0, 1.0, 1.0)
        
        self.visible: bool = True

    # --- 📐 Gestión de Posiciones ---

    def get_position(self) -> Vector3:
        return self.position

    def set_position(self, x: float, y: float, z: float):
        self.position.x = float(x)
        self.position.y = float(y)
        self.position.z = float(z)

    def get_global_position(self) -> Vector3:
        """Calcula la posición real acumulada sumando los padres Node3D."""
        global_pos = Vector3(self.position.x, self.position.y, self.position.z)
        current_parent = self.get_parent()

        while current_parent is not None:
            if isinstance(current_parent, Node3D):
                global_pos += current_parent.get_position()
            current_parent = current_parent.get_parent()

        return global_pos

    # --- 🔄 Gestión de Rotaciones ---

    def get_rotation(self) -> Vector3:
        return self.rotation

    def set_rotation(self, x_deg: float, y_deg: float, z_deg: float):
        self.rotation.x = float(x_deg) % 360.0
        self.rotation.y = float(y_deg) % 360.0
        self.rotation.z = float(z_deg) % 360.0

    # --- ⚖️ Gestión de Escalas ---

    def get_scale(self) -> Vector3:
        return self.scale

    def set_scale(self, x: float, y: float, z: float):
        self.scale.x = float(x)
        self.scale.y = float(y)
        self.scale.z = float(z)

    def __str__(self) -> str:
        pos = self.get_position()
        return f"[{self.__class__.__name__}:{self._name} en 3D (X: {pos.x:.1f}, Y: {pos.y:.1f}, Z: {pos.z:.1f})]"