from thirdparty.nodes.node2d.node2d import Node2D
from egas.core.logger import Logger


class Camera2D(Node2D):
    """
    Nodo de Cámara para entornos 2D en el motor EGAS.
    Permite seguir a un objetivo, hacer zoom y limitar el desplazamiento en el mapa.
    """

    def __init__(self):
        super().__init__()
        self.set_name("Camera2D")

        # Configuración de Seguimiento
        self.target_node = None  # Otro Nodo del motor (ej: el Jugador)
        self.smoothing = 0.1     # Suavizado de 0.0 a 1.0 (0.1 es un movimiento suave)
        self.offset_x = 0.0      # Desplazamiento manual de la cámara en X
        self.offset_y = 0.0      # Desplazamiento manual de la cámara en Y

        # Configuración de Zoom y Límites
        self.zoom = 1.0
        self.limit_left = -1000000.0
        self.limit_right = 1000000.0
        self.limit_top = -1000000.0
        self.limit_bottom = 1000000.0

        Logger.info("Camera2D", "Nodo Camera2D instanciado con éxito.")

    def process(self, delta: float):
        """
        Calcula el movimiento de la cámara en cada frame (Tick del motor).
        """
        super().process(delta)

        if self.target_node:
            # 1. Obtener la posición del objetivo que queremos seguir
            target_x = getattr(self.target_node, "position_x", 0.0)
            target_y = getattr(self.target_node, "position_y", 0.0)

            # 2. Aplicar el desplazamiento manual (Offset)
            target_x += self.offset_x
            target_y += self.offset_y

            # 3. Mover la cámara usando Interpolación Lineal (Lerp) para suavizado
            self.position_x += (target_x - self.position_x) * self.smoothing
            self.position_y += (target_y - self.position_y) * self.smoothing

            # 4. Asegurarnos de que la cámara no se salga de los límites del mapa
            self._clamp_to_limits()

    def _clamp_to_limits(self):
        """Mantiene la cámara dentro de los límites matemáticos definidos."""
        if self.position_x < self.limit_left:
            self.position_x = self.limit_left
        elif self.position_x > self.limit_right:
            self.position_x = self.limit_right

        if self.position_y < self.limit_top:
            self.position_y = self.limit_top
        elif self.position_y > self.limit_bottom:
            self.position_y = self.limit_bottom

    # --- Funciones de Utilidad accesibles desde GOS ---

    def set_target(self, node):
        """Asigna a qué nodo del árbol de escenas debe seguir la cámara."""
        self.target_node = node

    def set_limits(self, left: float, top: float, right: float, bottom: float):
        """Configura los bordes del mapa para que la cámara no los sobrepase."""
        self.limit_left = left
        self.limit_top = top
        self.limit_right = right
        self.limit_bottom = bottom

    def set_zoom(self, zoom_factor: float):
        """Establece el nivel de zoom óptico."""
        if zoom_factor > 0:
            self.zoom = zoom_factor