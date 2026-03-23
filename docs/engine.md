# Arquitectura del motor

## Capas principales

### `run.py`

Es el punto de entrada. Hace tres cosas:

- abre el launcher PyQt6 si no se pasa `--project --play`
- carga configuracion del proyecto
- registra nodos y arranca el runtime unificado

### `egas/core/`

- `engine.py`: ciclo principal, input, fisicas, logica y render
- `logger.py`: salida de consola del motor
- `runtime_services.py`: acceso global para cambio de escena y busqueda de nodos

### `egas/scene/`

- `parser.py`: reconstruye escenas `.dscn`
- `tree.py`: mantiene el `SceneTree`
- `script.py`: puente entre un nodo Python y un script GOS

### `egas/render/`

- `server.py`: backend actual de render sobre Pygame
- `texture.py`: envoltorio de texturas

### `egas/physics/`

- `simulator.py`: actualizacion de fisicas
- `solver.py`: operaciones de colision

## Ciclo de vida de una escena

1. `SceneParser` carga la escena inicial.
2. `SceneTree.set_root()` activa el nodo raiz.
3. `Engine.initialize()` dispara `_ready`.
4. Cada frame:
   - `_input`
   - `_physics_process`
   - `_process`
   - `_draw` y `draw`
5. Al cerrar:
   - `_exit_tree`

## Orden de dibujado

El render sigue el arbol activo:

- el padre se dibuja antes que los hijos
- los hijos se dibujan por encima del padre
- entre hermanos se ordena por `z_index`

Esto permite construir UI y capas visuales de forma parecida a Godot.

## Registro de nodos

Los tipos de nodo se registran en `UnifiedRuntime._register_builtin_nodes()` dentro de [`run.py`](../run.py). Si se crea un nodo nuevo en Python, hay que registrarlo ahi para poder usarlo en escenas `.dscn`.
