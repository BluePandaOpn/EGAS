from typing import List, Optional
from egas.interfaces.node import INode
from egas.core.logger import Logger


class Node(INode):
    """
    Representación base de todos los objetos que viven en el árbol de escenas del motor EGAS.
    Maneja la jerarquía estructural (Padres e Hijos) y el ciclo de vida básico.
    """

    def __init__(self, name: str = "Node"):
        self._name: str = name
        self._parent: Optional[INode] = None
        self._children: List[INode] = []
        
        # Puente opcional para ejecutar scripts de tu lenguaje GOS
        self.script_bridge = None 

    # --- Gestión de Nombres ---
    def get_name(self) -> str:
        return self._name

    def set_name(self, name: str):
        self._name = name

    # --- Gestión de Jerarquías (Árbol) ---
    def get_parent(self) -> Optional[INode]:
        return self._parent

    def set_parent(self, parent: Optional[INode]):
        self._parent = parent

    def add_child(self, child: INode):
        """Añade un nodo hijo y le asigna este nodo como su padre."""
        if child not in self._children:
            child.set_parent(self)
            self._children.append(child)
            # Si el juego ya está corriendo, disparamos su evento ready
            # (En el SceneParser se hace de golpe al cargar, pero esto sirve para spawnear dinámicamente)

    def remove_child(self, child: INode):
        """Remueve un nodo hijo y lo desvincula de este padre."""
        if child in self._children:
            child.set_parent(None)
            self._children.remove(child)

    def get_children(self) -> List[INode]:
        return self._children

    def get_node(self, path: str) -> Optional[INode]:
        """
        Busca un nodo hijo por su nombre o ruta relativa (ej: "Nave/Escudo").
        Muy útil para que los scripts GOS busquen otros nodos.
        """
        if not path:
            return None

        parts = path.split("/")
        current_search = self

        for part in parts:
            found = False
            for child in current_search.get_children():
                if child.get_name() == part:
                    current_search = child
                    found = True
                    break
            if not found:
                return None

        return current_search

    # --- Ciclo de Vida (Sobrescribir en herederos) ---
    def ready(self):
        """
        Se ejecuta una única vez cuando el nodo entra al árbol activo.
        Ideal para inicializar variables.
        """
        pass

    def process(self, delta: float):
        """
        Se ejecuta frame por frame. 
        Llama al puente del lenguaje GOS si este nodo tiene un script adjunto.
        """
        # 1. Ejecutar la lógica de GOS escrita por el usuario
        if self.script_bridge:
            self.script_bridge.execute_tick(delta)

        # 2. (Opcional) Lógica escrita directamente en Python para este nodo
        self._custom_process(delta)

    def _custom_process(self, delta: float):
        """Sobrescribir en clases hijas si se quiere lógica en Python puro."""
        pass

    def __str__(self) -> str:
        return f"[{self.__class__.__name__}:{self._name}]"