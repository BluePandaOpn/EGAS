from typing import List, Optional

from egas.interfaces.node import INode


class Node(INode):
    """Nodo base del arbol de escenas."""

    def __init__(self, name: str = "Node"):
        self._name: str = name
        self._parent: Optional[INode] = None
        self._children: List[INode] = []
        self.script_bridge = None
        self._queued_for_free = False

    def get_name(self) -> str:
        return self._name

    def set_name(self, name: str):
        self._name = name

    def get_parent(self) -> Optional[INode]:
        return self._parent

    def set_parent(self, parent: Optional[INode]):
        self._parent = parent

    def add_child(self, child: INode):
        if child not in self._children:
            child.set_parent(self)
            self._children.append(child)

    def remove_child(self, child: INode):
        if child in self._children:
            child.set_parent(None)
            self._children.remove(child)

    def get_children(self) -> List[INode]:
        return self._children

    def get_node(self, path: str) -> Optional[INode]:
        if not path:
            return None

        parts = path.split("/")
        current = self
        for part in parts:
            match = next((child for child in current.get_children() if child.get_name() == part), None)
            if match is None:
                return None
            current = match
        return current

    def has_node(self, path: str) -> bool:
        return self.get_node(path) is not None

    def find_child(self, name: str):
        for child in self._children:
            if child.get_name() == name:
                return child
            nested = getattr(child, "find_child", lambda _name: None)(name)
            if nested is not None:
                return nested
        return None

    def queue_free(self):
        self._queued_for_free = True

    def is_queued_for_free(self) -> bool:
        return self._queued_for_free

    def duplicate(self):
        import copy

        clone = copy.deepcopy(self)
        clone._parent = None
        clone.script_bridge = None
        clone._queued_for_free = False
        return clone

    def ready(self):
        pass

    def process(self, delta: float):
        if self.script_bridge:
            self.script_bridge.call("_process", delta)
        self._custom_process(delta)

    def _custom_process(self, delta: float):
        pass

    def __str__(self) -> str:
        return f"[{self.__class__.__name__}:{self._name}]"
