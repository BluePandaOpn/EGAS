import json
import os
from pathlib import Path


class Settings:
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    VSYNC = True
    FPS_LIMIT = 60
    FULLSCREEN = False
    TITLE = "EGAS Engine V2.0"

    GRAVITY = 9.81
    PIXELS_PER_METER = 32
    PHYSICS_TIMESTEP = 1 / 60

    INPUT_MAP = {
        "ui_up": ["w", "up"],
        "ui_down": ["s", "down"],
        "ui_left": ["a", "left"],
        "ui_right": ["d", "right"],
        "ui_accept": ["space", "enter"],
        "ui_cancel": ["escape"],
        "move_up": ["w", "up"],
        "move_down": ["s", "down"],
        "move_left": ["a", "left"],
        "move_right": ["d", "right"],
    }
    KEY_ALIASES = {
        "return": "enter",
        "enter": "enter",
        "esc": "escape",
        "spacebar": "space",
    }

    DEBUG_INPUT = False
    DEBUG_LIFECYCLE = False

    BASE_DIR = Path(__file__).resolve().parent.parent
    PROJECT_DIR = None
    MAIN_SCENE = "res://scenes/nivel1.dscn"

    @classmethod
    def load_from_project(cls, project_path: str):
        cls.PROJECT_DIR = Path(project_path)
        egas_file = cls.PROJECT_DIR / "proyecto.egas"

        if not egas_file.exists():
            print(f"[Config] No se encontro proyecto.egas en {cls.PROJECT_DIR}.")
            return

        print(f"[Config] Cargando configuracion desde: {proyecto_content_file(egas_file)}")

        try:
            current_section = None
            with open(egas_file, "r", encoding="utf-8") as file_handle:
                for raw_line in file_handle:
                    line = raw_line.strip()
                    if not line or line.startswith("#"):
                        continue

                    if line.startswith("[") and line.endswith("]"):
                        current_section = line[1:-1]
                        continue

                    if "=" not in line:
                        continue

                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = cls._parse_value(value.strip())

                    if current_section == "project":
                        if key == "name":
                            cls.TITLE = value
                        elif key == "main_scene":
                            cls.MAIN_SCENE = value
                    elif current_section == "render":
                        if key == "width":
                            cls.SCREEN_WIDTH = value
                        elif key == "height":
                            cls.SCREEN_HEIGHT = value
                        elif key == "vsync":
                            cls.VSYNC = value
                    elif current_section == "debug":
                        if key == "input":
                            cls.DEBUG_INPUT = bool(value)
                        elif key == "lifecycle":
                            cls.DEBUG_LIFECYCLE = bool(value)
                    elif current_section == "input":
                        if isinstance(value, list):
                            cls.INPUT_MAP[key] = [cls.normalize_key_name(entry) for entry in value]

            print("[Config] Configuracion del proyecto cargada exitosamente.")
        except Exception as exc:
            print(f"[Config] Error leyendo proyecto.egas: {exc}.")

    @classmethod
    def normalize_key_name(cls, key_name: str) -> str:
        normalized = str(key_name).strip().lower()
        return cls.KEY_ALIASES.get(normalized, normalized)

    @staticmethod
    def _parse_value(value: str):
        if value.startswith('"') and value.endswith('"'):
            return value[1:-1]
        if value.lower() == "true":
            return True
        if value.lower() == "false":
            return False
        if value.isdigit():
            return int(value)
        if value.startswith("[") and value.endswith("]"):
            try:
                return json.loads(value.replace("'", '"'))
            except Exception:
                return value
        return value


def proyecto_content_file(path_file):
    return os.path.basename(path_file)
