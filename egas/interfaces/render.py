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
    def end_frame(self):
        """Vuelca el buffer de dibujo a la pantalla física."""
        pass

    @abstractmethod
    def load_texture(self, path: str) -> ITexture:
        """Carga una imagen del disco duro."""
        pass