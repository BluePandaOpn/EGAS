from .io import IO_EXTENSIONS

# Recopila todas las funciones escritas en Python puro para que GOS las entienda
STDLIB_BUILTINS = {}

# Unimos las de Entrada y Salida (Archivos y JSON)
STDLIB_BUILTINS.update(IO_EXTENSIONS)

# Aquí podrás añadir extensiones futuras (Audio, Redes, etc.)
# STDLIB_BUILTINS.update(AUDIO_EXTENSIONS)

def get_stdlib_extensions():
    """Retorna el diccionario unificado para el Interpreter."""
    return STDLIB_BUILTINS