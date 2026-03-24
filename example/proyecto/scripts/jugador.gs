const velocidad = 260.0

func _ready() {
    printc("Jugador listo. Usa acciones move_* y ui_accept.")
}

func _physics_process(delta) {
    var x = self.position_x
    var y = self.position_y

    if (action_pressed("move_right")) {
        x = x + (velocidad * delta)
    }

    if (action_pressed("move_left")) {
        x = x - (velocidad * delta)
    }

    if (action_pressed("move_down")) {
        y = y + (velocidad * delta)
    }

    if (action_pressed("move_up")) {
        y = y - (velocidad * delta)
    }

    self.position_x = x
    self.position_y = y

    if (action_just_pressed("ui_accept")) {
        print("Accion detectada con ui_accept")
    }

    if (mouse_just_pressed(1)) {
        printc("Mouse actual en", mouse_x(), mouse_y())
    }
}

func _input(event) {
    if (event is InputEventMouseButton and event.pressed == true and event.button_index == 1) {
        printc("Click izquierdo en", event.position_x, event.position_y)
    }

    if (event is InputEventKey and event.pressed == true) {
        if (event.key_name == "tab") {
            printc("TAB presionada")
        }

        if (len(event.action_names) > 0) {
            printc("Acciones del evento:", str(event.action_names))
        }
    }
}
