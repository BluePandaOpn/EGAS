from config.settings import Settings
from egas.core.logger import Logger
from egas.interfaces.node import INode, ISceneTree


class SceneTree(ISceneTree):
    """Gestiona el arbol activo y propaga callbacks."""

    def __init__(self):
        self.root_node: INode = None

    def get_root(self) -> INode:
        return self.root_node

    def set_root(self, root_node: INode):
        self.root_node = root_node
        Logger.info("SceneTree", f"Nuevo nodo raiz establecido: '{root_node.get_name()}'")

    def get_node(self, path: str):
        if not self.root_node or not path:
            return None

        normalized = path.strip("/")
        if not normalized:
            return self.root_node

        parts = normalized.split("/")
        current = self.root_node
        if parts[0] == current.get_name():
            parts = parts[1:]

        for part in parts:
            current = next((child for child in current.get_children() if child.get_name() == part), None)
            if current is None:
                return None
        return current

    def update(self, delta_time: float):
        self.propagate_process(delta_time)

    def propagate_ready(self):
        self._walk(self.root_node, self._call_ready)

    def propagate_input(self, event):
        self._walk(self.root_node, lambda node: self._call_if_present(node, "_input", event))
        self._cleanup_queued_nodes()

    def propagate_physics_process(self, delta: float):
        self._walk(self.root_node, lambda node: self._call_if_present(node, "_physics_process", delta))
        self._cleanup_queued_nodes()

    def propagate_process(self, delta: float):
        self._walk(self.root_node, lambda node: node.process(delta))
        self._cleanup_queued_nodes()

    def propagate_draw(self, render_server):
        self._render_walk(self.root_node, render_server, draw_custom=False)

    def propagate_exit_tree(self):
        self._walk(self.root_node, lambda node: self._call_if_present(node, "_exit_tree"))

    def render_nodes(self, render_server):
        self._render_walk(self.root_node, render_server, draw_script=False)

    def render_scene(self, render_server):
        self._render_walk(self.root_node, render_server)

    def _walk(self, node: INode, callback):
        if not node:
            return
        callback(node)
        for _, child in self._sorted_children(node):
            self._walk(child, callback)

    def _sorted_children(self, node: INode):
        children = list(node.get_children())
        return sorted(enumerate(children), key=lambda item: (getattr(item[1], "z_index", 0), item[0]))

    def _render_walk(self, node: INode, render_server, draw_script: bool = True, draw_custom: bool = True):
        if not node:
            return
        if draw_script:
            self._call_if_present(node, "_draw", render_server)
        if draw_custom:
            self._draw_node(node, render_server)
        for _, child in self._sorted_children(node):
            self._render_walk(child, render_server, draw_script=draw_script, draw_custom=draw_custom)

    def _call_ready(self, node: INode):
        self._debug_node(node, "_ready")
        node.ready()
        bridge = getattr(node, "script_bridge", None)
        if bridge:
            bridge.execute_ready()

    def _call_if_present(self, node: INode, method_name: str, *args):
        self._debug_node(node, method_name)
        if hasattr(node, method_name):
            getattr(node, method_name)(*args)

        bridge = getattr(node, "script_bridge", None)
        if bridge:
            bridge.call(method_name, *args)

    def _draw_node(self, node: INode, render_server):
        if hasattr(node, "draw"):
            node.draw(render_server)

    def _cleanup_queued_nodes(self):
        if self.root_node is None:
            return
        if getattr(self.root_node, "is_queued_for_free", lambda: False)():
            self.root_node = None
            return
        self._cleanup_subtree(self.root_node)

    def _cleanup_subtree(self, node: INode):
        for child in list(node.get_children()):
            if getattr(child, "is_queued_for_free", lambda: False)():
                node.remove_child(child)
                continue
            self._cleanup_subtree(child)

    @staticmethod
    def _debug_node(node: INode, method_name: str):
        if Settings.DEBUG_LIFECYCLE:
            Logger.debug("Lifecycle", f"{node.get_name()}.{method_name}")
