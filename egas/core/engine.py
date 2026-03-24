import time

from config.settings import Settings
from egas.core.logger import Logger
from egas.core.runtime_services import RuntimeServices
from thirdparty.input_system import InputEventWindowClose, InputSystem


class Engine:
    """Orquestador principal del main loop de EGAS."""

    def __init__(self):
        self.is_running = False
        self.fps_clock = None
        self.delta_time = 0.0
        self.render_server = None
        self.physics_manager = None
        self.scene_tree = None

    def initialize(self):
        Logger.system("Iniciando secuencia de arranque de EGAS.")
        Logger.info("Engine", f"Resolucion configurada a {Settings.SCREEN_WIDTH}x{Settings.SCREEN_HEIGHT}")
        Logger.info("Engine", f"Fisicas configuradas a {Settings.GRAVITY} m/s^2.")
        self.is_running = True

        if self.scene_tree:
            self._debug_lifecycle("ready")
            self.scene_tree.propagate_ready()

    def run(self):
        self.initialize()
        last_time = time.time()
        Logger.system("Entrando en el Main Loop")

        while self.is_running:
            current_time = time.time()
            self.delta_time = current_time - last_time
            last_time = current_time

            if not self._process_input():
                self.stop()
                continue

            self._process_physics(self.delta_time)
            self._process_logic(self.delta_time)
            RuntimeServices.flush_pending_scene_change()
            self._process_render()
            time.sleep(Settings.PHYSICS_TIMESTEP)

        self._shutdown()

    def _process_input(self) -> bool:
        self._debug_lifecycle("_input")
        events = InputSystem.update()
        if any(isinstance(event, InputEventWindowClose) for event in events):
            return False

        if self.scene_tree:
            for event in events:
                self.scene_tree.propagate_input(event)
        return True

    def _process_physics(self, dt: float):
        self._debug_lifecycle("_physics_process")
        if self.physics_manager:
            self.physics_manager.update(dt)
        if self.scene_tree:
            self.scene_tree.propagate_physics_process(dt)

    def _process_logic(self, dt: float):
        self._debug_lifecycle("_process")
        if self.scene_tree:
            self.scene_tree.propagate_process(dt)

    def _process_render(self):
        self._debug_lifecycle("_draw")
        if self.render_server:
            self.render_server.begin_frame()
            if self.scene_tree:
                self.scene_tree.render_scene(self.render_server)
            self.render_server.end_frame()

    def _shutdown(self):
        if self.scene_tree:
            self.scene_tree.propagate_exit_tree()
        Logger.system("Apagando motor EGAS.")

    def stop(self):
        self.is_running = False

    @staticmethod
    def _debug_lifecycle(stage: str):
        if Settings.DEBUG_LIFECYCLE:
            Logger.debug("Lifecycle", f"Etapa {stage}")
