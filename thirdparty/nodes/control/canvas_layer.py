from thirdparty.nodes.control.control import Control


class CanvasLayer(Control):
    """
    Capa de interfaz desacoplada del mundo 2D.
    """

    def __init__(self, name: str = "CanvasLayer"):
        super().__init__(name)
        self.layer = 1000
        self.z_index = 1000
