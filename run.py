import argparse
import configparser
import json
import os
import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from config.settings import Settings
from egas.core.logger import Logger
from egas.scene.parser import SceneParser
from egas.scene.tree import SceneTree
from thirdparty.nodes.base.node import Node
from thirdparty.nodes.node2d.node2d import Node2D
from thirdparty.nodes.node2d.visuals.sprite_2d import Sprite2D
from thirdparty.nodes.camera_2d import Camera2D
from thirdparty.nodes.timers.timer import Timer
from thirdparty.nodes.control.label import Label
from thirdparty.nodes.node2d.physics.area_2d import Area2D
from thirdparty.nodes.node2d.visuals.animated_sprite_2d import AnimatedSprite2D
from thirdparty.nodes.audio_player import AudioPlayer


ENGINE_VERSION = "1.0.2"
DEFAULT_MAIN_SCENE = "res://scenes/nivel1.dscn"

try:
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import (
        QApplication,
        QCheckBox,
        QFileDialog,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QMessageBox,
        QPushButton,
        QSpinBox,
        QVBoxLayout,
        QWidget,
    )
    PYQT_AVAILABLE = True
except ModuleNotFoundError:
    QApplication = None
    QCheckBox = QFileDialog = QHBoxLayout = QLabel = QLineEdit = QMessageBox = None
    QPushButton = QSpinBox = QVBoxLayout = QWidget = None
    Qt = None
    PYQT_AVAILABLE = False


def _parse_scalar(value: str) -> Any:
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
            return text

    try:
        if "." in text:
            return float(text)
        return int(text)
    except ValueError:
        return text


def _read_key_value_file(path: Path) -> dict[str, Any]:
    data: dict[str, Any] = {}
    if not path.exists():
        return data

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip()] = _parse_scalar(value)
    return data


def _read_ini_file(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}

    config = configparser.ConfigParser()
    config.read(path, encoding="utf-8")
    result: dict[str, dict[str, Any]] = {}
    for section in config.sections():
        result[section] = {}
        for key, value in config.items(section):
            result[section][key] = _parse_scalar(value)
    return result


@dataclass
class ProjectConfig:
    name: str
    version: str
    egas_version: str
    main_scene: str
    platforms: list[str] = field(default_factory=list)
    engine: list[str] = field(default_factory=lambda: ["egas", "pygame"])
    rute_engine: str = "../Egas"
    width: int = 1920
    height: int = 1080
    vsync: bool = True
    fullscreen: bool = False
    fps_limit: int = 60
    route_res: str = "res://"
    route_assets: str = "res://assets/"
    route_export: str = "res://build/"
    show_colliders: bool = True
    auto_reload_scripts: bool = True
    clear_cache_on_run: bool = True
    gos_allow_unsafe: bool = False
    gos_print_stack_trace: bool = True
    gos_max_memory: str = "512MB"
    gos_execution_timeout: float = 5.0
    current_build_target: str = "Windows"


