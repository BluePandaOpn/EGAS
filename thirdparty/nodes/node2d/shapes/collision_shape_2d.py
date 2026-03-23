from thirdparty.nodes.node2d.node2d import Node2D
from thirdparty.math2d import Vector2

class CollisionShape2D(Node2D):
    """
    Nodo que define una forma geométrica simple para colisiones (Caja o Círculo).
    Debe ser hijo de un nodo físico (CharacterBody2D, RigidBody2D, etc.).
    """
    SHAPE_BOX = "box"
    SHAPE_CIRCLE = "circle"

    def __init__(self, name: str = "CollisionShape2D"):
        super().__init__(name)
        
        self.shape_type: str = self.SHAPE_BOX
        
        # Si es BOX: (Ancho, Alto). Si es CIRCLE: (Radio, Radio).
        self.size: Vector2 = Vector2(32.0, 32.0)
        
        self.disabled: bool = False # Para desactivar la colisión temporalmente

    def ready(self):
        super().ready()
        self._sync_with_parent()

    def _sync_with_parent(self):
        """
        Busca si su padre es un cuerpo físico y le pasa las dimensiones 
        de esta forma geométrica automáticamente.
        """
        parent = self.get_parent()
        if parent and hasattr(parent, 'size'):
            # Pasamos el tamaño escalado por la escala de este propio nodo Shape
            scaled_w = self.size.x * self.scale.x
            scaled_h = self.size.y * self.scale.y
            parent.size = (scaled_w, scaled_h)

    def get_half_extents(self) -> Vector2:
        """Retorna la mitad del tamaño (útil para cálculos matemáticos del Solver)."""
        return Vector2(self.size.x * self.scale.x / 2, self.size.y * self.scale.y / 2)