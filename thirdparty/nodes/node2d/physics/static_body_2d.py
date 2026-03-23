from thirdparty.nodes.node2d.node2d import Node2D

class StaticBody2D(Node2D):
    """
    Representa un cuerpo físico estático (Paredes, Suelos, Plataformas).
    No responde a la gravedad ni a fuerzas aplicadas por el simulador físico.
    """
    def __init__(self, name: str = "StaticBody2D"):
        super().__init__(name)
        
        # Propiedades para el simulador físico
        self.is_static = True
        self.velocity = (0.0, 0.0) # No se mueve
        self.size = (32, 32)        # Tamaño de caja AABB por defecto

    def get_velocity(self):
        return self.velocity

    def set_velocity(self, vx: float, vy: float):
        pass # Ignoramos intentos de moverlo por velocidad física

    def ready(self):
        super().ready()
        # Aquí más adelante se puede registrar automáticamente en el PhysicsManager