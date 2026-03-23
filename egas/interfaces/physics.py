from abc import ABC, abstractmethod
from typing import Tuple

class IBody(ABC):
    """
    Representación de un objeto físico en el espacio.
    """
    @abstractmethod
    def get_position(self) -> Tuple[float, float]:
        pass

    @abstractmethod
    def set_position(self, x: float, y: float):
        pass

    @abstractmethod
    def get_velocity(self) -> Tuple[float, float]:
        pass

    @abstractmethod
    def set_velocity(self, vx: float, vy: float):
        pass


class IPhysicsManager(ABC):
    """
    Simulador que procesa gravedades y colisiones por frame.
    """

    @abstractmethod
    def add_body(self, body: IBody):
        pass

    @abstractmethod
    def remove_body(self, body: IBody):
        pass

    @abstractmethod
    def update(self, delta_time: float):
        """Avanza la simulación física un paso de tiempo (ticks)."""
        pass

    @abstractmethod
    def check_collision(self, body_a: IBody, body_b: IBody) -> bool:
        """Resuelve si dos cuerpos están chocando."""
        pass