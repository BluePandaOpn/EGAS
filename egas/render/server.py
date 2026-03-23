import pygame
from typing import Tuple, Dict
from config.settings import Settings
from egas.interfaces.render import IRenderServer, ITexture
from egas.render.texture import PygameTexture
from egas.core.logger import Logger


class PygameRenderServer(IRenderServer):
    """
    Implementación del Servidor de Renderizado utilizando la librería Pygame.
    Controla la pantalla, las cámaras y las transformaciones de dibujo bidimensionales.
    """

    def __init__(self):
        self.screen: pygame.Surface = None
        self.is_initialized = False
        self._texture_cache: Dict[str, PygameTexture] = {} # Evita recargar la misma imagen de disco

    def initialize(self, width: int, height: int, vsync: bool):
        """Inicializa la pantalla de Pygame."""
        if self.is_initialized:
            return

        pygame.init()
        
        flags = pygame.DOUBLEBUF
        if Settings.FULLSCREEN:
            flags |= pygame.FULLSCREEN

        self.screen = pygame.display.set_mode((width, height), flags, vsync=int(vsync))
        pygame.display.set_caption(Settings.TITLE)

        self.is_initialized = True
        Logger.success("RenderServer", f"Ventana Pygame abierta con éxito ({width}x{height})")

    def begin_frame(self):
        """Limpia la pantalla con un color de fondo base (Gris oscuro por defecto)."""
        if not self.is_initialized: return
        self.screen.fill((30, 30, 30)) # Color de fondo del motor

    def draw_texture(self, texture: ITexture, position: Tuple[float, float], scale: Tuple[float, float], rotation: float):
        """
        Dibuja una textura aplicando transformaciones espaciales (Escala y Rotación).
        """
        if not self.is_initialized or not isinstance(texture, PygameTexture):
            return

        surf = texture.get_surface()

        # 1. Aplicar Escala si es diferente de (1, 1)
        if scale[0] != 1.0 or scale[1] != 1.0:
            new_w = int(texture.get_width() * scale[0])
            new_w = max(1, new_w) # Evitar escalas de 0
            new_h = int(texture.get_height() * scale[1])
            new_h = max(1, new_h)
            surf = pygame.transform.scale(surf, (new_w, new_h))

        # 2. Aplicar Rotación (Pygame rota en sentido antihorario, por eso el signo negativo)
        if rotation != 0.0:
            surf = pygame.transform.rotate(surf, -rotation)

        # 3. Calcular el Offset para que el dibujo se centre en su pivote y no en la esquina superior izquierda
        rect = surf.get_rect()
        rect.center = (int(position[0]), int(position[1]))

        # 4. Estampar (Blit) en pantalla
        self.screen.blit(surf, rect)

    def end_frame(self):
        """Hace el 'Flip' de los buffers para mostrar el frame al usuario."""
        if not self.is_initialized: return
        pygame.display.flip()

    def load_texture(self, path: str) -> ITexture:
        """Carga una imagen y la guarda en caché para optimizar memoria."""
        if path in self._texture_cache:
            return self._texture_cache[path]

        try:
            # En Windows/Pygame las barras deben convertirse correctamente
            clean_path = path.replace("res://", "")
            full_path = str(Settings.BASE_DIR / clean_path) if Settings.PROJECT_DIR is None else str(Settings.PROJECT_DIR / clean_path)

            loaded_surface = pygame.image.load(full_path).convert_alpha()
            texture = PygameTexture(loaded_surface, path)
            self._texture_cache[path] = texture
            
            Logger.info("RenderServer", f"Textura cargada con éxito: {path}")
            return texture

        except Exception as e:
            Logger.error("RenderServer", f"No se pudo cargar la textura {path}. Error: {e}")
            # Retornar una textura dummy fucsia por si falla
            dummy = pygame.Surface((32, 32))
            dummy.fill((255, 0, 255))
            return PygameTexture(dummy, path)