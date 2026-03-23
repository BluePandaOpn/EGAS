var mensaje = "Proyecto EGAS listo!"

// Usaremos un "paso" para controlar la dirección
// 0 = Derecha, 1 = Abajo, 2 = Izquierda, 3 = Arriba
var paso_actual = 0 

func _ready() {
    print(mensaje)
}

func _physics_process(delta) {
    var x = self.position_x
    var y = self.position_y
    var velocidad = 250.0

    // ➡️ PASO 0: Moverse a la Derecha hasta 900
    if (paso_actual == 0) {
        x = x + (velocidad * delta)
        if (x >= 900.0) {
            x = 900.0
            paso_actual = 1 // Ahora baja
        }
    }

    // ⬇️ PASO 1: Moverse Abajo hasta 800
    if (paso_actual == 1) {
        y = y + (velocidad * delta)
        if (y >= 800.0) {
            y = 800.0
            paso_actual = 2 // Ahora va a la izquierda
        }
    }

    // ⬅️ PASO 2: Moverse a la Izquierda hasta 400
    if (paso_actual == 2) {
        x = x - (velocidad * delta)
        if (x <= 400.0) {
            x = 400.0
            paso_actual = 3 // Ahora sube
        }
    }

    // ⬆️ PASO 3: Moverse Arriba hasta 400 (Origen)
    if (paso_actual == 3) {
        y = y - (velocidad * delta)
        if (y <= 400.0) {
            y = 400.0
            paso_actual = 0 // 🔄 ¡Reinicia el bucle a la derecha!
        }
    }

    // 🚀 Guardar posiciones actualizadas en Python
    self.position_x = x
    self.position_y = y
}