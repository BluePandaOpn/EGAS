import os
import json
from pathlib import Path

class Settings:
    """
    Clase Singleton que almacena y carga la configuración global del motor EGAS.
    Centraliza Pantalla, Físicas, Entradas de Teclado y Rutas del Sistema.
    """
    
    # --- 🖥️ CONFIGURACIÓN DE PANTALLA (Por defecto) ---
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    VSYNC = True
    FPS_LIMIT = 60
    FULLSCREEN = False
    TITLE = "EGAS Engine V2.0"

    # --- 🧬 CONFIGURACIÓN DE FÍSICAS (Por defecto) ---
    GRAVITY = 9.81              # Gravedad estándar en m/s^2
    PIXELS_PER_METER = 32       # Factor de escala para pasar metros a píxeles
    PHYSICS_TIMESTEP = 1 / 60   # Delta time fijo para las físicas (60Hz)

    # --- ⌨️ MAPEO DE ENTRADAS (Input Map estándar) ---
    INPUT_MAP = {
        "ui_up": ["w", "up"],
        "ui_down": ["s", "down"],
        "ui_left": ["a", "left"],
        "ui_right": ["d", "right"],
        "ui_accept": ["space", "return"],
        "ui_cancel": ["escape"]
    }

    # --- 📂 RUTAS DEL SISTEMA ---
    BASE_DIR = Path(__file__).resolve().parent.parent
    PROJECT_DIR = None
    MAIN_SCENE = "res://scenes/nivel1.dscn"

    @classmethod
    def load_from_project(cls, project_path: str):
        """
        Carga la configuración dinámica leyendo el archivo proyecto.egas generado por PyQt6.
        """
        cls.PROJECT_DIR = Path(project_path)
        egas_file = cls.PROJECT_DIR / "proyecto.egas"

        if not egas_file.exists():
            print(f"⚠️ [Config] No se encontró proyecto.egas en {cls.PROJECT_DIR}. Usando valores por defecto.")
            return

        print(f"⚙️ [Config] Cargando configuraciones de: {proyecto_content_file(egas_file)}")
        
        try:
            # Leemos el archivo proyecto.egas (parseo manual estilo INI/TOML simplificado)
            current_section = None
            
            with open(egas_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                        
                    if line.startswith("[") and line.endswith("]"):
                        current_section = line[1:-1]
                        continue

                    if "=" in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip()

                        # --- Limpieza de comillas y tipos ---
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.lower() == "true":
                            value = True
                        elif value.lower() == "false":
                            value = False
                        elif value.isdigit():
                            value = int(value)
                        elif value.startswith("[") and value.endswith("]"):
                            # Intentar leerlo como lista (ej: las plataformas)
                            try:
                                value = json.loads(value.replace("'", '"'))
                            except:
                                pass

                        # --- Aplicar al motor ---
                        if current_section == "project":
                            if key == "name": cls.TITLE = value
                            if key == "main_scene": cls.MAIN_SCENE = value
                        
                        elif current_section == "render":
                            if key == "width": cls.SCREEN_WIDTH = value
                            if key == "height": cls.SCREEN_HEIGHT = value
                            if key == "vsync": cls.VSYNC = value

            print("✅ [Config] Configuración del proyecto cargada exitosamente.")
            
        except Exception as e:
            print(f"❌ [Config] Error leyendo proyecto.egas: {e}. Usando valores por defecto.")


def proyecto_content_file(path_file):
    """Retorna el nombre del archivo para debug"""
    return os.path.basename(path_file)