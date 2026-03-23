from egas.core.logger import Logger
from egas.interfaces.node import INode, ISceneTree


class SceneTree(ISceneTree):
    """
    Gestiona el árbol de nodos activo y propaga los callbacks del ciclo de vida.
    """

    def __init__(self):
        self.root_node: INode = None

    def get_root(self) -> INode:
        return self.root_node

    def set_root(self, root_node: INode):
        self.root_node = root_node
        Logger.info("SceneTree", f"Nuevo nodo raíz establecido: '{root_node.get_name()}'")

    def update(self, delta_time: float):
        self.propagate_process(delta_time)

    def propagate_ready(self):
        self._walk(self.root_node, self._call_ready)

    def propagate_input(self, event):
        self._walk(self.root_node, lambda node: self._call_if_present(node, "_input", event))

    def propagate_physics_process(self, delta: float):
        self._walk(self.root_node, lambda node: self._call_if_present(node, "_physics_process", delta))

    def propagate_process(self, delta: float):
        self._walk(self.root_node, lambda node: node.process(delta))

    def propagate_draw(self, render_server):
        self._walk(self.root_node, lambda node: self._call_if_present(node, "_draw", render_server))

    def propagate_exit_tree(self):
        self._walk(self.root_node, lambda node: self._call_if_present(node, "_exit_tree"))

    def render_nodes(self, render_server):
        self._walk(self.root_node, lambda node: self._draw_node(node, render_server))

    def _walk(self, node: INode, callback):
        if not node:
            return
        callback(node)
        for child in node.get_children():
            self._walk(child, callback)

    def _call_ready(self, node: INode):
        node.ready()
        bridge = getattr(node, "script_bridge", None)
        if bridge:
            bridge.execute_ready()

    def _call_if_present(self, node: INode, method_name: str, *args):
        if hasattr(node, method_name):
            getattr(node, method_name)(*args)

        bridge = getattr(node, "script_bridge", None)
        if bridge:
            bridge.call(method_name, *args)

    def _draw_node(self, node: INode, render_server):
        if hasattr(node, "draw"):
            node.draw(render_server)
