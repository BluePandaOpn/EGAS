from typing import List
from thirdparty.nodes.node2d.node2d import Node2D
from thirdparty.math2d import Vector2

class CollisionPolygon2D(Node2D):
    """
    Define un área de colisión basada en una lista de puntos (polígono).
    Ideal para formas complejas como naves triangulares o terrenos irregulares.
    """
    def __init__(self, name: str = "CollisionPolygon2D"):
        super().__init__(name)
        
        # Lista de Vector2 que definen los vértices del polígono
        self.polygon_points: List[Vector2] = [
            Vector2(0, 0),
            Vector2(32, 0),
            Vector2(32, 32),
            Vector2(0, 32)
        ]
        
        self.disabled: bool = False

    def get_global_points(self) -> List[Vector2]:
        """
        Calcula la posición matemática real en el mundo de cada vértice del polígono,
        aplicando la rotación y la posición del objeto padre.
        """
        import math
        global_points = []
        base_pos = self.get_global_position()
        rad_rot = math.radians(self.get_global_rotation())

        for pt in self.polygon_points:
            # Aplicar escala
            sx = pt.x * self.scale.x
            sy = pt.y * self.scale.y

            # Aplicar Rotación trigonométrica
            rx = sx * math.cos(rad_rot) - sy * math.sin(rad_rot)
            ry = sx * math.sin(rad_rot) + sy * math.cos(rad_rot)

            # Aplicar traslación a la posición del mundo
            global_points.append(Vector2(rx + base_pos.x, ry + base_pos.y))

        return global_points

    def ready(self):
        super().ready()
        self._sync_bounding_box_with_parent()

    def _sync_bounding_box_with_parent(self):
        """
        Calcula la caja AABB máxima que contiene a todo el polígono 
        para pasársela al padre.
        """
        if not self.polygon_points: return

        pts = self.get_global_points()
        min_x = min(p.x for p in pts)
        max_x = max(p.x for p in pts)
        min_y = min(p.y for p in pts)
        max_y = max(p.y for p in pts)

        parent = self.get_parent()
        if parent and hasattr(parent, 'size'):
            parent.size = (max_x - min_x, max_y - min_y)