class ResourceManager:
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir.resolve()
        self.user_dir = self.project_dir / ".egas" / "user"
        self.executor = ThreadPoolExecutor(max_workers=2)
        self._scene_future = None
        self._reload_lock = threading.Lock()
        self._last_script_mtimes: dict[Path, float] = {}

    def _default_project_config(self) -> ProjectConfig:
        project_name = self.project_dir.name.replace("_", " ").title()
        return ProjectConfig(
            name=project_name,
            version="1.0.0",
            egas_version=ENGINE_VERSION,
            main_scene=DEFAULT_MAIN_SCENE,
        )

    def ensure_project_layout(self) -> None:
        defaults = self._default_project_config()
        required_dirs = [
            self.project_dir / ".egas" / "editor",
            self.project_dir / ".egas" / "imported",
            self.project_dir / ".egas" / "user",
            self.project_dir / ".gos",
            self.project_dir / "assets",
            self.project_dir / "scenes",
            self.project_dir / "scripts",
            self.project_dir / "build",
        ]
        for directory in required_dirs:
            directory.mkdir(parents=True, exist_ok=True)

        project_manifest = self.project_dir / "proyecto.egas"
        if not project_manifest.exists():
            Logger.warning("ResourceManager", "Falta proyecto.egas. Recreando manifiesto principal.")
            self._write_project_manifest(project_manifest, defaults)

        run_cfg = self.project_dir / ".egas" / "run.cfg"
        if not run_cfg.exists():
            Logger.warning("ResourceManager", "Falta .egas/run.cfg. Recreando manifiesto de ejecución.")
            run_cfg.write_text(
                f"current_scene={defaults.main_scene}\nrun_mode=editor\nproject_path={self.project_dir.as_posix()}\n",
                encoding="utf-8",
            )

        editor_dir = self.project_dir / ".egas" / "editor"
        editor_defaults = {
            "route.cfg": "res_path=res://\nassets_path=res://assets/\nexport_path=res://build/\n",
            "sixe_win_game.cfg": "window_w=1920\nwindow_h=1080\nfullscreen=false\n",
            "plataform_engine.cfg": "build_targets=Windows\ncurrent_build_target=Windows\n",
            "imagenes.cfg": "compression=lossless\nmax_texture_size=2048\ndefault_filter=linear\n",
            "config_node.cfg": "editor_grid_size=32\nsnap_to_grid=true\nshow_colliders=true\n",
            "config_ico.cfg": "icon_path=res://ico.svg.import\n",
            "run_engine.cfg": "auto_reload_scripts=true\nclear_cache_on_run=true\n",
        }
        for filename, content in editor_defaults.items():
            target = editor_dir / filename
            if not target.exists():
                Logger.warning("ResourceManager", f"Falta {target.name}. Regenerando archivo por defecto.")
                target.write_text(content, encoding="utf-8")

        gos_defaults = {
            "rute_config_lenguis.cfg": "stdlib_path=res://lib/gos/stdlib/\nuse_absolute_paths=false\n",
            "config.cfg": "allow_unsafe_code=false\nprint_stack_trace=true\nmax_memory_alloc=512MB\n",
            "run_gos.cfg": f"entry_point={defaults.main_scene}\nexecution_timeout=5.0\n",
        }
        for filename, content in gos_defaults.items():
            target = self.project_dir / ".gos" / filename
            if not target.exists():
                Logger.warning("ResourceManager", f"Falta .gos/{filename}. Regenerando archivo por defecto.")
                target.write_text(content, encoding="utf-8")

        for imported_name in ("egas", "gos", "node", "pygame"):
            imported_path = self.project_dir / ".egas" / "imported" / f"{imported_name}.import"
            if not imported_path.exists():
                imported_path.write_text(
                    "imported_at=auto_generated\nstatus=ok\nvalid=true\n",
                    encoding="utf-8",
                )

        self.ensure_import_metadata(self.project_dir / "ico.svg")
        self._ensure_bootstrap_files(defaults.main_scene)

    def _ensure_bootstrap_files(self, main_scene: str) -> None:
        scene_path = self.resolve_path(main_scene)
        scene_path.parent.mkdir(parents=True, exist_ok=True)
        if not scene_path.exists():
            scene_path.write_text(
                "\n".join(
                    [
                        "[Main]",
                        "type = Node2D",
                        "",
                        "[Logo]",
                        "type = Sprite2D",
                        "parent = Main",
                        "position_x = 960",
                        "position_y = 540",
                        "texture = res://assets/placeholder.png",
                        "script = res://scripts/main.gs",
                        "",
                    ]
                ),
                encoding="utf-8",
            )

        main_script = self.project_dir / "scripts" / "main.gs"
        if not main_script.exists():
            main_script.write_text(
                "\n".join(
                    [
                        'var mensaje = "Proyecto EGAS listo"',
                        "",
                        "func _process(delta) {",
                        "    print(mensaje)",
                        "}",
                    ]
                ),
                encoding="utf-8",
            )

    def _write_project_manifest(self, path: Path, config: ProjectConfig) -> None:
        content = "\n".join(
            [
                "[project]",
                f'name = "{config.name}"',
                f'version = "{config.version}"',
                f'egas_version = "{config.egas_version}"',
                f'main_scene = "{config.main_scene}"',
                f"platforms = {json.dumps(config.platforms)}",
                f"engine = {json.dumps(config.engine)}",
                f'rute_engine = "{config.rute_engine}"',
                "",
                "[render]",
                f"width = {config.width}",
                f"height = {config.height}",
                f"vsync = {'true' if config.vsync else 'false'}",
                "",
            ]
        )
        path.write_text(content, encoding="utf-8")

    def load_project_config(self) -> ProjectConfig:
        self.ensure_project_layout()
        manifest = _read_ini_file(self.project_dir / "proyecto.egas")
        run_cfg = _read_key_value_file(self.project_dir / ".egas" / "run.cfg")
        route_cfg = _read_key_value_file(self.project_dir / ".egas" / "editor" / "route.cfg")
        window_cfg = _read_key_value_file(self.project_dir / ".egas" / "editor" / "sixe_win_game.cfg")
        platform_cfg = _read_key_value_file(self.project_dir / ".egas" / "editor" / "plataform_engine.cfg")
        node_cfg = _read_key_value_file(self.project_dir / ".egas" / "editor" / "config_node.cfg")
        engine_cfg = _read_key_value_file(self.project_dir / ".egas" / "editor" / "run_engine.cfg")
        gos_cfg = _read_key_value_file(self.project_dir / ".gos" / "config.cfg")
        gos_run_cfg = _read_key_value_file(self.project_dir / ".gos" / "run_gos.cfg")

        project_section = manifest.get("project", {})
        render_section = manifest.get("render", {})
        config = ProjectConfig(
            name=str(project_section.get("name", self.project_dir.name)),
            version=str(project_section.get("version", "1.0.0")),
            egas_version=str(project_section.get("egas_version", ENGINE_VERSION)),
            main_scene=str(run_cfg.get("current_scene", project_section.get("main_scene", DEFAULT_MAIN_SCENE))),
            platforms=list(project_section.get("platforms", ["Windows"])),
            engine=list(project_section.get("engine", ["egas", "pygame"])),
            rute_engine=str(project_section.get("rute_engine", "../Egas")),
            width=int(window_cfg.get("window_w", render_section.get("width", 1920))),
            height=int(window_cfg.get("window_h", render_section.get("height", 1080))),
            vsync=bool(render_section.get("vsync", True)),
            fullscreen=bool(window_cfg.get("fullscreen", False)),
            fps_limit=int(_read_key_value_file(self.project_dir / ".egas" / "config_engine_standar.cfg").get("fps_limit", 60)),
            route_res=str(route_cfg.get("res_path", "res://")),
            route_assets=str(route_cfg.get("assets_path", "res://assets/")),
            route_export=str(route_cfg.get("export_path", "res://build/")),
            show_colliders=bool(node_cfg.get("show_colliders", True)),
            auto_reload_scripts=bool(engine_cfg.get("auto_reload_scripts", True)),
            clear_cache_on_run=bool(engine_cfg.get("clear_cache_on_run", True)),
            gos_allow_unsafe=bool(gos_cfg.get("allow_unsafe_code", False)),
            gos_print_stack_trace=bool(gos_cfg.get("print_stack_trace", True)),
            gos_max_memory=str(gos_cfg.get("max_memory_alloc", "512MB")),
            gos_execution_timeout=float(gos_run_cfg.get("execution_timeout", 5.0)),
            current_build_target=str(platform_cfg.get("current_build_target", "Windows")),
        )

        self._warn_on_version_gap(config.egas_version)
        self._sync_runtime_manifest(config)
        return config

    def _sync_runtime_manifest(self, config: ProjectConfig) -> None:
        manifest_path = self.project_dir / "proyecto.egas"
        self._write_project_manifest(manifest_path, config)

    def _warn_on_version_gap(self, project_version: str) -> None:
        if project_version != ENGINE_VERSION:
            Logger.warning(
                "ResourceManager",
                f"Versión del proyecto {project_version} distinta al motor {ENGINE_VERSION}.",
            )

    def resolve_path(self, virtual_path: str) -> Path:
        if virtual_path.startswith("res://"):
            suffix = virtual_path.removeprefix("res://")
            return self.project_dir / suffix
        if virtual_path.startswith("user://"):
            suffix = virtual_path.removeprefix("user://")
            return self.user_dir / suffix
        return Path(virtual_path)

    def ensure_import_metadata(self, asset_path: Path) -> None:
        if asset_path.suffix == ".import":
            return

        import_path = asset_path.with_name(f"{asset_path.name}.import")
        if import_path.exists():
            return

        import_path.write_text(
            "imported_at=auto_generated\nstatus=ok\nvalid=true\n",
            encoding="utf-8",
        )

    def scan_asset_imports(self) -> None:
        for asset in self.project_dir.rglob("*"):
            if not asset.is_file():
                continue
            if asset.parts and ".egas" in asset.parts:
                continue
            if asset.suffix.lower() in {".png", ".jpg", ".jpeg", ".bmp", ".svg"}:
                self.ensure_import_metadata(asset)

    def preload_scene_async(self, scene_path: str):
        self._scene_future = self.executor.submit(self._load_scene, scene_path)
        return self._scene_future

    def _load_scene(self, scene_path: str):
        parser = SceneParser()
        return parser.load_scene(scene_path)

    def collect_script_paths(self, root_node) -> list[Path]:
        paths: list[Path] = []

        def walk(node) -> None:
            if node is None:
                return
            bridge = getattr(node, "script_bridge", None)
            script_path = getattr(bridge, "script_path", None)
            if script_path:
                paths.append(Path(script_path))
            for child in node.get_children():
                walk(child)

        walk(root_node)
        return paths

    def prime_script_watch(self, root_node) -> None:
        self._last_script_mtimes.clear()
        for path in self.collect_script_paths(root_node):
            if path.exists():
                self._last_script_mtimes[path] = path.stat().st_mtime

    def reload_scripts_if_needed(self, root_node) -> None:
        if root_node is None:
            return

        with self._reload_lock:
            for path in self.collect_script_paths(root_node):
                if not path.exists():
                    continue
                current_mtime = path.stat().st_mtime
                previous_mtime = self._last_script_mtimes.get(path)
                if previous_mtime is None:
                    self._last_script_mtimes[path] = current_mtime
                    continue
                if current_mtime <= previous_mtime:
                    continue

                self._last_script_mtimes[path] = current_mtime
                self._reload_node_script(root_node, path)

    def _reload_node_script(self, root_node, changed_script: Path) -> None:
        def walk(node) -> bool:
            bridge = getattr(node, "script_bridge", None)
            if bridge and Path(getattr(bridge, "script_path", "")).resolve() == changed_script.resolve():
                Logger.info("LiveReload", f"Recargando script {changed_script.name}")
                bridge.attach_script(bridge.virtual_script_path)
                return True
            return any(walk(child) for child in node.get_children())

        walk(root_node)

    def cleanup_runtime_cache(self, render_server: Any | None) -> None:
        if render_server and hasattr(render_server, "_texture_cache"):
            render_server._texture_cache.clear()
        Logger.info("ResourceManager", "Caché de ejecución liberada.")

    def write_crash_log(self, exc: BaseException) -> None:
        crash_log = self.project_dir / ".egas" / "crash.log"
        crash_log.write_text(
            f"error={type(exc).__name__}\nmessage={exc}\n",
            encoding="utf-8",
        )


