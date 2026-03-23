# Escenas `.dscn`

## Formato actual

Las escenas usan un formato de secciones tipo INI:

```ini
[Nivel]
type = Node2D

[Jugador]
type = Sprite2D
parent = Nivel
position_x = 200
position_y = 120
texture = res://assets/player.png
script = res://scripts/player.gs
```

## Claves soportadas

- `type`: clase del nodo registrada en el runtime
- `parent`: nombre del padre o ruta jerarquica
- `instance`: instancia otra escena
- `script`: script GOS asociado
- `position_x`, `position_y`
- `scale_x`, `scale_y`
- `rotation`
- `size_x`, `size_y`
- cualquier otra propiedad publica del nodo

## Referencias a otros nodos

Si una propiedad termina en `_node`, el parser intenta resolverla como referencia a otro nodo de la escena.

Ejemplo:

```ini
[Juego]
type = SnakeGame2D
score_label_node = LabelPuntos
```

## Jerarquia

Ahora `parent` puede usarse con rutas:

```ini
parent = Root/UI/HUD
```

## Instanciacion de subescenas

```ini
[Jugador]
instance = res://scenes/jugador.dscn
parent = Nivel
```

## Buenas practicas

- usa un nodo raiz claro por escena
- separa mundo y UI con `CanvasLayer`
- deja scripts en `scripts/`
- deja assets en `assets/`
- usa nombres de nodo estables si vas a referenciarlos desde `_node`
