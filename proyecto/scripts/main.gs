var mensaje = "Proyecto EGAS listo!"

func _ready() {
    print(mensaje)
}

func _physics_process(delta) {
    // 1. Crear variables locales del frame leyendo las de Python
    var x = self.position_x
    var y = self.position_y
    var velocidad = 250.0

    // 2. Moverse a la Derecha hasta llegar a 900 (400 + 500)
    if (x < 900.0) {
        if (y <= 400.0) {
            x = x + (velocidad * delta)
            if (x > 900.0) {
                x = 900.0
            }
        }
    }

    // 3. Moverse Abajo hasta llegar a 800 (400 + 400)
    if (x >= 900.0) {
        if (y < 800.0) {
            y = y + (velocidad * delta)
            if (y > 800.0) {
                y = 800.0
            }
        }
    }

    // 4. Moverse a la Izquierda hasta 400 (900 - 500)
    if (y >= 800.0) {
        if (x > 400.0) {
            x = x - (velocidad * delta)
            if (x < 400.0) {
                x = 400.0
            }
        }
    }

    // 5. Moverse Arriba hasta 400 (Volver al origen)
    if (x <= 400.0) {
        if (y > 400.0) {
            y = y - (velocidad * delta)
            if (y < 400.0) {
                y = 400.0
            }
        }
    }

    // 🚀 Guardar de vuelta en el objeto real de Python
    self.position_x = x
    self.position_y = y
}