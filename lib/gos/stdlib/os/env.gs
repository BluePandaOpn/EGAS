/*
  ==========================================
  GOS Standard Library - OS / Environment
  Variables de estado de la computadora.
  ==========================================
*/

func get_engine_version() {
    return "EGAS Engine V2.0 (GOS Framework active)"
}

func is_debug_mode() {
    return true // Cambiar a false en compilación final de tu videojuego
}

func get_platform() {
    return "Windows / PC Desktop"
}