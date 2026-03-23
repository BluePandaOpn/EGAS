import pygame

from egas.core.logger import Logger
from thirdparty.nodes.control.control import Control


class Label(Control):
    """
    Texto de interfaz dibujado en coordenadas de pantalla.
    """

    def __init__(self, name: str = "Label"):
        super().__init__(name)
        self.text = "Hola Mundo"
        self.font_size = 24
        self.font_color = (255, 255, 255)
        self.font_name = None
        self.z_index = 100
        self._font_cache = None
        self._text_surface = None
        self._dirty = True
        Logger.info("Label", f"Nodo Label '{self.get_name()}' instanciado con exito.")

    def _draw(self, render_server):
        if not self.visible:
            return

        if self._dirty or self._text_surface is None:
            self._regenerate_surface()

        if not self._text_surface:
            return

        screen = getattr(render_server, "screen", pygame.display.get_surface())
        if not screen:
            return

        pos = self.get_global_position()
        screen.blit(self._text_surface, (int(pos.x), int(pos.y)))

    def _regenerate_surface(self):
        try:
            self._font_cache = pygame.font.SysFont(self.font_name, int(self.font_size))
            self._text_surface = self._font_cache.render(str(self.text), True, self.font_color)
            self.size.x = float(self._text_surface.get_width())
            self.size.y = float(self._text_surface.get_height())
            self._dirty = False
        except Exception as exc:
            Logger.error("Label", f"Error renderizando el texto '{self.text}': {exc}")

    def set_text(self, new_text: str):
        if str(new_text) != self.text:
            self.text = str(new_text)
            self._dirty = True

    def set_font_size(self, size: int):
        if int(size) != self.font_size:
            self.font_size = int(size)
            self._dirty = True

    def set_color(self, r: int, g: int, b: int):
        new_color = (int(r), int(g), int(b))
        if new_color != self.font_color:
            self.font_color = new_color
            self._dirty = True
