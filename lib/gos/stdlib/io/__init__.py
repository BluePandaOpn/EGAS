import json
import os
from egas.core.logger import Logger

class GosIO:
    @staticmethod
    def file_write(path: str, content: str) -> bool:
        """Escribe texto en un archivo del disco duro."""
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(str(content))
            return True
        except Exception as e:
            Logger.error("IO STDLIB", f"No se pudo escribir en el archivo '{path}': {e}")
            return False

    @staticmethod
    def file_read(path: str) -> str:
        """Lee el texto de un archivo del disco duro."""
        if not os.path.exists(path):
            Logger.warning("IO STDLIB", f"El archivo '{path}' no existe.")
            return ""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            Logger.error("IO STDLIB", f"Error leyendo el archivo '{path}': {e}")
            return ""

    @staticmethod
    def json_to_dict(json_str: str):
        """Transforma un String JSON a un diccionario legible por GOS."""
        try:
            return json.loads(json_str)
        except Exception:
            return {}

# Mapeo de nombres de funciones que usará el lenguaje GOS
IO_EXTENSIONS = {
    "save_file": GosIO.file_write,
    "load_file": GosIO.file_read,
    "parse_json": GosIO.json_to_dict
}