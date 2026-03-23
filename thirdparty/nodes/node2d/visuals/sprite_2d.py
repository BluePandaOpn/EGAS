from thirdparty.nodes.node2d.node2d import Node2D
from egas.core.logger import Logger

class Sprite2D(Node2D):
    """
    Nodo que representa una imagen fija en el espacio 2D.
    Hereda de Node2D y se comunica con el RenderServer para dibujarse.
    """
    def __init__(self, name: str = "Sprite2D"):
        super().__init__(name)
        
        self.texture_path: str = ""
        self._cached_texture = None # Se carga en RAM la primera vez
        
        # Atributos de visualización
        self.visible: bool = True
        self.centered: bool = True
        self.offset_x: float = 0.0
        self.offset_y: float = 0.0

    def ready(self):
        super().ready()
        # Puedes pre-cargar la textura si lo deseas aquí

    def draw(self, render_server):
        """
        Método invocado automáticamente por el SceneTree en cada frame.
        """
        if not self.visible or not self.texture_path:
            return

        # 1. Cargar la textura si no está en caché
        if not self._cached_texture:
            self._cached_texture = render_server.load_texture(self.texture_path)

        # 2. Calcular posición global (Posición del padre + posición local)
        global_pos = self.get_global_position()
        pos_tuple = (global_pos.x + self.offset_x, global_pos.y + self.offset_y)

        # 3. Dibujar en el RenderServer
        render_server.draw_texture(
            texture=self._cached_texture,
            position=pos_tuple,
            scale=self.get_scale().to_tuple(),
            rotation=self.get_global_rotation()
        )