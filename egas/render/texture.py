import pygame
from egas.interfaces.render import ITexture

class PygameTexture(ITexture):
    """
    Implementación de ITexture utilizando Pygame Surface.
    Encapsula una imagen cargada de disco duro lista para renderizar.
    """
    def __init__(self, surface: pygame.Surface, path: str):
        self._surface = surface
        self._path = path
        self._width = surface.get_width()
        self._height = surface.get_height()

    def get_width(self) -> int:
        return self._width

    def get_height(self) -> int:
        return self._height

    def get_surface(self) -> pygame.Surface:
        """Retorna la superficie nativa de Pygame."""
        return self._surface

    def get_path(self) -> str:
        return self._path