import configparser
from pathlib import Path
from egas.core.logger import Logger

# Importaciones dinámicas de Thirdparty (se llenarán dinámicamente)
# por simplicidad usaremos un diccionario de registro de tipos de Nodos de Thirdparty.
NODE_REGISTRY = {}

class SceneParser:
    """
    Lee archivos de formato .dscn (estilo INI/TOML) y reconstruye el árbol de nodos en memoria.
    """

    @staticmethod
    def register_node_type(type_name: str, node_class):
        """Registra una clase de nodo de thirdparty para que el parser sepa construirlo."""
        NODE_REGISTRY[type_name] = node_class

    def load_scene(self, scene_path: str):
        """
        Analiza el archivo .dscn y devuelve un nodo Raíz del árbol configurado.
        """
        clean_path = scene_path.replace("res://", "")
        
        if not Path(clean_path).exists():
            Logger.error("SceneParser", f"No se encontró el archivo de escena en: {clean_path}")
            return None

        config = configparser.ConfigParser()
        config.read(clean_path, encoding='utf-8')

        nodes_by_id = {}
        root = None

        for section in config.sections():
            # El formato de sección suele ser [node_name] o [node_name:parent_name]
            node_type = config.get(section, "type", fallback="Node")
            
            if node_type not in NODE_REGISTRY:
                Logger.warning("SceneParser", f"Tipo de nodo desconocido: {node_type}. Saltando...")
                continue

            # Construir el nodo de thirdparty
            node_instance = NODE_REGISTRY[node_type]()
            node_instance.set_name(section)

            # Cargar propiedades (posición, escala, texturas, scripts...)
            if config.has_option(section, "script"):
                from egas.scene.script import ScriptBridge
                bridge = ScriptBridge(node_instance)
                bridge.attach_script(config.get(section, "script"))
                setattr(node_instance, 'script_bridge', bridge)

            nodes_by_id[section] = node_instance

            # Establecer herencia padre/hijo
            parent_name = config.get(section, "parent", fallback=None)
            if parent_name and parent_name in nodes_by_id:
                nodes_by_id[parent_name].add_child(node_instance)
            elif not root:
                # El primer nodo sin padre se convierte en la raíz del mundo
                root = node_instance

        Logger.success("SceneParser", f"Escena '{scene_path}' reconstruida exitosamente.")
        return root