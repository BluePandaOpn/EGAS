import pygame
from thirdparty.nodes.control.control import Control

class Label(Control):
    """
    Nodo de UI para pintar texto plano en la pantalla utilizando fuentes del sistema.
    """
    def __init__(self, name: str = "Label"):
        super().__init__(name)
        
        self.text: str = "Texto de Prueba"
        self.font_size: int = 24
        self.font_color = (255, 255, 255) # Blanco
        self.font_name: str = None # Usará la fuente por defecto del sistema
        
        self._cached_surface = None

    def draw(self, render_server):
        if not self.visible or not self.text:
            return

        # Para pintar texto, aprovechamos directamente las capacidades de Pygame
        # (Aunque en un motor purista esto se delegaría al RenderServer)
        if not self._cached_surface:
            font = pygame.font.SysFont(self.font_name, self.font_size)
            self._cached_surface = font.render(self.text, True, self.font_color)
            
            # Auto-ajustar el tamaño del control al tamaño del texto renderizado
            self.size.x = self._cached_surface.get_width()
            self.size.y = self._cached_surface.get_height()

        # Enviar al render_server
        # Creamos una ITexture al vuelo para pintarlo
        from egas.render.texture import PygameTexture
        txt_texture = PygameTexture(self._cached_surface, f"label_{self.get_name()}")
        
        render_server.draw_texture(
            texture=txt_texture,
            position=self.get_global_position().to_tuple(),
            scale=(1.0, 1.0),
            rotation=0.0
        )

    def set_text(self, new_text: str):
        if self.text != new_text:
            self.text = new_text
            self._cached_surface = None # Forzar regeneración del texto