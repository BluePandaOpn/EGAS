// --- Ajustes de la Cuadrícula ---
var celda = 40.0

// --- Reloj del Juego (Ticks) ---
var tiempo_acumulado = 0.0
var velocidad_tick = 0.15

// --- Direcciones (0: Derecha, 1: Abajo, 2: Izquierda, 3: Arriba) ---
var direccion_actual = 0
var direccion_siguiente = 0

// 🏆 CONTADOR DE PUNTOS
var puntos = 0

// 🍎 POSICIÓN INICIAL DE LA MANZANA
var manzana_x = 600.0
var manzana_y = 400.0

func _ready() {
    printc("🐍 Snake Iniciado! Puntos: 0")
}

func _physics_process(delta) {
    
    // 1. ⌨️ LEER TECLAS (Movimientos individuales e independientes)
    if (key_pressed("w")) {
        if (direccion_actual != 1) { direccion_siguiente = 3 }
    }
    if (key_pressed("up")) {
        if (direccion_actual != 1) { direccion_siguiente = 3 }
    }

    if (key_pressed("s")) {
        if (direccion_actual != 3) { direccion_siguiente = 1 }
    }
    if (key_pressed("down")) {
        if (direccion_actual != 3) { direccion_siguiente = 1 }
    }

    if (key_pressed("a")) {
        if (direccion_actual != 0) { direccion_siguiente = 2 }
    }
    if (key_pressed("left")) {
        if (direccion_actual != 0) { direccion_siguiente = 2 }
    }

    if (key_pressed("d")) {
        if (direccion_actual != 2) { direccion_siguiente = 0 }
    }
    if (key_pressed("right")) {
        if (direccion_actual != 2) { direccion_siguiente = 0 }
    }

    // 2. ⏳ RELOJ DEL JUEGO (El movimiento ocurre por Ticks)
    tiempo_acumulado = tiempo_acumulado + delta

    if (tiempo_acumulado >= velocidad_tick) {
        tiempo_acumulado = 0.0
        direccion_actual = direccion_siguiente

        var x = self.position_x
        var y = self.position_y

        if (direccion_actual == 0) { x = x + celda }
        if (direccion_actual == 1) { y = y + celda }
        if (direccion_actual == 2) { x = x - celda }
        if (direccion_actual == 3) { y = y - celda }

        // 🧱 COLISIÓN CON PAREDES (Pantalla de 1020x720)
        var choco = 0
        if (x < 0.0) { choco = 1 }
        if (x >= 1020.0) { choco = 1 }
        if (y < 0.0) { choco = 1 }
        if (y >= 720.0) { choco = 1 }

        if (choco == 1) {
            printc("💥 ¡GAME OVER! Chocaste con la pared.")
            x = 200.0
            y = 200.0
            direccion_actual = 0
            direccion_siguiente = 0
            puntos = 0
        }

        // 🍎 COLISIÓN CON LA MANZANA (Evaluados sin usar '&&')
        if (x == manzana_x) {
            if (y == manzana_y) {
                
                puntos = puntos + 1.0
                printc("🍎 ¡Manzana Comida! Puntos totales:", puntos)

                // Algoritmo matemático seguro para mover la manzana sin %
                manzana_x = manzana_x + (celda * 3.0)
                manzana_y = manzana_y + (celda * 2.0)

                if (manzana_x >= 960.0) {
                    manzana_x = 80.0
                }

                if (manzana_y >= 640.0) {
                    manzana_y = 80.0
                }

                printc("🍎 La manzana se movió a:", manzana_x, manzana_y)
            }
        }

        self.position_x = x
        self.position_y = y
    }
}