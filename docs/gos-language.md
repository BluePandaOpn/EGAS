# Lenguaje GOS

## Objetivo

GOS es el lenguaje de scripting del motor. Se usa para controlar nodos, responder al ciclo de vida y escribir logica de gameplay.

## Sintaxis base

GOS usa una sintaxis inspirada en C o JavaScript:

```javascript
var speed = 240.0

func _process(delta) {
    self.position_x = self.position_x + (speed * delta)
}
```

## Elementos soportados

- `var`
- `func`
- `if / else`
- `while`
- `return`
- llamadas a funciones
- acceso a propiedades con `.`
- asignacion a propiedades
- operadores `+ - * /`
- comparaciones `> >= < <= == !=`
- operador `is`

## Literales

- numeros
- cadenas
- `true`
- `false`
- `nil`

## Ciclo de vida soportado

Un script puede definir estas funciones si el nodo las necesita:

- `_ready()`
- `_input(event)`
- `_physics_process(delta)`
- `_process(delta)`
- `_draw(render_server)`
- `_exit_tree()`

## Acceso al nodo actual

El runtime inyecta `self` para referirse al nodo dueño del script.

Ejemplo:

```javascript
func _ready() {
    self.position_x = 100
    self.position_y = 180
}
```

## Acceso a otros nodos

Desde GOS puedes usar funciones del runtime como:

- `get_root()`
- `get_node("Ruta/Del/Nodo")`
- `load_scene(...)`
- `change_scene(...)`

## Alcance actual

GOS ya sirve para gameplay basico y scripting de escenas. Si necesitas una capacidad concreta, revisa primero el parser y el interprete para confirmar si esa sintaxis ya existe.
