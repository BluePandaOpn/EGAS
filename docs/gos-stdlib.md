# Runtime y stdlib de GOS

## Builtins del motor

Estas funciones se cargan desde [`lib/gos/runtime/builtins.py`](../lib/gos/runtime/builtins.py):

- `print(...)`
- `printc(...)`
- `sin(grados)`
- `cos(grados)`
- `rand(min, max)`
- `key_pressed(nombre)`
- `key_just_pressed(nombre)`
- `key_just_released(nombre)`
- `action_pressed(nombre)`
- `action_just_pressed(nombre)`
- `action_just_released(nombre)`
- `mouse_pressed(boton)`
- `mouse_just_pressed(boton)`
- `mouse_just_released(boton)`
- `mouse_x()`
- `mouse_y()`
- `load_scene(path)`
- `change_scene(path)`
- `get_root()`
- `get_node(path)`

## Libreria estandar incluida

Codigo en:

- [`lib/gos/stdlib/math/`](../lib/gos/stdlib/math)
- [`lib/gos/stdlib/io/`](../lib/gos/stdlib/io)
- [`lib/gos/stdlib/os/`](../lib/gos/stdlib/os)

## Material de apoyo ya incluido

El proyecto ya trae documentos `.gs` de ayuda en:

- [`lib/gos/docs/bucles.gs`](../lib/gos/docs/bucles.gs)
- [`lib/gos/docs/declarar_variables.gs`](../lib/gos/docs/declarar_variables.gs)
- [`lib/gos/docs/estructura_de_condicionales.gs`](../lib/gos/docs/estructura_de_condicionales.gs)
- [`lib/gos/docs/funciones_natibas_del_motor.gs`](../lib/gos/docs/funciones_natibas_del_motor.gs)
- [`lib/gos/docs/funciones_y_retornos.gs`](../lib/gos/docs/funciones_y_retornos.gs)

## Recomendacion

Para aprender GOS en orden:

1. `declarar_variables.gs`
2. `estructura_de_condicionales.gs`
3. `bucles.gs`
4. `funciones_y_retornos.gs`
5. `funciones_natibas_del_motor.gs`
