from thirdparty.nodes.node2d.node2d import Node2D
from egas.core.logger import Logger

class AnimatedSprite2D(Node2D):
    """
    Nodo que reproduce animaciones basadas en cuadros (frames) desde un Spritesheet.
    """
    def __init__(self, name: str = "AnimatedSprite2D"):
        super().__init__(name)
        
        self.texture_path: str = ""
        self._cached_texture = None
        self.visible: bool = True

        # Configuración de Animación
        self.h_frames: int = 1  # Cuadros horizontales
        self.v_frames: int = 1  # Cuadros verticales
        
        self.current_frame: int = 0
        self.is_playing: bool = False
        self.animation_speed: float = 12.0 # Cuadros por segundo (FPS de animación)
        self.loop: bool = True

        self._time_elapsed: float = 0.0

    def play(self, start_frame: int = 0):
        self.current_frame = start_frame
        self.is_playing = True
        self._time_elapsed = 0.0

    def stop(self):
        self.is_playing = False

    def _custom_process(self, delta: float):
        """Avanza la animación según el delta time del motor."""
        if not self.is_playing or self.h_frames <= 1 and self.v_frames <= 1:
            return

        self._time_elapsed += delta
        frame_duration = 1.0 / self.animation_speed

        if self._time_elapsed >= frame_duration:
            self._time_elapsed -= frame_duration
            self.current_frame += 1

            total_frames = self.h_frames * self.v_frames
            if self.current_frame >= total_frames:
                if self.loop:
                    self.current_frame = 0
                else:
                    self.current_frame = total_frames - 1
                    self.is_playing = False

    def draw(self, render_server):
        if not self.visible or not self.texture_path:
            return

        if not self._cached_texture:
            self._cached_texture = render_server.load_texture(self.texture_path)

        # Matematicas para recortar el Spritesheet (Sub-cuadros)
        # NOTA: En PygameRenderServer necesitamos expandir `draw_texture` para soportar 
        # rectángulos de recorte (Sub-surface). Para esta V2.0 simplificada, el dibujo se hace
        # escalando la textura completa del fotograma actual.
        
        global_pos = self.get_global_position()

        render_server.draw_texture(
            texture=self._cached_texture,
            position=global_pos.to_tuple(),
            scale=self.get_scale().to_tuple(),
            rotation=self.get_global_rotation()
        )