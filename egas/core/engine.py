import time
import pygame
from config.settings import Settings
from egas.core.logger import Logger
from thirdparty.input_system import InputSystem, InputEvent  # Importamos el sistema actualizado

class Engine:
    """
    Orquestador principal del Main Loop del motor EGAS V2.0.
    Gestiona el tiempo, la sincronización de FPS y delega el procesamiento.
    Ahora integra el ciclo de vida de Godot (_input, _process, _physics_process).
    """
    
    def __init__(self):
        self.is_running = False
        self.fps_clock = None
        self.delta_time = 0.0 # Tiempo transcurrido entre frames en segundos
        
        # Referencias a los subsistemas (Se inyectan después)
        self.render_server = None
        self.physics_manager = None
        self.scene_tree = None

    def initialize(self):
        """Prepara todos los subsistemas del motor antes de arrancar."""
        Logger.system("Iniciando secuencia de arranque de EGAS V2.0...")
        
        # 1. Configurar pantalla (Pygame se inicializará en el RenderServer)
        Logger.info("Engine", f"Resolución de pantalla configurada a {Settings.SCREEN_WIDTH}x{Settings.SCREEN_HEIGHT}")
        
        # 2. Preparar el Árbol de Escena (Nodos)
        Logger.info("Engine", "Estructura de SceneTree preparada para recibir nodos.")

        # 3. Encender físicas
        Logger.info("Engine", f"Físicas configuradas a {Settings.GRAVITY} m/s².")

        Logger.success("Engine", "¡Todos los sistemas centrales han arrancado con éxito!")
        self.is_running = True

        # 🔥 DISPARAR _ready() EN EL ÁRBOL DE ESCENAS AL INICIAR EL JUEGO
        if self.scene_tree:
            self.scene_tree.propagate_ready()

    def run(self):
        """Arranca el bucle principal de ejecución."""
        self.initialize()

        last_time = time.time()
        
        Logger.system("🟢 Entrando en el Main Loop (Ciclo de Vida Activo)")

        while self.is_running:
            # --- 🕒 A. CÁLCULO DEL DELTA TIME ---
            current_time = time.time()
            self.delta_time = current_time - last_time
            last_time = current_time

            # --- 📥 B. PROCESAMIENTO DE EVENTOS (Entradas de Teclado/Mouse/Cierre) ---
            if not self._process_input():
                self.stop()
                continue

            # --- 🧬 C. PROCESAMIENTO DE FÍSICAS (_physics_process) ---
            self._process_physics(self.delta_time)

            # --- 🧠 D. PROCESAMIENTO DE LÓGICA VISUAL (_process) ---
            self._process_logic(self.delta_time)

            # --- 🎨 E. PROCESAMIENTO DE DIBUJO (_draw y Renderizado) ---
            self._process_render()

            # --- ⏳ F. CONTROL DE FPS ---
            # Idealmente usa un clock de pygame.time.Clock() si lo inicializas en RenderServer,
            # pero por ahora mantenemos tu sincronización limpia.
            time.sleep(Settings.PHYSICS_TIMESTEP) 

        self._shutdown()

    def _process_input(self) -> bool:
        """
        Lee eventos de Pygame y los reparte por el Scene Tree 
        usando el método _input(event).
        """
        eventos = InputSystem.update()

        # Si el usuario clickea la 'X' de cerrar ventana, devuelve lista vacía
        if pygame.event.peek(pygame.QUIT):
            return False

        if self.scene_tree:
            for event in eventos:
                self.scene_tree.propagate_input(event)

        return True

    def _process_physics(self, dt: float):
        """Avanza la simulación física y avisa a los nodos con _physics_process."""
        if self.physics_manager:
            self.physics_manager.update(dt)

        if self.scene_tree:
            self.scene_tree.propagate_physics_process(dt)

    def _process_logic(self, dt: float):
        """Ejecuta los scripts .gs sobre los nodos activos para lógica visual (_process)."""
        if self.scene_tree:
            self.scene_tree.propagate_process(dt)

    def _process_render(self):
        """Dibuja personalizados (_draw) y pinta los sprites del servidor de renderizado."""
        if self.render_server:
            self.render_server.begin_frame()

            if self.scene_tree:
                # Disparamos las primitivas de dibujo GOS (_draw) antes de dibujar sprites
                self.scene_tree.propagate_draw(self.render_server)
                self.scene_tree.render_nodes(self.render_server)

            self.render_server.end_frame()

    def _shutdown(self):
        """Apaga el motor limpiando la memoria y avisando a los nodos."""
        if self.scene_tree:
            self.scene_tree.propagate_exit_tree()
            
        Logger.system("🔴 Apagando motor EGAS V2.0. Guardando configuraciones...")

    def stop(self):
        """Detiene la bandera del bucle principal."""
        self.is_running = False