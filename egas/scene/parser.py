import configparser
import json
from pathlib import Path

from egas.core.logger import Logger

NODE_REGISTRY = {}


def _line_lookup_map(scene_text: str):
    section_lines = {}
    key_lines = {}
    current_section = None

    for line_no, raw_line in enumerate(scene_text.splitlines(), start=1):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith(";"):
            continue
        if stripped.startswith("[") and stripped.endswith("]"):
            current_section = stripped[1:-1].strip()
            section_lines[current_section] = line_no
            continue
        if "=" in stripped and current_section:
            key = stripped.split("=", 1)[0].strip().lower()
            key_lines[(current_section, key)] = line_no

    return section_lines, key_lines


def _parse_scalar(value: str, *, section: str, key: str, line_no: int | None):
    text = value.strip()
    if not text:
        return ""

    if text.startswith('"') and text.endswith('"'):
        return text[1:-1]

    lower = text.lower()
    if lower == "true":
        return True
    if lower == "false":
        return False

    if text.startswith("[") and text.endswith("]"):
        try:
            return json.loads(text.replace("'", '"'))
        except json.JSONDecodeError:
            Logger.warning("SceneParser", f"Lista invalida en [{section}] {key} linea {line_no}: {text}")
            return text

    try:
        if "." in text:
            return float(text)
        return int(text)
    except ValueError:
        if "/" in text or text.startswith("res://"):
            Logger.warning(
                "SceneParser",
                f"String sin comillas en [{section}] {key} linea {line_no}. Se acepta por compatibilidad, pero conviene usar comillas.",
            )
        return text