class UnifiedRuntime:
    def __init__(self, project_dir: Path):
        from egas.core.engine import Engine
        from egas.physics.simulator import PhysicsSimulator
        from egas.render.server import PygameRenderServer

        self.project_dir = project_dir.resolve()
        self.resource_manager = ResourceManager(self.project_dir)
        self.engine = Engine()
        self.render_server = PygameRenderServer()
        self.physics_manager = PhysicsSimulator()
        self.scene_tree = SceneTree()
        self._original_cwd = Path.cwd()

    def boot(self) -> None:
        config = self.resource_manager.load_project_config()
        self._apply_settings(config)
        self._register_builtin_nodes()
        self.resource_manager.scan_asset_imports()

        os.chdir(self.project_dir)
        self.render_server.initialize(Settings.SCREEN_WIDTH, Settings.SCREEN_HEIGHT, Settings.VSYNC)

        future = self.resource_manager.preload_scene_async(config.main_scene)
        root_node = future.result()
        if root_node is None:
            raise RuntimeError(f"No se pudo cargar la escena inicial '{config.main_scene}'.")

        self.scene_tree.set_root(root_node)
        self.resource_manager.prime_script_watch(root_node)

        self.engine.render_server = self.render_server
        self.engine.physics_manager = self.physics_manager
        self.engine.scene_tree = self.scene_tree

        if config.auto_reload_scripts:
            self._install_live_reload_hook()

        Logger.system(f"Proyecto '{config.name}' listo. Escena inicial: {config.main_scene}")
        self.engine.run()

    def shutdown(self) -> None:
        try:
            if Settings.PROJECT_DIR:
                config = self.resource_manager.load_project_config()
                if config.clear_cache_on_run:
                    self.resource_manager.cleanup_runtime_cache(self.render_server)
        finally:
            os.chdir(self._original_cwd)

    def _apply_settings(self, config: ProjectConfig) -> None:
        Settings.PROJECT_DIR = self.project_dir
        Settings.BASE_DIR = self.project_dir
        Settings.TITLE = config.name
        Settings.SCREEN_WIDTH = config.width
        Settings.SCREEN_HEIGHT = config.height
        Settings.VSYNC = config.vsync
        Settings.FULLSCREEN = config.fullscreen
        Settings.FPS_LIMIT = config.fps_limit
        Settings.MAIN_SCENE = config.main_scene

    def _register_builtin_nodes(self) -> None:
        SceneParser.register_node_type("Node", Node)  
        SceneParser.register_node_type("Node2D", Node2D)
        SceneParser.register_node_type("Sprite2D", Sprite2D)
        SceneParser.register_node_type("Camera2D", Camera2D)
        SceneParser.register_node_type("Timer", Timer)
        SceneParser.register_node_type("Label", Label)
        SceneParser.register_node_type("Area2D", Area2D)
        SceneParser.register_node_type("AnimatedSprite2D", AnimatedSprite2D)
        SceneParser.register_node_type("AudioPlayer", AudioPlayer)
        

    def _install_live_reload_hook(self) -> None:
        original_process_logic = self.engine._process_logic

        def wrapped_process_logic(dt: float) -> None:
            self.resource_manager.reload_scripts_if_needed(self.scene_tree.get_root())
            original_process_logic(dt)

        self.engine._process_logic = wrapped_process_logic


