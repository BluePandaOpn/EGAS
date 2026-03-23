from abc import ABC, abstractmethod
from typing import Tuple

class ITexture(ABC):
    """
    Representación abstracta de una imagen cargada en memoria ram/vram.
    """
    @abstractmethod
    def get_width(self) -> int:
        pass

    @abstractmethod
    def get_height(self) -> int:
        pass


class IRenderServer(ABC):
    """
    Servidor gráfico abstracto. Puede implementarse con Pygame, OpenGL, SDL, etc.
    """

    @abstractmethod
    def initialize(self, width: int, height: int, vsync: bool):
        pass

    @abstractmethod
    def begin_frame(self):
        """Limpia la pantalla para un nuevo frame."""
        pass

    @abstractmethod
    def draw_texture(self, texture: ITexture, position: Tuple[float, float], scale: Tuple[float, float], rotation: float):
        """Dibuja una textura en coordenadas bidimensionales."""
        pass

    @abstractmethod
    def draw_rect(self, rect: Tuple[float, float, float, float], color, width: int = 0, border_radius: int = 0):
        """Dibuja un rectangulo solido o solo su borde."""
        pass

    @abstractmethod
    def draw_circle(self, color, center: Tuple[float, float], radius: float, width: int = 0):
        """Dibuja un circulo solido o solo su borde."""
        pass

    @abstractmethod
    def end_frame(self):
        """Vuelca el buffer de dibujo a la pantalla física."""
        pass

    @abstractmethod
    def load_texture(self, path: str) -> ITexture:
        """Carga una imagen del disco duro."""
        pass
