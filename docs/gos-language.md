# Lenguaje GOS

## Objetivo

GOS es el lenguaje de scripting del motor. Se usa para controlar nodos, responder al ciclo de vida y escribir logica de gameplay.

## Sintaxis base

```javascript
const speed = 240.0

func _process(delta) {
    if (action_pressed("move_right")) {
        self.position_x = self.position_x + (speed * delta)
    }
}
```

## Elementos soportados

- `var`
- `const`
- `func`
- `if / elif / else`
- `while`
- `return`
- llamadas a funciones
- acceso a propiedades con `.`
- asignacion a propiedades
- operadores `+ - * /`
- comparaciones `> >= < <= == !=`
- operadores `and`, `or`, `not`
- operador `|`
- operador `is`

## Literales

- numeros
- cadenas
- `true`
- `false`
- `nil`
- listas: `[1, 2, 3]`
- diccionarios: `{ "hp": 10, "name": "slime" }`

## Ciclo de vida soportado

- `_ready()`
- `_input(event)`
- `_physics_process(delta)`
- `_process(delta)`
- `_draw(render_server)`
- `_exit_tree()`

## Input recomendado

Usa acciones configurables antes que teclas crudas:

- `action_pressed("move_up")`
- `action_just_pressed("ui_accept")`
- `action_just_released("ui_cancel")`

En `_input(event)`, los eventos de teclado incluyen:

- `event.key_name`
- `event.pressed`
- `event.action_names`

`enter` y `return` se normalizan al mismo nombre canonico: `enter`.

## Acceso al nodo actual

El runtime inyecta `self` para referirse al nodo dueño del script.

## Cambio de escena

`change_scene(...)` encola el cambio y lo aplica al final del frame.

## Errores

Los errores del runtime intentan incluir:

- archivo
- funcion
- linea

Esto hace mas facil localizar problemas sin entrar al codigo Python del motor.