class SceneParser:
    """Lee archivos .dscn y reconstruye un arbol de nodos."""

    @staticmethod
    def register_node_type(type_name: str, node_class):
        NODE_REGISTRY[type_name] = node_class

    def load_scene(self, scene_path: str):
        clean_path = scene_path.replace("res://", "")
        path = Path(clean_path)
        if not path.exists():
            Logger.error("SceneParser", f"No se encontro el archivo de escena en: {clean_path}")
            return None

        scene_text = path.read_text(encoding="utf-8")
        section_lines, key_lines = _line_lookup_map(scene_text)

        config = configparser.ConfigParser()
        config.optionxform = str
        config.read_string(scene_text)

        nodes_by_id = {}
        pending_parent_links: list[tuple[str, str]] = []
        pending_reference_links: list[tuple[object, str, str, int | None]] = []
        root = None

        for section in config.sections():
            node_instance = self._create_node_instance(config, section, section_lines.get(section))
            if node_instance is None:
                continue

            node_instance.set_name(section)
            self._apply_properties(node_instance, config[section], section, key_lines, pending_reference_links)

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
            parent = self._resolve_node_reference(parent_name, nodes_by_id, root)
            if not node or not parent:
                Logger.warning("SceneParser", f"No se pudo enlazar '{node_name}' con su padre '{parent_name}'.")
                continue
            parent.add_child(node)

        for node_instance, attr_name, target_name, line_no in pending_reference_links:
            target_node = self._resolve_node_reference(target_name, nodes_by_id, root)
            if target_node is None:
                Logger.warning("SceneParser", f"No se pudo resolver la referencia '{attr_name}={target_name}' en linea {line_no}.")
                continue
            setattr(node_instance, attr_name, target_node)

        Logger.success("SceneParser", f"Escena '{scene_path}' reconstruida exitosamente.")
        return root

    def _create_node_instance(self, config, section: str, line_no: int | None):
        if config.has_option(section, "instance"):
            nested_scene_path = config.get(section, "instance")
            nested_root = self.load_scene(nested_scene_path)
            if nested_root is None:
                Logger.warning("SceneParser", f"No se pudo instanciar la subescena '{nested_scene_path}' en linea {line_no}.")
            return nested_root

        node_type = config.get(section, "type", fallback="Node")
        if node_type not in NODE_REGISTRY:
            Logger.warning("SceneParser", f"Tipo de nodo desconocido '{node_type}' en [{section}] linea {line_no}.")
            return None
        return NODE_REGISTRY[node_type]()

    def _apply_properties(self, node_instance, section_data, section_name: str, key_lines, pending_reference_links):
        metadata_keys = {"type", "parent", "script", "instance"}

        if "position_x" in section_data or "position_y" in section_data:
            current_pos = getattr(node_instance, "get_position", lambda: None)()
            pos_x = _parse_scalar(
                section_data.get("position_x", str(getattr(current_pos, "x", 0.0))),
                section=section_name,
                key="position_x",
                line_no=key_lines.get((section_name, "position_x")),
            )
            pos_y = _parse_scalar(
                section_data.get("position_y", str(getattr(current_pos, "y", 0.0))),
                section=section_name,
                key="position_y",
                line_no=key_lines.get((section_name, "position_y")),
            )
            if hasattr(node_instance, "set_position"):
                node_instance.set_position(pos_x, pos_y)

        if "scale_x" in section_data or "scale_y" in section_data:
            current_scale = getattr(node_instance, "get_scale", lambda: None)()
            scale_x = _parse_scalar(
                section_data.get("scale_x", str(getattr(current_scale, "x", 1.0))),
                section=section_name,
                key="scale_x",
                line_no=key_lines.get((section_name, "scale_x")),
            )
            scale_y = _parse_scalar(
                section_data.get("scale_y", str(getattr(current_scale, "y", 1.0))),
                section=section_name,
                key="scale_y",
                line_no=key_lines.get((section_name, "scale_y")),
            )
            if hasattr(node_instance, "set_scale"):
                node_instance.set_scale(scale_x, scale_y)

        if "rotation" in section_data and hasattr(node_instance, "set_rotation"):
            node_instance.set_rotation(
                _parse_scalar(section_data.get("rotation"), section=section_name, key="rotation", line_no=key_lines.get((section_name, "rotation")))
            )

        if "size_x" in section_data or "size_y" in section_data:
            current_size = getattr(node_instance, "size", None)
            current_x = getattr(current_size, "x", 100.0) if current_size is not None else 100.0
            current_y = getattr(current_size, "y", 40.0) if current_size is not None else 40.0
            size_x = _parse_scalar(section_data.get("size_x", str(current_x)), section=section_name, key="size_x", line_no=key_lines.get((section_name, "size_x")))
            size_y = _parse_scalar(section_data.get("size_y", str(current_y)), section=section_name, key="size_y", line_no=key_lines.get((section_name, "size_y")))
            if hasattr(node_instance, "set_size"):
                node_instance.set_size(size_x, size_y)
            elif current_size is not None and hasattr(current_size, "x") and hasattr(current_size, "y"):
                current_size.x = float(size_x)
                current_size.y = float(size_y)

        for key, raw_value in section_data.items():
            if key in metadata_keys or key.startswith(("position_", "scale_", "size_")) or key == "rotation":
                continue

            line_no = key_lines.get((section_name, key))
            value = _parse_scalar(raw_value, section=section_name, key=key, line_no=line_no)
            setter_name = f"set_{key}"
            setter = getattr(node_instance, setter_name, None)

            if key == "texture" and hasattr(node_instance, "texture_path"):
                node_instance.texture_path = value
                continue

            if key.endswith("_node") and isinstance(value, str):
                pending_reference_links.append((node_instance, key, value, line_no))
                continue

            if callable(setter):
                setter(value)
                continue

            has_attr = hasattr(node_instance, key)
            if has_attr:
                current_attr = getattr(node_instance, key, None)
                if isinstance(current_attr, tuple) and isinstance(value, list):
                    setattr(node_instance, key, tuple(value))
                    continue
                setattr(node_instance, key, value)
                continue

            Logger.warning(
                "SceneParser",
                f"Propiedad desconocida en [{section_name}] {key}={raw_value} linea {line_no}. Se aplicara dinamicamente.",
            )
            setattr(node_instance, key, value)

    def _resolve_node_reference(self, reference: str, nodes_by_id: dict[str, object], root):
        if reference in nodes_by_id:
            return nodes_by_id[reference]

        normalized = reference.strip("/")
        if not normalized:
            return root

        parts = normalized.split("/")
        current = root
        if current is None:
            return None

        if parts[0] == current.get_name():
            parts = parts[1:]

        for part in parts:
            next_node = next((child for child in current.get_children() if child.get_name() == part), None)
            if next_node is None:
                return None
            current = next_node
        return current
