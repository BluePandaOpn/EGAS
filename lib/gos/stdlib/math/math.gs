/*
  ==========================================
  GOS Standard Library - Math Module
  Módulo de cálculos matemáticos para EGAS.
  ==========================================
*/

func clamp(value, min_val, max_val) {
    if (value < min_val) { return min_val } // Forzar límite mínimo
    if (value > max_val) { return max_val } // Forzar límite máximo
    return value
}

func lerp(a, b, t) {
    /* Interpolación lineal: 
      Útil para mover cámaras o naves suavemente.
    */
    return a + (b - a) * t
}

func abs(value) {
    if (value < 0) { return -value }
    return value
}