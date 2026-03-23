import configparser
from pathlib import Path

from egas.core.logger import Logger

NODE_REGISTRY = {}


class SceneParser:
    """
    Lee archivos .dscn en texto plano y reconstruye un árbol de nodos.
    """

    @staticmethod
    def register_node_type(type_name: str, node_class):
        NODE_REGISTRY[type_name] = node_class

    def load_scene(self, scene_path: str):
        clean_path = scene_path.replace("res://", "")
        path = Path(clean_path)
        if not path.exists():
            Logger.error("SceneParser", f"No se encontró el archivo de escena en: {clean_path}")
            return None

        config = configparser.ConfigParser()
        config.read(path, encoding="utf-8")

        nodes_by_id = {}
        pending_parent_links: list[tuple[str, str]] = []
        root = None

        for section in config.sections():
            node_type = config.get(section, "type", fallback="Node")
            if node_type not in NODE_REGISTRY:
                Logger.warning("SceneParser", f"Tipo de nodo desconocido: {node_type}.")
                continue

            node_instance = NODE_REGISTRY[node_type]()
            node_instance.set_name(section)
            self._apply_properties(node_instance, config[section])

            if config.has_option(section, "script"):
                from egas.scene.script import ScriptBridge

                bridge = ScriptBridge(node_instance)
                bridge.attach_script(config.get(section, "script"))
                setattr(node_instance, "script_bridge", bridge)

            nodes_by_id[section] = node_instance

            parent_name = config.get(section, "parent", fallback=None)
            if parent_name:
                pending_parent_links.append((section, parent_name))
            elif root is None:
                root = node_instance

        for node_name, parent_name in pending_parent_links:
            node = nodes_by_id.get(node_name)
            parent = nodes_by_id.get(parent_name)
            if not node or not parent:
                Logger.warning("SceneParser", f"No se pudo enlazar '{node_name}' con su padre '{parent_name}'.")
                continue
            parent.add_child(node)

        Logger.success("SceneParser", f"Escena '{scene_path}' reconstruida exitosamente.")
        return root

    def _apply_properties(self, node_instance, section):
        if "texture" in section and hasattr(node_instance, "texture_path"):
            node_instance.texture_path = section.get("texture", "")

        if "position_x" in section and "position_y" in section and hasattr(node_instance, "set_position"):
            node_instance.set_position(section.getfloat("position_x"), section.getfloat("position_y"))

        if "scale_x" in section and "scale_y" in section and hasattr(node_instance, "set_scale"):
            node_instance.set_scale(section.getfloat("scale_x"), section.getfloat("scale_y"))

        if "rotation" in section and hasattr(node_instance, "set_rotation"):
            node_instance.set_rotation(section.getfloat("rotation"))
