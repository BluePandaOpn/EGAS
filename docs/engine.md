# Arquitectura del motor

## Capas principales

### `run.py`

Punto de entrada. Carga el proyecto, registra nodos y arranca el runtime.

### `egas/core/`

- `engine.py`: ciclo principal, input, fisicas, logica y render
- `logger.py`: salida de consola y trazas de debug
- `runtime_services.py`: acceso global a escenas y nodos

### `egas/scene/`

- `parser.py`: reconstruye escenas `.dscn`
- `tree.py`: mantiene el `SceneTree`
- `script.py`: puente entre un nodo Python y un script GOS

## Ciclo de vida oficial

El orden del frame es:

1. `_input(event)` para cada evento del frame
2. `_physics_process(delta)`
3. `_process(delta)`
4. aplicar `change_scene(...)` encolado
5. `_draw(render_server)` y `draw(render_server)`

Al arrancar una escena:

1. `SceneParser` la carga
2. `SceneTree.set_root()` activa el nodo raiz
3. `Engine.initialize()` dispara `_ready()`

Al cerrar o reemplazar la escena activa:

- `_exit_tree()`

## Cambio de escena

`change_scene(path)` ya no cambia la escena en mitad del callback actual.
Ahora encola el cambio y lo aplica al final del frame, despues de `_process`.
Esto evita estados intermedios raros desde `_input` o `_physics_process`.

## Debug del ciclo de vida

Puedes activar trazas del loop en `proyecto.egas`:

```ini
[debug]
lifecycle = true
input = true
```

Con eso el motor imprime por consola las etapas del frame y los eventos recibidos.

## Orden de dibujado

- el padre se dibuja antes que los hijos
- los hijos se dibujan por encima del padre
- entre hermanos se ordena por `z_index`

## Registro de nodos

Los tipos de nodo se registran en `UnifiedRuntime._register_builtin_nodes()` dentro de [`run.py`](../run.py).
