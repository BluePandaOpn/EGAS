from egas.core.logger import Logger
from thirdparty.nodes.node2d.node2d import Node2D


class Camera2D(Node2D):
    """
    Nodo de camara para entornos 2D.
    """

    def __init__(self):
        super().__init__()
        self.set_name("Camera2D")
        self.active = False
        self.target_node = None
        self.smoothing = 0.1
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.zoom = 1.0
        self.limit_left = -1000000.0
        self.limit_right = 1000000.0
        self.limit_top = -1000000.0
        self.limit_bottom = 1000000.0
        Logger.info("Camera2D", "Nodo Camera2D instanciado con exito.")

    def process(self, delta: float):
        super().process(delta)

        if self.target_node:
            target_pos = self.target_node.get_position() if hasattr(self.target_node, "get_position") else None
            target_x = getattr(target_pos, "x", 0.0) + self.offset_x
            target_y = getattr(target_pos, "y", 0.0) + self.offset_y

            current_pos = self.get_position()
            new_x = current_pos.x + (target_x - current_pos.x) * self.smoothing
            new_y = current_pos.y + (target_y - current_pos.y) * self.smoothing
            self.set_position(new_x, new_y)
            self._clamp_to_limits()

    def _clamp_to_limits(self):
        position = self.get_position()
        x = position.x
        y = position.y

        if x < self.limit_left:
            x = self.limit_left
        elif x > self.limit_right:
            x = self.limit_right

        if y < self.limit_top:
            y = self.limit_top
        elif y > self.limit_bottom:
            y = self.limit_bottom

        self.set_position(x, y)

    def set_target(self, node):
        self.target_node = node

    def set_limits(self, left: float, top: float, right: float, bottom: float):
        self.limit_left = left
        self.limit_top = top
        self.limit_right = right
        self.limit_bottom = bottom

    def set_zoom(self, zoom_factor: float):
        if zoom_factor > 0:
            self.zoom = zoom_factor
