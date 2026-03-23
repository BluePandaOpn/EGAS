from thirdparty.nodes.node2d.node2d import Node2D
from thirdparty.math2d import Vector2

class RigidBody2D(Node2D):
    """
    Cuerpo físico dinámico gobernado al 100% por el simulador de físicas.
    Cae por gravedad y colisiona automáticamente.
    """
    def __init__(self, name: str = "RigidBody2D"):
        super().__init__(name)
        
        self.is_static = False
        self.mass: float = 1.0
        self.velocity: Vector2 = Vector2.ZERO()
        self.size = (32, 32) # Tamaño de caja AABB por defecto

    def get_velocity(self):
        return self.velocity.to_tuple()

    def set_velocity(self, vx: float, vy: float):
        self.velocity.x = vx
        self.velocity.y = vy

    def apply_impulse(self, impulse: Vector2):
        """Aplica una fuerza instantánea basada en la masa (F = m * a)."""
        if self.mass > 0:
            self.velocity += impulse / self.mass

    def _custom_process(self, delta: float):
        # El PhysicsSimulator se encarga de cambiar la posición. 
        # Aquí solo leemos la nueva posición calculada por el simulador.
        pass