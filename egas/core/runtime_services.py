from __future__ import annotations

from egas.core.logger import Logger


class RuntimeServices:
    """
    Registro global minimo para exponer servicios del runtime a GOS.
    """

    scene_tree = None
    resource_manager = None

    @classmethod
    def configure(cls, scene_tree, resource_manager):
        cls.scene_tree = scene_tree
        cls.resource_manager = resource_manager

    @classmethod
    def load_scene(cls, scene_path: str):
        if cls.resource_manager is None:
            Logger.error("RuntimeServices", "No hay ResourceManager disponible para cargar escenas.")
            return None
        return cls.resource_manager.load_scene_sync(scene_path)

    @classmethod
    def change_scene(cls, scene_path: str):
        if cls.scene_tree is None or cls.resource_manager is None:
            Logger.error("RuntimeServices", "No hay runtime activo para cambiar de escena.")
            return None

        new_root = cls.resource_manager.load_scene_sync(scene_path)
        if new_root is None:
            return None

        current_root = cls.scene_tree.get_root()
        if current_root is not None:
            cls.scene_tree.propagate_exit_tree()

        cls.scene_tree.set_root(new_root)
        cls.scene_tree.propagate_ready()
        cls.resource_manager.prime_script_watch(new_root)
        Logger.success("RuntimeServices", f"Escena activa cambiada a '{scene_path}'.")
        return new_root

    @classmethod
    def get_root(cls):
        if cls.scene_tree is None:
            return None
        return cls.scene_tree.get_root()

    @classmethod
    def get_node(cls, node_path: str):
        if cls.scene_tree is None:
            return None
        return cls.scene_tree.get_node(node_path)
