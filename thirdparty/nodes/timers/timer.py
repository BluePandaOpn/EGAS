from thirdparty.nodes.base.node import Node
from egas.core.logger import Logger


class Timer(Node):
    """
    Nodo Timer para el motor EGAS.
    Cuenta hacia atrás y ejecuta funciones cuando el tiempo llega a cero.
    """

    def __init__(self):
        super().__init__()
        self.set_name("Timer")

        # --- Propiedades de Configuración ---
        self.wait_time = 1.0   # Tiempo total que durará la cuenta atrás (en segundos)
        self.time_left = 1.0   # Tiempo restante actual
        self.one_shot = False  # Si es True, se detiene al terminar. Si es False, se reinicia.
        self.autostart = False # Si inicia automáticamente al nacer el nodo

        # --- Estado interno ---
        self.is_running = False

    def ready(self):
        """Se ejecuta al iniciar el nodo en el árbol de escenas."""
        super().ready()
        if self.autostart:
            self.start()

    def process(self, delta: float):
        """
        Resta el tiempo del frame actual (delta) al temporizador.
        Se ejecuta 60 veces por segundo.
        """
        super().process(delta)

        if not self.is_running:
            return

        self.time_left -= delta

        if self.time_left <= 0:
            self._timeout()

    def _timeout(self):
        """
        Se dispara cuando el contador llega a cero.
        Llama a la función de GOS y decide si se reinicia.
        """
        # 1. Avisar a la consola que el tiempo terminó
        Logger.info("Timer", f"¡El temporizador '{self.get_name()}' ha terminado!")

        # 2. 🚀 EJECUTAR CÓDIGO EN TU LENGUAJE GOS
        # Busca si el nodo tiene un script .gs pegado con la función '_on_timeout'
        if hasattr(self, "script_bridge") and self.script_bridge:
            self.script_bridge.call("_on_timeout")

        # 3. Decidir si se detiene (OneShot) o hace bucle (Loop)
        if self.one_shot:
            self.stop()
        else:
            self.time_left = self.wait_time # Reiniciar la cuenta

    # --- 🛠️ Funciones de Control accesibles desde GOS ---

    def start(self, time: float = -1.0):
        """Inicia el temporizador. Si pasas un número, sobreescribe el wait_time."""
        if time > 0:
            self.wait_time = time

        self.time_left = self.wait_time
        self.is_running = True
        Logger.info("Timer", f"Temporizador '{self.get_name()}' iniciado ({self.wait_time}s).")

    def stop(self):
        """Detiene la cuenta y la resetea."""
        self.is_running = False
        self.time_left = self.wait_time

    def set_paused(self, paused: bool):
        """Pausa o despausa el temporizador sin resetear el tiempo restante."""
        self.is_running = not paused

    def get_time_left(self) -> float:
        """Devuelve cuánto tiempo falta para terminar."""
        return max(0.0, self.time_left)