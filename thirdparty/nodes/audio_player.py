import pygame
from thirdparty.nodes.base.node import Node
from egas.core.logger import Logger


class AudioPlayer(Node):
    """
    Nodo AudioPlayer para el motor EGAS.
    Carga y reproduce efectos de sonido o música de fondo usando pygame.mixer.
    """

    def __init__(self):
        super().__init__()
        self.set_name("AudioPlayer")

        # --- Propiedades de Configuración ---
        self.stream_path = ""
        self.autoplay = False
        self.volume = 1.0        # De 0.0 (silencio) a 1.0 (máximo)
        self.loop = False        # True para música infinita, False para efectos de un solo disparo
        self.is_playing = False

        # --- Control de memoria interno ---
        self._sound_cache = None # Guarda el objeto Sound cargado en RAM

        # Aseguramos que el mezclador de Pygame esté encendido
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init()
            except Exception as e:
                Logger.error("AudioPlayer", f"No se pudo inicializar pygame.mixer: {e}")

        Logger.info("AudioPlayer", f"Nodo AudioPlayer '{self.get_name()}' instanciado.")

    def ready(self):
        super().ready()
        if self.stream_path:
            self.load_audio(self.stream_path)

        if self.autoplay:
            self.play()

    # --- 🛠️ Funciones de Control accesibles desde GOS ---

    def load_audio(self, path: str):
        """Carga el archivo de audio (.mp3, .wav, .ogg) en la memoria RAM."""
        self.stream_path = path
        clean_path = path.replace("res://", "")

        try:
            self._sound_cache = pygame.mixer.Sound(clean_path)
            self._sound_cache.set_volume(self.volume)
            Logger.success("AudioPlayer", f"Audio cargado con éxito: {clean_path}")
        except Exception as e:
            Logger.error("AudioPlayer", f"No se pudo cargar el audio en {clean_path}: {e}")
            self._sound_cache = None

    def play(self):
        """Reproduce el audio."""
        if not self._sound_cache:
            Logger.warning("AudioPlayer", f"No hay audio cargado en '{self.get_name()}' para reproducir.")
            return

        loops = -1 if self.loop else 0
        self._sound_cache.play(loops=loops)
        self.is_playing = True

    def stop(self):
        """Detiene la reproducción."""
        if self._sound_cache:
            self._sound_cache.stop()
        self.is_playing = False

    def set_volume(self, value: float):
        """Cambia el volumen dinámicamente (0.0 a 1.0)."""
        self.volume = max(0.0, min(1.0, value))
        if self._sound_cache:
            self._sound_cache.set_volume(self.volume)

    def set_loop(self, loop: bool):
        """Configura si el audio debe repetirse infinitamente."""
        self.loop = loop