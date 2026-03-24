# Runtime y stdlib de GOS

## Builtins del motor

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

## Utilidades nuevas

- `len(valor)`
- `str(valor)`
- `lower(texto)`
- `upper(texto)`
- `trim(texto)`
- `replace(texto, viejo, nuevo)`
- `clamp(valor, min, max)`
- `round(valor)`
- `floor(valor)`
- `ceil(valor)`
- `abs(valor)`
- `min(...)`
- `max(...)`
- `range(fin)` / `range(inicio, fin)` / `range(inicio, fin, paso)`
- `contains(coleccion, valor)`
- `type_of(valor)`
- `append(lista, valor)`
- `pop(lista, indice?)`
- `keys(diccionario)`
- `values(diccionario)`
- `has_key(diccionario, clave)`
- `duplicate(valor)`

## Recomendacion de uso

- usa `action_*` para gameplay
- usa `str(...)` cuando quieras componer texto sin depender de conversion implicita
- usa listas y diccionarios para estado de UI, inventarios y tablas simples
