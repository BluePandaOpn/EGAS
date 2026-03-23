var celda = 40.0

func _ready() {
    printc("🍎 Manzana lista en la escena.")
}

// Función para mover la manzana sin usar el símbolo %
func mover_manzana(nuevo_x, nuevo_y) {
    var nx = nuevo_x
    var ny = nuevo_y

    // --- Validación de bordes Izquierdo y Superior ---
    if (nx <= 0.0) { 
        nx = 80.0 
    }
    if (ny <= 0.0) { 
        ny = 80.0 
    }

    // --- Validación de bordes Derecho e Inferior (Pantalla 1020x720) ---
    if (nx >= 960.0) { 
        nx = 120.0 
    }
    if (ny >= 640.0) { 
        ny = 120.0 
    }

    // Aplicar las nuevas coordenadas al motor en Python
    self.position_x = nx
    self.position_y = ny

    printc("🍎 Manzana reposicionada en:", nx, ny)
}

func _physics_process(delta) {
    // La manzana no necesita moverse por sí sola en cada tick, 
    // se queda quieta esperando a ser comida.
}