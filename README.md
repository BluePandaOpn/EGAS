# EGAS Engine

EGAS es un motor 2D en Python sobre Pygame con arquitectura de nodos y un lenguaje de scripting propio llamado GOS.

Este `README.md` solo cubre la informacion basica del motor. La documentacion detallada vive en [`docs/`](docs/README.md).

## Que incluye

- Motor 2D con `SceneTree`, nodos, render y fisicas basicas.
- Lenguaje GOS para scripts de gameplay.
- Loader de escenas `.dscn`.
- Launcher de proyectos con PyQt6.
- Ejemplos de proyecto en [`example/`](example).

## Requisitos

- Python 3.13 o compatible con el proyecto.
- Dependencias de [`requirements.txt`](requirements.txt).
- Entorno virtual recomendado.

## Instalacion

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

## Ejecucion

Para abrir el launcher:

```bash
python run.py
```

Para ejecutar un proyecto concreto:

```bash
python run.py --project example/snake --play
```

## Estructura minima

```text
config/       Configuracion global del motor
docs/         Documentacion del motor y del lenguaje
egas/         Nucleo del motor
example/      Proyectos de ejemplo
lib/gos/      Lexer, parser, runtime y stdlib de GOS
thirdparty/   Nodos y utilidades del runtime
run.py        Launcher y runtime unificado
```

## Documentacion

Empieza por aqui:

- [`docs/README.md`](docs/README.md): indice general.
- [`docs/getting-started.md`](docs/getting-started.md): primer arranque.
- [`docs/engine.md`](docs/engine.md): arquitectura del motor.
- [`docs/scenes.md`](docs/scenes.md): formato `.dscn`.
- [`docs/nodes.md`](docs/nodes.md): nodos disponibles.
- [`docs/gos-language.md`](docs/gos-language.md): lenguaje GOS.
- [`docs/gos-stdlib.md`](docs/gos-stdlib.md): funciones globales y stdlib.
- [`docs/index.txt`](docs/index.txt): mapa rapido de rutas locales y rutas raw.

## Estado actual

EGAS ya puede cargar escenas, instanciar nodos, ejecutar scripts GOS y renderizar proyectos 2D simples. Todavia hay partes en desarrollo, asi que la documentacion intenta separar con claridad lo que ya existe de lo que aun esta verde.
