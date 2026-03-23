from thirdparty.math2d import Vector2
from thirdparty.nodes.node2d.node2d import Node2D


class CollisionShape2D(Node2D):
    """
    Forma de colision simple para nodos 2D.
    """

    SHAPE_BOX = "box"
    SHAPE_CIRCLE = "circle"

    def __init__(self, name: str = "CollisionShape2D"):
        super().__init__(name)
        self.shape_type: str = self.SHAPE_BOX
        self.size: Vector2 = Vector2(32.0, 32.0)
        self.disabled: bool = False
        self.debug_visible: bool = True
        self.debug_color = (255, 185, 64)
        self.z_index = 50

    def ready(self):
        super().ready()
        self._sync_with_parent()

    def set_size(self, width: float, height: float):
        self.size.x = float(width)
        self.size.y = float(height)
        self._sync_with_parent()

    def _sync_with_parent(self):
        parent = self.get_parent()
        if parent and hasattr(parent, "size"):
            if hasattr(parent.size, "x") and hasattr(parent.size, "y"):
                parent.size.x = self.size.x
                parent.size.y = self.size.y
            elif isinstance(parent.size, tuple):
                parent.size = (self.size.x, self.size.y)

    def get_half_extents(self) -> Vector2:
        return Vector2(self.size.x * self.scale.x / 2, self.size.y * self.scale.y / 2)

    def _draw(self, render_server):
        if self.disabled or not self.debug_visible:
            return

        global_pos = self.get_global_position()
        if self.shape_type == self.SHAPE_CIRCLE:
            render_server.draw_circle(
                self.debug_color,
                (
                    global_pos.x + (self.size.x / 2),
                    global_pos.y + (self.size.y / 2),
                ),
                self.size.x / 2,
                width=2,
            )
            return

        render_server.draw_rect(
            (global_pos.x, global_pos.y, self.size.x, self.size.y),
            self.debug_color,
            width=2,
            border_radius=6,
        )
