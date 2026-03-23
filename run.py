import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QCheckBox, QSpinBox, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt


class EgasLauncher(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("EGAS Engine V2.0 - Gestor de Proyectos")
        self.resize(500, 600)

        # Diseño Principal
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)

        title_lbl = QLabel("🚀 Crear Nuevo Proyecto EGAS")
        title_lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #4CAF50;")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_lbl)

        # --- SECCIÓN: INFORMACIÓN DEL PROYECTO ---
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ejemplo: Naves Espaciales")
        main_layout.addWidget(QLabel("Nombre del Juego:"))
        main_layout.addWidget(self.name_input)

        # Ruta de guardado físico
        path_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setReadOnly(True)
        self.path_input.setText(os.getcwd())
        btn_browse = QPushButton("Explorar...")
        btn_browse.clicked.connect(self.browse_folder)
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(btn_browse)
        main_layout.addWidget(QLabel("Ruta de creación:"))
        main_layout.addLayout(path_layout)

        # Versión del proyecto
        self.version_input = QLineEdit("1.0.0")
        main_layout.addWidget(QLabel("Versión del Juego:"))
        main_layout.addWidget(self.version_input)

        # Escena principal .dscn
        self.scene_input = QLineEdit("res://scenes/nivel1.dscn")
        main_layout.addWidget(QLabel("Escena Inicial:"))
        main_layout.addWidget(self.scene_input)

        # --- SECCIÓN: RENDER (Resoluciones) ---
        render_layout = QHBoxLayout()
        self.width_input = QSpinBox()
        self.width_input.setRange(640, 3840)
        self.width_input.setValue(1920)
        self.height_input = QSpinBox()
        self.height_input.setRange(480, 2160)
        self.height_input.setValue(1080)
        
        render_layout.addWidget(QLabel("Ancho:"))
        render_layout.addWidget(self.width_input)
        render_layout.addWidget(QLabel("Alto:"))
        render_layout.addWidget(self.height_input)
        main_layout.addLayout(render_layout)

        self.vsync_check = QCheckBox("Habilitar VSync")
        self.vsync_check.setChecked(True)
        main_layout.addWidget(self.vsync_check)

        # --- SECCIÓN: PLATAFORMAS ---
        main_layout.addWidget(QLabel("Plataformas objetivo:"))
        self.check_windows = QCheckBox("Windows")
        self.check_windows.setChecked(True)
        self.check_linux = QCheckBox("Linux")
        self.check_mac = QCheckBox("MacOS")
        
        plat_layout = QHBoxLayout()
        plat_layout.addWidget(self.check_windows)
        plat_layout.addWidget(self.check_linux)
        plat_layout.addWidget(self.check_mac)
        main_layout.addLayout(plat_layout)

        # --- BOTÓN DE CREACIÓN AUTOMATIZADA ---
        self.btn_create = QPushButton("🏗️ Crear Proyecto Automatizado")
        self.btn_create.setStyleSheet(
            "background-color: #2E7D32; color: white; font-weight: bold; padding: 12px; font-size: 14px;"
        )
        self.btn_create.clicked.connect(self.create_project)
        main_layout.addWidget(self.btn_create)

        self.setLayout(main_layout)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta de Destino")
        if folder:
            self.path_input.setText(folder)

    def create_project(self):
        project_name = self.name_input.text().strip()
        if not project_name:
            QMessageBox.warning(self, "Error", "¡El nombre del proyecto no puede estar vacío!")
            return

        # Normalización de carpetas en minúscula
        folder_name = project_name.lower().replace(" ", "_")
        base_dir = Path(self.path_input.text()) / folder_name

        if base_dir.exists():
            QMessageBox.critical(self, "Error", f"La carpeta '{folder_name}' ya existe. Prueba con otro nombre.")
            return

        try:
            # 1. Crear directorios internos de .egas y .gos
            sub_dirs = [
                base_dir / ".egas" / "editor",
                base_dir / ".egas" / "imported",
                base_dir / ".gos",
            ]
            for d in sub_dirs:
                d.mkdir(parents=True, exist_ok=True)

            # --- VARIABLES DE CONTROL DINÁMICAS ---
            width = self.width_input.value()
            height = self.height_input.value()
            vsync_val = "true" if self.vsync_check.isChecked() else "false"
            
            platforms = []
            if self.check_windows.isChecked(): platforms.append("Windows")
            if self.check_linux.isChecked(): platforms.append("Linux")
            if self.check_mac.isChecked(): platforms.append("MacOS")

            # 2. Guardar manifiesto de proyecto principal (proyecto.egas)
            proyecto_content = f"""[project]
name = "{project_name}"
version = "{self.version_input.text()}"
egas_version = "1.0.2"
main_scene = "{self.scene_input.text()}"
platforms = {platforms}
engine = ["egas", "pygame"]
rute_engine = "../Egas"

[render]
width = {width}
height = {height}
vsync = {vsync_val}
"""
            (base_dir / "proyecto.egas").write_text(proyecto_content, encoding="utf-8")

            # 3. 📂 Automatización de .egas/
            (base_dir / ".egas" / "config_engine_standar.cfg").write_text(
                "engine_name=egas\nversion=1.0.2\ndefault_renderer=pygame\nfps_limit=60\n", encoding="utf-8"
            )
            (base_dir / ".egas" / "run.cfg").write_text(
                f"current_scene={self.scene_input.text()}\nrun_mode=editor\nproject_path={base_dir.as_posix()}\n", encoding="utf-8"
            )

            # 4. 📂 Automatización de .egas/editor/
            (base_dir / ".egas" / "editor" / "route.cfg").write_text(
                "res_path=res://\nassets_path=res://assets/\nexport_path=res://build/\n", encoding="utf-8"
            )
            (base_dir / ".egas" / "editor" / "sixe_win_game.cfg").write_text(
                f"window_w={width}\nwindow_h={height}\nfullscreen=false\n", encoding="utf-8"
            )
            (base_dir / ".egas" / "editor" / "plataform_engine.cfg").write_text(
                f"build_targets={','.join(platforms)}\ncurrent_build_target=Windows\n", encoding="utf-8"
            )
            (base_dir / ".egas" / "editor" / "imagenes.cfg").write_text(
                "compression=lossless\nmax_texture_size=2048\ndefault_filter=linear\n", encoding="utf-8"
            )
            (base_dir / ".egas" / "editor" / "config_node.cfg").write_text(
                "editor_grid_size=32\nsnap_to_grid=true\nshow_colliders=true\n", encoding="utf-8"
            )
            (base_dir / ".egas" / "editor" / "config_ico.cfg").write_text(
                "icon_path=res://ico.svg.import\n", encoding="utf-8"
            )
            (base_dir / ".egas" / "editor" / "run_engine.cfg").write_text(
                "auto_reload_scripts=true\nclear_cache_on_run=true\n", encoding="utf-8"
            )

            # 5. 📂 Automatización de .egas/imported/
            for imp in ["egas", "gos", "node", "pygame"]:
                (base_dir / ".egas" / "imported" / f"{imp}.import").write_text(
                    "imported_at=auto_generated\nstatus=ok\nvalid=true\n", encoding="utf-8"
                )

            # 6. 📂 Automatización de .gos/ (El Lenguaje de Scripts GOS)
            (base_dir / ".gos" / "rute_config_lenguis.cfg").write_text(
                "stdlib_path=res://lib/gos/stdlib/\nuse_absolute_paths=false\n", encoding="utf-8"
            )
            (base_dir / ".gos" / "config.cfg").write_text(
                "allow_unsafe_code=false\nprint_stack_trace=true\nmax_memory_alloc=512MB\n", encoding="utf-8"
            )
            (base_dir / ".gos" / "run_gos.cfg").write_text(
                f"entry_point={self.scene_input.text()}\nexecution_timeout=5.0\n", encoding="utf-8"
            )

            # Metadato de icono inicial
            (base_dir / "ico.svg.import").write_text("status=unloaded\ndefault_fallback=true\n", encoding="utf-8")

            QMessageBox.information(
                self, "¡Éxito Automatizado!", 
                f"✅ El proyecto '{project_name}' ha sido configurado y guardado correctamente."
            )

            # 🚀 Abrir el explorador del S.O de forma automática
            if sys.platform == "win32":
                os.startfile(base_dir)
            else:
                import subprocess
                opener = "open" if sys.platform == "darwin" else "xdg-open"
                subprocess.call([opener, str(base_dir)])

        except Exception as e:
            QMessageBox.critical(self, "Error Crítico", f"Ocurrió un error escribiendo los ficheros: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EgasLauncher()
    window.show()
    sys.exit(app.exec())