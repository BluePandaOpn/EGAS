# Empezar con EGAS

## Que es EGAS

EGAS es un motor 2D orientado a escenas y nodos. Usa:

- Python como base del runtime.
- Pygame para ventana, render e input.
- GOS como lenguaje de scripting.
- Archivos `.dscn` para escenas.

## Primer arranque

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python run.py
```

Para lanzar un proyecto sin abrir el launcher:

```bash
python run.py --project example/snake --play
```

## Estructura de un proyecto EGAS

```text
proyecto.egas
.egas/
.gos/
assets/
build/
scenes/
scripts/
```

## Flujo basico de trabajo

1. Crear o abrir un proyecto.
2. Definir una escena `.dscn` en `scenes/`.
3. Crear scripts `.gs` en `scripts/`.
4. Asignar `script = res://scripts/archivo.gs` a un nodo de la escena.
5. Ejecutar el proyecto con `run.py`.

## Donde mirar codigo

- Runtime general: [`run.py`](../run.py)
- Engine principal: [`egas/core/engine.py`](../egas/core/engine.py)
- Carga de escenas: [`egas/scene/parser.py`](../egas/scene/parser.py)
- Arbol activo: [`egas/scene/tree.py`](../egas/scene/tree.py)
- Intreprete GOS: [`lib/gos/runtime/interpreter.py`](../lib/gos/runtime/interpreter.py)
- Ejemplo de referencia: [`example/snake/`](../example/snake)
