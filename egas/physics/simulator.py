from typing import List
from config.settings import Settings
from egas.interfaces.physics import IPhysicsManager, IBody
from egas.physics.solver import CollisionSolver
from egas.core.logger import Logger

class PhysicsSimulator(IPhysicsManager):
    """
    Administrador del mundo físico del motor EGAS.
    Aplica gravedad, procesa velocidades y resuelve colisiones usando el Solver.
    """

    def __init__(self):
        self.bodies: List[IBody] = []
        self.gravity_scale = Settings.GRAVITY * Settings.PIXELS_PER_METER # m/s^2 a px/s^2
        Logger.info("Physics", f"Simulador físico inicializado con gravedad de {Settings.GRAVITY} m/s²")

    def add_body(self, body: IBody):
        if body not in self.bodies:
            self.bodies.append(body)

    def remove_body(self, body: IBody):
        if body in self.bodies:
            self.bodies.remove(body)

    def update(self, delta_time: float):
        """
        Avanza la simulación física un Tick de reloj.
        """
        # 1. Aplicar Gravedad y Movimiento
        for body in self.bodies:
            # Si el cuerpo no es estático (piso), aplicarle gravedad
            if getattr(body, 'is_static', False) == False:
                vx, vy = body.get_velocity()
                vy += self.gravity_scale * delta_time # caida libre
                body.set_velocity(vx, vy)

            # Mover el cuerpo según su velocidad
            x, y = body.get_position()
            vx, vy = body.get_velocity()
            body.set_position(x + vx * delta_time, y + vy * delta_time)

        # 2. Comprobar Colisiones entre todos los cuerpos (O(N^2) ingenuo por ahora)
        for i in range(len(self.bodies)):
            for j in range(i + 1, len(self.bodies)):
                body_a = self.bodies[i]
                body_b = self.bodies[j]

                if self.check_collision(body_a, body_b):
                    self._on_collision_detected(body_a, body_b)

    def check_collision(self, body_a: IBody, body_b: IBody) -> bool:
        """
        Delega el chequeo geométrico al Solver.
        """
        # Extraer tamaños (estos atributos vendrán de los Nodos del thirdparty)
        size_a = getattr(body_a, 'size', (32, 32))
        size_b = getattr(body_b, 'size', (32, 32))

        return CollisionSolver.aabb_check(
            body_a.get_position(), size_a,
            body_b.get_position(), size_b
        )

    def _on_collision_detected(self, body_a: IBody, body_b: IBody):
        """
        Lógica de respuesta de colisión cuando dos cuerpos impactan.
        """
        # Aquí puedes llamar al solver.resolve_elastic_collision, detener movimiento, 
        # o lanzar una señal al lenguaje GOS para que el programador responda.
        pass