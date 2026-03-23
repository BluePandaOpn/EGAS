import time

from config.settings import Settings
from egas.core.logger import Logger
from thirdparty.input_system import InputEventWindowClose, InputSystem


class Engine:
    """
    Orquestador principal del main loop de EGAS.
    Gestiona tiempo, fisicas, logica y render.
    """

    def __init__(self):
        self.is_running = False
        self.fps_clock = None
        self.delta_time = 0.0

        self.render_server = None
        self.physics_manager = None
        self.scene_tree = None

    def initialize(self):
        """Prepara todos los subsistemas del motor antes de arrancar."""
        Logger.system("Iniciando secuencia de arranque de EGAS V2.0...")
        Logger.info(
            "Engine",
            f"Resolucion de pantalla configurada a {Settings.SCREEN_WIDTH}x{Settings.SCREEN_HEIGHT}",
        )
        Logger.info("Engine", "Estructura de SceneTree preparada para recibir nodos.")
        Logger.info("Engine", f"Fisicas configuradas a {Settings.GRAVITY} m/s^2.")
        Logger.success("Engine", "Todos los sistemas centrales han arrancado con exito.")
        self.is_running = True

        if self.scene_tree:
            self.scene_tree.propagate_ready()

    def run(self):
        """Arranca el bucle principal de ejecucion."""
        self.initialize()

        last_time = time.time()
        Logger.system("Entrando en el Main Loop (Ciclo de Vida Activo)")

        while self.is_running:
            current_time = time.time()
            self.delta_time = current_time - last_time
            last_time = current_time

            if not self._process_input():
                self.stop()
                continue

            self._process_physics(self.delta_time)
            self._process_logic(self.delta_time)
            self._process_render()

            time.sleep(Settings.PHYSICS_TIMESTEP)

        self._shutdown()

    def _process_input(self) -> bool:
        """
        Lee eventos de Pygame y los reparte por el Scene Tree
        usando el metodo _input(event).
        """
        eventos = InputSystem.update()

        if any(isinstance(event, InputEventWindowClose) for event in eventos):
            return False

        if self.scene_tree:
            for event in eventos:
                self.scene_tree.propagate_input(event)

        return True

    def _process_physics(self, dt: float):
        """Avanza la simulacion fisica y avisa a los nodos."""
        if self.physics_manager:
            self.physics_manager.update(dt)

        if self.scene_tree:
            self.scene_tree.propagate_physics_process(dt)

    def _process_logic(self, dt: float):
        """Ejecuta la logica visual (_process)."""
        if self.scene_tree:
            self.scene_tree.propagate_process(dt)

    def _process_render(self):
        """Ejecuta draw y renderizado del frame."""
        if self.render_server:
            self.render_server.begin_frame()

            if self.scene_tree:
                self.scene_tree.render_scene(self.render_server)

            self.render_server.end_frame()

    def _shutdown(self):
        """Apaga el motor limpiando memoria y avisando a los nodos."""
        if self.scene_tree:
            self.scene_tree.propagate_exit_tree()

        Logger.system("Apagando motor EGAS V2.0. Guardando configuraciones...")

    def stop(self):
        """Detiene la bandera del bucle principal."""
        self.is_running = False