def launch_project(project_dir: Path) -> int:
    runtime = UnifiedRuntime(project_dir)
    try:
        runtime.boot()
        return 0
    except Exception as exc:
        runtime.resource_manager.write_crash_log(exc)
        Logger.error("Runtime", f"Arranque fallido: {exc}")
        return 1
    finally:
        runtime.shutdown()


class EgasLauncher(QWidget if PYQT_AVAILABLE else object):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("EGAS Engine V2.0 - Gestor de Proyectos")
        self.resize(540, 660)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)

        title_lbl = QLabel("Crear Nuevo Proyecto EGAS")
        title_lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #2E7D32;")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_lbl)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ejemplo: Naves Espaciales")
        main_layout.addWidget(QLabel("Nombre del Juego:"))
        main_layout.addWidget(self.name_input)

        path_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setReadOnly(True)
        self.path_input.setText(str(Path.cwd()))
        btn_browse = QPushButton("Explorar...")
        btn_browse.clicked.connect(self.browse_folder)
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(btn_browse)
        main_layout.addWidget(QLabel("Ruta de creación:"))
        main_layout.addLayout(path_layout)

        self.version_input = QLineEdit("1.0.0")
        main_layout.addWidget(QLabel("Versión del Juego:"))
        main_layout.addWidget(self.version_input)

        self.scene_input = QLineEdit(DEFAULT_MAIN_SCENE)
        main_layout.addWidget(QLabel("Escena Inicial:"))
        main_layout.addWidget(self.scene_input)

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

        self.btn_create = QPushButton("Crear Proyecto Automatizado")
        self.btn_create.setStyleSheet(
            "background-color: #2E7D32; color: white; font-weight: bold; padding: 12px; font-size: 14px;"
        )
        self.btn_create.clicked.connect(self.create_project)
        main_layout.addWidget(self.btn_create)

        self.btn_open = QPushButton("Abrir Proyecto Existente")
        self.btn_open.clicked.connect(self.open_existing_project)
        main_layout.addWidget(self.btn_open)

        self.setLayout(main_layout)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta de Destino")
        if folder:
            self.path_input.setText(folder)

    def create_project(self):
        project_name = self.name_input.text().strip()
        if not project_name:
            QMessageBox.warning(self, "Error", "El nombre del proyecto no puede estar vacío.")
            return

        folder_name = project_name.lower().replace(" ", "_")
        base_dir = Path(self.path_input.text()) / folder_name

        if base_dir.exists():
            QMessageBox.critical(self, "Error", f"La carpeta '{folder_name}' ya existe.")
            return

        platforms = []
        if self.check_windows.isChecked():
            platforms.append("Windows")
        if self.check_linux.isChecked():
            platforms.append("Linux")
        if self.check_mac.isChecked():
            platforms.append("MacOS")
        if not platforms:
            platforms.append("Windows")

        try:
            config = ProjectConfig(
                name=project_name,
                version=self.version_input.text().strip() or "1.0.0",
                egas_version=ENGINE_VERSION,
                main_scene=self.scene_input.text().strip() or DEFAULT_MAIN_SCENE,
                platforms=platforms,
                width=self.width_input.value(),
                height=self.height_input.value(),
                vsync=self.vsync_check.isChecked(),
            )

            resource_manager = ResourceManager(base_dir)
            resource_manager.ensure_project_layout()
            resource_manager._write_project_manifest(base_dir / "proyecto.egas", config)
            (base_dir / ".egas" / "run.cfg").write_text(
                f"current_scene={config.main_scene}\nrun_mode=editor\nproject_path={base_dir.as_posix()}\n",
                encoding="utf-8",
            )
            (base_dir / ".egas" / "editor" / "sixe_win_game.cfg").write_text(
                f"window_w={config.width}\nwindow_h={config.height}\nfullscreen=false\n",
                encoding="utf-8",
            )
            (base_dir / ".egas" / "editor" / "plataform_engine.cfg").write_text(
                f"build_targets={','.join(config.platforms)}\ncurrent_build_target={config.platforms[0]}\n",
                encoding="utf-8",
            )
            resource_manager.scan_asset_imports()

            QMessageBox.information(
                self,
                "Proyecto Creado",
                f"El proyecto '{project_name}' fue configurado correctamente.",
            )
            self._open_in_file_explorer(base_dir)
        except Exception as exc:
            QMessageBox.critical(self, "Error Crítico", f"No se pudo crear el proyecto: {exc}")

    def open_existing_project(self):
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar Proyecto EGAS")
        if not folder:
            return

        project_dir = Path(folder)
        if not (project_dir / "proyecto.egas").exists():
            QMessageBox.warning(self, "Proyecto inválido", "La carpeta seleccionada no contiene proyecto.egas.")
            return

        QMessageBox.information(
            self,
            "Ejecutar Proyecto",
            "Se iniciará el motor con el proyecto seleccionado.",
        )
        self.close()
        raise SystemExit(launch_project(project_dir))

    def _open_in_file_explorer(self, path: Path) -> None:
        if sys.platform == "win32":
            os.startfile(path)
            return

        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, str(path)])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Launcher y runtime unificado de EGAS.")
    parser.add_argument("--project", type=Path, help="Ruta de un proyecto EGAS existente.")
    parser.add_argument("--play", action="store_true", help="Ejecuta directamente el proyecto indicado.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.project and args.play:
        return launch_project(args.project)

    if not PYQT_AVAILABLE:
        Logger.error("Launcher", "PyQt6 no está instalado. Usa '--project RUTA --play' o instala PyQt6.")
        return 1

    app = QApplication(sys.argv)
    window = EgasLauncher()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
