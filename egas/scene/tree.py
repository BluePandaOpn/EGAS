from egas.interfaces.node import ISceneTree, INode
from egas.core.logger import Logger

class SceneTree(ISceneTree):
    """
    Gestiona el árbol de nodos activo en el juego y propaga el ciclo de vida.
    """
    def __init__(self):
        self.root_node: INode = None

    def get_root(self) -> INode:
        return self.root_node

    def set_root(self, root_node: INode):
        self.root_node = root_node
        Logger.info("SceneTree", f"Nuevo nodo raíz establecido: '{root_node.get_name()}'")
        self._propagate_ready(self.root_node)

    def _propagate_ready(self, node: INode):
        """Llama al método ready() de un nodo y todos sus hijos recursivamente."""
        if not node: return
        node.ready()
        for child in node.get_children():
            self._propagate_ready(child)

    def update(self, delta_time: float):
        """Actualiza la lógica de todos los nodos en cada frame."""
        if self.root_node:
            self._propagate_process(self.root_node, delta_time)

    def _propagate_process(self, node: INode, delta: float):
        if not node: return
        node.process(delta)
        for child in node.get_children():
            self._propagate_process(child, delta)

    def render_nodes(self, render_server):
        """Recorre el árbol de arriba hacia abajo para dibujar los nodos visuales."""
        if self.root_node:
            self._propagate_render(self.root_node, render_server)

    def _propagate_render(self, node: INode, render_server):
        # Si el nodo tiene una función draw(), la ejecutamos (ej: Sprite2D)
        if hasattr(node, 'draw'):
            node.draw(render_server)
        
        for child in node.get_children():
            self._propagate_render(child, render_server)