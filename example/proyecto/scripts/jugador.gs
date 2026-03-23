var velocidad = 260.0

func _ready() {
    printc("Jugador listo. Movimiento con WASD o flechas. Click izquierdo para log.")
}

func _physics_process(delta) {
    var x = self.position_x
    var y = self.position_y

    if (key_pressed("d")) {
        x = x + (velocidad * delta)
    }

    if (key_pressed("right")) {
        x = x + (velocidad * delta)
    }

    if (key_pressed("a")) {
        x = x - (velocidad * delta)
    }

    if (key_pressed("left")) {
        x = x - (velocidad * delta)
    }

    if (key_pressed("s")) {
        y = y + (velocidad * delta)
    }

    if (key_pressed("down")) {
        y = y + (velocidad * delta)
    }

    if (key_pressed("w")) {
        y = y - (velocidad * delta)
    }

    if (key_pressed("up")) {
        y = y - (velocidad * delta)
    }

    self.position_x = x
    self.position_y = y

    if (key_just_pressed("space")) {
        print("Accion detectada con SPACE")
    }

    if (mouse_just_pressed(1)) {
        printc("Mouse actual en", mouse_x(), mouse_y())
    }
}

func _input(event) {
    if (event is InputEventMouseButton) {
        if (event.pressed == true) {
            if (event.button_index == 1) {
                printc("Click izquierdo en", event.position_x, event.position_y)
            }
        }
    }

    if (event is InputEventKey) {
        if (event.pressed == true) {
            if (event.key_name == "tab") {
                printc("TAB presionada")
            }
        }
    }
}
