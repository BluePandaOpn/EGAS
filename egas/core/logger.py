import datetime

class Logger:
    """
    Sistema de diagnóstico centralizado de EGAS Engine V2.0.
    Permite imprimir mensajes formateados por categorías (INFO, WARNING, ERROR, SUCCESS).
    """
    
    # Códigos de colores ANSI para la terminal
    RESET = "\033[0m"
    BOLD = "\033[1m"
    CYAN = "\033[36m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    GREEN = "\033[32m"

    @classmethod
    def _get_timestamp(cls) -> str:
        """Obtiene la estampa de tiempo actual."""
        return datetime.datetime.now().strftime("%H:%M:%S")

    @classmethod
    def info(cls, context: str, message: str):
        """Mensaje informativo estándar."""
        print(f"[{cls._get_timestamp()}] {cls.CYAN}[INFO]{cls.RESET} [{context}] {message}")

    @classmethod
    def success(cls, context: str, message: str):
        """Mensaje de éxito o carga exitosa."""
        print(f"[{cls._get_timestamp()}] {cls.GREEN}[SUCCESS]{cls.RESET} [{context}] {message}")

    @classmethod
    def warning(cls, context: str, message: str):
        """Mensajes de advertencia (amarillo)."""
        print(f"[{cls._get_timestamp()}] {cls.YELLOW}[WARNING]{cls.RESET} [{context}] {message}")

    @classmethod
    def error(cls, context: str, message: str):
        """Mensajes de error crítico (rojo y negrita)."""
        print(f"[{cls._get_timestamp()}] {cls.RED}{cls.BOLD}[ERROR]{cls.RESET} [{context}] {message}")

    @classmethod
    def system(cls, message: str):
        """Mensajes del sistema de bajo nivel del motor."""
        print(f"[{cls._get_timestamp()}] {cls.BOLD}⚙️  [EGAS SYSTEM]{cls.RESET} {message}")