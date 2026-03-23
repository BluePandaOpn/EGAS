import math
import random
from egas.core.logger import Logger

class BuiltInFunctions:
    """
    Colección de funciones predefinidas globales de GOS.
    """
    
    @staticmethod
    def print_gos(*args):
        """Imprime en la consola del Logger del motor."""
        message = " ".join(str(arg) for arg in args)
        Logger.info("GOS Script", message)
        return None

    @staticmethod
    def sin_deg(deg):
        return math.sin(math.radians(deg))

    @staticmethod
    def cos_deg(deg):
        return math.cos(math.radians(deg))

    @staticmethod
    def random_range(min_val, max_val):
        return random.uniform(min_val, max_val)

# Mapeo que se inyectará al entorno global de GOS
BUILTINS = {
    "print": BuiltInFunctions.print_gos,
    "sin": BuiltInFunctions.sin_deg,
    "cos": BuiltInFunctions.cos_deg,
    "rand": BuiltInFunctions.random_range,
}