import pygame
from thirdparty.nodes.node2d.node2d import Node2D
from egas.core.logger import Logger


class AnimatedSprite2D(Node2D):
    """
    Nodo AnimatedSprite2D para el motor EGAS.
    Permite reproducir secuencias de imágenes (animaciones) para personajes u objetos.
    """

    def __init__(self):
        super().__init__()
        self.set_name("AnimatedSprite2D")

        # --- Propiedades de Animación ---
        self.animations = {}       # Diccionario: {"caminar": ["ruta1.png", "ruta2.png"], "saltar": [...]}
        self.current_animation = ""
        self.current_frame = 0
        self.speed = 10.0          # Fotogramas por segundo (FPS de animación)
        self.playing = False
        self.loop = True

        # --- Control de tiempo interno ---
        self._frame_timer = 0.0
        self._cached_surfaces = {} # Caché en RAM de las imágenes de Pygame

        Logger.info("AnimatedSprite2D", f"Nodo '{self.get_name()}' instanciado.")

    def process(self, delta: float):
        """
        Calcula qué fotograma debe mostrarse según el tiempo transcurrido (delta).
        """
        super().process(delta)

        if not self.playing or not self.current_animation:
            return

        frames = self.animations.get(self.current_animation, [])
        if not frames:
            return

        # Sumar tiempo y calcular si pasamos al siguiente fotograma
        self._frame_timer += delta
        time_per_frame = 1.0 / self.speed

        if self._frame_timer >= time_per_frame:
            self._frame_timer -= time_per_frame
            self.current_frame += 1

            # Manejar el fin de la animación
            if self.current_frame >= len(frames):
                if self.loop:
                    self.current_frame = 0
                else:
                    self.current_frame = len(frames) - 1
                    self.playing = False
                    self._on_animation_finished()

    def _draw(self, render_server):
        """
        Dibuja el fotograma actual de la animación en pantalla usando Pygame.
        """
        frames = self.animations.get(self.current_animation, [])
        if not frames or self.current_frame >= len(frames):
            return

        image_path = frames[self.current_frame]
        surface = self._get_cached_surface(image_path)

        if surface:
            screen = getattr(render_server, "screen", pygame.display.get_surface())
            if screen:
                screen.blit(surface, (self.position_x, self.position_y))

    # --- 🛠️ Funciones de Control accesibles desde GOS ---

    def add_animation(self, anim_name: str, frames_list: list):
        """Añade una animación nueva (ej: 'caminar', ['res://f1.png', 'res://f2.png'])"""
        self.animations[anim_name] = frames_list

    def play(self, anim_name: str = ""):
        """Reproduce una animación. Si se deja vacío, reproduce la actual."""
        if anim_name and anim_name in self.animations:
            if self.current_animation != anim_name:
                self.current_animation = anim_name
                self.current_frame = 0
                self._frame_timer = 0.0
        
        self.playing = True

    def stop(self):
        """Detiene la animación por completo."""
        self.playing = False
        self.current_frame = 0
        self._frame_timer = 0.0

    # --- Gestión de Memoria interna ---

    def _get_cached_surface(self, path: str):
        """Evita ahogar el disco duro cargando la imagen una sola vez en RAM."""
        clean_path = path.replace("res://", "")
        if clean_path not in self._cached_surfaces:
            try:
                # Se carga y se convierte a un formato óptimo para Pygame
                surface = pygame.image.load(clean_path).convert_alpha()
                self._cached_surfaces[clean_path] = surface
            except Exception as e:
                Logger.error("AnimatedSprite2D", f"No se pudo cargar la imagen '{clean_path}': {e}")
                return None
        
        return self._cached_surfaces.get(clean_path)

    def _on_animation_finished(self):
        """Dispara una señal al lenguaje GOS cuando una animación de un solo uso termina."""
        if hasattr(self, "script_bridge") and self.script_bridge:
            self.script_bridge.call("_on_animation_finished", self.current_animation)