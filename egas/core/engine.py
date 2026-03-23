import time
from config.settings import Settings
from egas.core.logger import Logger

class Engine:
    """
    Orquestador principal del Main Loop del motor EGAS V2.0.
    Gestiona el tiempo, la sincronización de FPS y delega el procesamiento.
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

            # --- 📥 B. PROCESAMIENTO DE EVENTOS (Entradas de Teclado/Cierre) ---
            self._process_input()

            # --- 🧬 C. PROCESAMIENTO DE FÍSICAS ---
            self._process_physics(self.delta_time)

            # --- 🧠 D. PROCESAMIENTO DE LÓGICA (Scripts de GOS) ---
            self._process_logic(self.delta_time)

            # --- 🎨 E. PROCESAMIENTO DE DIBUJO (Renderizado) ---
            self._process_render()

            # --- ⏳ F. CONTROL DE FPS ---
            time.sleep(Settings.PHYSICS_TIMESTEP) # Simulación de frames por segundo

        self._shutdown()

    def _process_input(self):
        """Detecta teclado y mouse (Delega al Thirdparty Input System)."""
        # Aquí más adelante leeremos pygame.event.get()
        pass

    def _process_physics(self, dt: float):
        """Avanza la simulación del mundo físico."""
        if self.physics_manager:
            self.physics_manager.update(dt)

    def _process_logic(self, dt: float):
        """Ejecuta los scripts .gs sobre los nodos activos."""
        if self.scene_tree:
            self.scene_tree.update_scripts(dt)

    def _process_render(self):
        """Borra la pantalla y vuelve a dibujar los nodos."""
        if self.render_server:
            self.render_server.begin_frame()
            if self.scene_tree:
                self.scene_tree.render_nodes(self.render_server)
            self.render_server.end_frame()

    def _shutdown(self):
        """Apaga el motor limpiando la memoria."""
        Logger.system("🔴 Apagando motor EGAS V2.0. Guardando configuraciones...")
        # Limpieza de hilos, memoria de pygame, etc.

    def stop(self):
        """Detiene la bandera del bucle principal."""
        self.is_running = False