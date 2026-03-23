// Declaramos variables básicas
var vida = 100
var dano_enemigo = 25
var defensa = 5

// El Parser resolverá la matemática priorizando la multiplicación (*) antes que la resta (-)
var dano_final = dano_enemigo - defensa * 2

vida = vida - dano_final

print("Vida restante del personaje:")
print(vida) // Debería dar 85 (100 - (25 - 10))