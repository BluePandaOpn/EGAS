from thirdparty.nodes.node2d.node2d import Node2D
from thirdparty.math2d import Vector2

class CharacterBody2D(Node2D):
    """
    Cuerpo físico diseñado para personajes controlados por el jugador o la IA.
    Se mueve por código, pero obedece colisiones con el entorno.
    """
    def __init__(self, name: str = "CharacterBody2D"):
        super().__init__(name)
        
        self.is_static = False
        self.velocity: Vector2 = Vector2.ZERO()
        self.size = (32, 32)
        
        # Atributos de ayuda para el gameplay
        self.is_on_floor: bool = False

    def get_velocity(self):
        return self.velocity.to_tuple()

    def set_velocity(self, vx: float, vy: float):
        self.velocity.x = vx
        self.velocity.y = vy

    def move_and_slide(self):
        """
        Calcula el movimiento respetando colisiones (Deslizar por paredes).
        Este método es el más famoso de motores como Godot.
        Llamará al resolvedor de colisiones para deslizar al personaje en lugar de atascarlo.
        """
        # La lógica de deslizar se delega al CollisionSolver de egas/physics/solver.py
        pass

    def _custom_process(self, delta: float):
        # El programador manipula character.velocity.x / y desde GOS
        # y llama a move_and_slide()
        pass