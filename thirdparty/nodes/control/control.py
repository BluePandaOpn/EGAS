from thirdparty.nodes.base.node import Node
from thirdparty.math2d import Vector2

class Control(Node):
    """
    Nodo base para todos los elementos de Interfaz de Usuario (UI).
    Usa coordenadas de pantalla fijas en lugar de coordenadas de mundo.
    """
    def __init__(self, name: str = "Control"):
        super().__init__(name)
        
        self.position: Vector2 = Vector2.ZERO() # Posición en pantalla (X, Y)
        self.size: Vector2 = Vector2(100.0, 40.0) # Ancho y Alto del control
        
        self.visible: bool = True
        self.z_index: int = 10 # Se dibuja por encima del juego

    def get_global_position(self) -> Vector2:
        """Calcula la posición de pantalla sumando los desplazamientos de controles padres."""
        global_pos = Vector2(self.position.x, self.position.y)
        current_parent = self.get_parent()

        while current_parent is not None:
            if isinstance(current_parent, Control):
                global_pos += current_parent.position
            current_parent = current_parent.get_parent()

        return global_pos

    def get_rect(self):
        """Retorna el rectángulo (x, y, ancho, alto) en pantalla global."""
        pos = self.get_global_position()
        return (pos.x, pos.y, self.size.x, self.size.y)

    def is_mouse_over(self) -> bool:
        """Verifica si el mouse está encima de este control de UI."""
        from thirdparty.input_system import InputSystem
        mouse_pos = InputSystem.get_mouse_pos()
        x, y, w, h = self.get_rect()
        
        return (x <= mouse_pos.x <= x + w) and (y <= mouse_pos.y <= y + h)