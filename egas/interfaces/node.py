from abc import ABC, abstractmethod
from typing import List, Optional

class INode(ABC):
    """
    Interfaz base para todos los Nodos del motor EGAS.
    Garantiza el ciclo de vida: inicialización, actualización y destrucción.
    """
    
    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def set_name(self, name: str):
        pass

    @abstractmethod
    def get_parent(self) -> Optional['INode']:
        pass

    @abstractmethod
    def set_parent(self, parent: Optional['INode']):
        pass

    @abstractmethod
    def add_child(self, child: 'INode'):
        pass

    @abstractmethod
    def remove_child(self, child: 'INode'):
        pass

    @abstractmethod
    def get_children(self) -> List['INode']:
        pass

    # --- CICLO DE VIDA ---
    @abstractmethod
    def ready(self):
        """Se ejecuta una vez cuando el nodo entra al árbol activo."""
        pass

    @abstractmethod
    def process(self, delta: float):
        """Se ejecuta en cada frame para lógica del juego."""
        pass


class ISceneTree(ABC):
    """
    Interfaz que gestiona el árbol de nodos activo en el juego.
    """

    @abstractmethod
    def get_root(self) -> INode:
        pass

    @abstractmethod
    def set_root(self, root_node: INode):
        pass

    @abstractmethod
    def update(self, delta_time: float):
        """Recorre el árbol llamando al `process` de cada nodo."""
        pass