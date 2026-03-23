import pygame
from thirdparty.nodes.node2d.node2d import Node2D
from egas.core.logger import Logger


class Label(Node2D):
    """
    Nodo Label para el motor EGAS.
    Permite renderizar texto en pantalla usando las fuentes de Pygame.
    """

    def __init__(self):
        super().__init__()
        self.set_name("Label")

        # --- Propiedades de Texto ---
        self.text = "Hola Mundo"
        self.font_size = 24
        self.font_color = (255, 255, 255) # Blanco por defecto
        self.font_name = None             # None usa la fuente por defecto de Pygame

        # --- Cache del renderizado (Para no saturar la CPU) ---
        self._font_cache = None
        self._text_surface = None
        self._dirty = True # Bandera para saber si el texto cambió y hay que redibujarlo

        Logger.info("Label", "Nodo Label instanciado con éxito.")

    def process(self, delta: float):
        """Lógica por frame."""
        super().process(delta)

    def _draw(self, render_server):
        """
        Dibuja el texto en la pantalla usando Pygame.
        Esta función la llamará automáticamente el SceneTree.
        """
        # 1. Si el texto o tamaño cambió, regeneramos la superficie en RAM
        if self._dirty or self._text_surface is None:
            self._regenerate_surface()

        # 2. Dibujamos en la pantalla si la superficie es válida y tenemos el display de pygame
        if self._text_surface:
            # Obtenemos la pantalla principal de Pygame desde tu render_server
            screen = getattr(render_server, "screen", pygame.display.get_surface())
            
            if screen:
                # Calculamos la posición final sumando la posición global de la UI
                pos_x = self.position_x
                pos_y = self.position_y
                screen.blit(self._text_surface, (pos_x, pos_y))

    def _regenerate_surface(self):
        """Genera la imagen de los píxeles de las letras usando Pygame."""
        try:
            # Crear o cargar la fuente
            self._font_cache = pygame.font.SysFont(self.font_name, self.font_size)
            
            # Crear la superficie de imagen con el texto
            self._text_surface = self._font_cache.render(self.text, True, self.font_color)
            self._dirty = False
        except Exception as e:
            Logger.error("Label", f"Error renderizando el texto '{self.text}': {e}")

    # --- 🛠️ Funciones de Control accesibles desde GOS ---

    def set_text(self, new_text: str):
        """Cambia el texto que se muestra."""
        if str(new_text) != self.text:
            self.text = str(new_text)
            self._dirty = True

    def set_font_size(self, size: int):
        """Cambia el tamaño de la letra."""
        if size != self.font_size:
            self.font_size = size
            self._dirty = True

    def set_color(self, r: int, g: int, b: int):
        """Cambia el color del texto (RGB)."""
        new_color = (r, g, b)
        if new_color != self.font_color:
            self.font_color = new_color
            self._dirty = True