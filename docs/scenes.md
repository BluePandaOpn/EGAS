# Escenas `.dscn`

## Formato actual

Las escenas usan un formato tipo INI:

```ini
[Nivel]
type = "Node2D"

[Jugador]
type = "Sprite2D"
parent = "Nivel"
position_x = 200
position_y = 120
texture = "res://assets/player.png"
script = "res://scripts/player.gs"
```

## Tipos de valor

- numeros: `10`, `3.5`
- booleanos: `true`, `false`
- listas: `[1, 2, 3]`
- strings: `"texto"`
- referencias a nodo: `hud_label_node = "HUD/LabelPuntos"`

El parser todavia acepta strings sin comillas por compatibilidad, pero ahora muestra warning. La recomendacion es usar comillas siempre.

## Claves soportadas

- `type`
- `parent`
- `instance`
- `script`
- `position_x`, `position_y`
- `scale_x`, `scale_y`
- `rotation`
- `size_x`, `size_y`
- otras propiedades publicas del nodo

## Validacion

El parser intenta advertir:

- tipo de nodo desconocido
- referencia `_node` no resuelta
- listas invalidas
- propiedades desconocidas
- strings sin comillas

Los warnings incluyen seccion, clave y linea aproximada cuando es posible.

## Referencias a nodos

Si una propiedad termina en `_node`, el parser intenta resolverla antes de `_ready()`.

```ini
[Juego]
type = "SnakeGame2D"
score_label_node = "UI/LabelPuntos"
```

## Jerarquia

`parent` puede usarse con rutas:

```ini
parent = "Root/UI/HUD"
```

## Instanciacion de subescenas

```ini
[Jugador]
instance = "res://scenes/jugador.dscn"
parent = "Nivel"
```
