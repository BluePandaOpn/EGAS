var energia = 30
var costo_disparo = 50

if (energia >= costo_disparo) {
    print("¡Fuego! Disparando láser.")
    energia = energia - costo_disparo
} else {
    print("Sin energía suficiente. Por favor, recargue.")
}