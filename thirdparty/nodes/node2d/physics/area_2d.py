import pygame
from thirdparty.nodes.node2d.node2d import Node2D
from egas.core.logger import Logger


class Area2D(Node2D):
    """
    Nodo Area2D para el motor EGAS.
    Detecta cuando otros nodos entran o salen de su caja de colisión.
    """

    def __init__(self):
        super().__init__()
        self.set_name("Area2D")

        # --- Propiedades de la Caja de Colisión ---
        self.width = 32.0
        self.height = 32.0
        self.monitoring = True  # Si es False, ignora las colisiones por completo

        # --- Control de Nodos ---
        self._nodes_inside = set()  # Guarda qué nodos están dentro actualmente
        
        Logger.info("Area2D", f"Nodo Area2D '{self.get_name()}' instanciado.")

    def process(self, delta: float):
        """
        Calcula en cada frame si hay cuerpos entrando o saliendo de su caja.
        """
        super().process(delta)

        if not self.monitoring:
            return

        # Obtenemos todos los nodos del árbol de escenas activo para compararlos
        root_node = self._get_root()
        if not root_node:
            return

        current_overlapping_nodes = set()
        self._check_collisions_recursive(root_node, current_overlapping_nodes)

        # 🔍 1. Detectar nodos que ACABAN DE ENTRAR
        for node in current_overlapping_nodes:
            if node not in self._nodes_inside:
                self._nodes_inside.add(node)
                self._on_body_entered(node)

        # 🔍 2. Detectar nodos que ACABAN DE SALIR
        exited_nodes = self._nodes_inside - current_overlapping_nodes
        for node in exited_nodes:
            self._nodes_inside.remove(node)
            self._on_body_exited(node)

    def _check_collisions_recursive(self, node, overlap_set):
        """Recorre el árbol de escenas buscando nodos con los que chocar."""
        if node == self or not getattr(node, "visible", True):
            return

        # Solo chocamos con objetos que tengan posición espacial (herederos de Node2D)
        if isinstance(node, Node2D) and node != self:
            if self._intersects(node):
                overlap_set.add(node)

        for child in node.get_children():
            self._check_collisions_recursive(child, overlap_set)

    def _intersects(self, other: Node2D) -> bool:
        """Matemáticas AABB: Verifica si dos rectángulos se superponen."""
        # Se asume un tamaño por defecto para el otro objeto si no tiene width/height
        other_w = getattr(other, "width", 32.0)
        other_h = getattr(other, "height", 32.0)

        return (self.position_x < other.position_x + other_w and
                self.position_x + self.width > other.position_x and
                self.position_y < other.position_y + other_h and
                self.position_y + self.height > other.position_y)

    def _on_body_entered(self, node):
        """Dispara el evento hacia GOS cuando entra un cuerpo."""
        Logger.info("Area2D", f"'{node.get_name()}' entró en '{self.get_name()}'")
        
        if hasattr(self, "script_bridge") and self.script_bridge:
            self.script_bridge.call("_on_body_entered", node)

    def _on_body_exited(self, node):
        """Dispara el evento hacia GOS cuando sale un cuerpo."""
        Logger.info("Area2D", f"'{node.get_name()}' salió de '{self.get_name()}'")
        
        if hasattr(self, "script_bridge") and self.script_bridge:
            self.script_bridge.call("_on_body_exited", node)

    def _get_root(self):
        """Obtiene el nodo raíz subiendo por la jerarquía."""
        current = self
        while current.get_parent():
            current = current.get_parent()
        return current

    # --- 🛠️ Dibujado de Debug ---
    def _draw(self, render_server):
        """Dibuja el rectángulo de colisión para que los desarrolladores lo vean (Modo Debug)."""
        screen = getattr(render_server, "screen", pygame.display.get_surface())
        if screen:
            # Color verde si está vacío, rojo si hay algo dentro
            color = (255, 0, 0) if self._nodes_inside else (0, 255, 0)
            pygame.draw.rect(screen, color, (self.position_x, self.position_y, self.width, self.height), 2)