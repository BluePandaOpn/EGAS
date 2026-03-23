# Nodos disponibles

## Base

### `Node`

Nodo estructural base. Gestiona nombre, padre, hijos y ciclo de vida.

### `Node2D`

Nodo espacial 2D. Añade:

- posicion local y global
- rotacion
- escala
- `z_index`

## Visuales 2D

### `Sprite2D`

Dibuja una textura fija con `texture = res://...`.

### `AnimatedSprite2D`

Gestiona animaciones por fotogramas.

### `Camera2D`

Nodo de camara 2D. La base existe, pero la parte de comportamiento aun es simple.

## Fisicas y colision

### `Area2D`

Area de deteccion basica por caja. Puede disparar `_on_body_entered` y `_on_body_exited`.

### `CharacterBody2D`

Cuerpo para personajes controlados por codigo. La API existe, pero el comportamiento todavia es basico.

### `CollisionShape2D`

Forma de colision simple. Se usa como hijo de nodos 2D y tambien puede mostrar su debug visual.

### `RigidBody2D` y `StaticBody2D`

Nodos fisicos base presentes en el proyecto. Su estado actual es inicial y conviene revisar su codigo antes de usarlos en un proyecto grande.

## UI

### `Control`

Base para interfaz. Usa coordenadas de pantalla y tamaño.

### `CanvasLayer`

Capa de interfaz separada del mundo 2D.

### `Label`

Texto de interfaz.

### `ColorRect`

Panel o bloque de color para HUD, overlays y fondos de UI.

### `Button`

Boton simple con deteccion basica de hover y click.

## Otros

### `Timer`

Temporizador utilitario.

### `AudioPlayer`

Nodo para audio.

### `SnakeGame2D`

Nodo de ejemplo usado por `example/snake`. No forma parte del nucleo minimo del motor; sirve como demo jugable.

## Donde se implementan

- Base: [`thirdparty/nodes/base/`](../thirdparty/nodes/base)
- Control/UI: [`thirdparty/nodes/control/`](../thirdparty/nodes/control)
- Node2D: [`thirdparty/nodes/node2d/`](../thirdparty/nodes/node2d)
- Audio: [`thirdparty/nodes/audio_player.py`](../thirdparty/nodes/audio_player.py)
- Timers: [`thirdparty/nodes/timers/timer.py`](../thirdparty/nodes/timers/timer.py)
