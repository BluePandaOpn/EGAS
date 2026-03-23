from thirdparty.math2d import Vector2
from thirdparty.nodes.base.node import Node


class Control(Node):
    """
    Nodo base para todos los elementos de interfaz.
    Usa coordenadas de pantalla y puede anidarse bajo otros Control.
    """

    def __init__(self, name: str = "Control"):
        super().__init__(name)
        self.position: Vector2 = Vector2.ZERO()
        self.size: Vector2 = Vector2(100.0, 40.0)
        self.visible: bool = True
        self.z_index: int = 10

    def get_position(self) -> Vector2:
        return self.position

    def set_position(self, x: float, y: float):
        self.position.x = float(x)
        self.position.y = float(y)

    def set_size(self, width: float, height: float):
        self.size.x = float(width)
        self.size.y = float(height)

    def get_global_position(self) -> Vector2:
        global_pos = Vector2(self.position.x, self.position.y)
        current_parent = self.get_parent()

        while current_parent is not None:
            if isinstance(current_parent, Control):
                global_pos += current_parent.position
            current_parent = current_parent.get_parent()

        return global_pos

    def get_rect(self):
        pos = self.get_global_position()
        return (pos.x, pos.y, self.size.x, self.size.y)

    def is_mouse_over(self) -> bool:
        from thirdparty.input_system import InputSystem

        mouse_pos = InputSystem.get_mouse_pos()
        x, y, w, h = self.get_rect()
        return (x <= mouse_pos.x <= x + w) and (y <= mouse_pos.y <= y + h)
