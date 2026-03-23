# 🚀 EGAS Engine V2.0 & GOS Scripting Language

**EGAS Engine** es un motor de videojuegos en 2D desarrollado en Python utilizando **Pygame**, orientado a la arquitectura de nodos (similar a Godot). Cuenta con su propio lenguaje de programación integrado: **GOS (Game Object Scripting)**.

Este repositorio contiene el núcleo del motor, el transpilador del lenguaje, la librería estándar de matemáticas e Input/Output, y un Launcher automatizado visual en **PyQt6**.

---

## 🛠️ Características Principales

### 🛸 EGAS Engine (El Motor)
* **Arquitectura de Nodos:** Jerarquías visuales (`Node2D`, `Sprite2D`, `CollisionShape2D`).
* **Físicas AABB Integradas:** Colisiones elásticas y cajas delimitadoras rápidas de calcular.
* **Launcher en PyQt6:** Interfaz gráfica para crear y lanzar proyectos con un solo click.
* **Auto-Geolocalización:** El motor sabe dónde está instalado y auto-configura las rutas de los proyectos creados.

### 📜 GOS Language (El Lenguaje de Scripting)
* **Sintaxis de estilo C/JS:** Control de flujo limpio usando `{}` para bloques.
* **Comentarios Modernos:** Soporta comentarios de una línea `//` y multilínea `/* ... */`.
* **Tipado Dinámico:** Variables dinámicas para prototipado rápido de videojuegos.
* **Librería Estándar Integrada (Stdlib):** * `math.gs`: Métodos como `clamp`, `lerp` y `abs`.
  * `io`: Puentes directos con Python para serializar datos JSON y guardar partidas físicas en disco.
  * `os/env.gs`: Diagnóstico del sistema y lectura de plataforma.


---

## 🚦 Cómo Iniciar

### 1. Clonar el repositorio e instalar dependencias
Asegúrate de tener un entorno virtual activo de Python.

```bash
# Activar entorno virtual de Python (.venv)
python -m venv .venv

# Instalar librerías del motor y del Launcher GUI
python -m pip install -r requirements.txt
```

### 2. Abrir el Launcher de Proyectos
Ejecuta el launcher para crear un nuevo proyecto de videojuego automatizado:

```bash
python run.py
```

### 3. Escribir Scripts GOS
Puedes controlar el comportamiento de cualquier nodo del juego creando un archivo de extensión `.gs`. He aquí un ejemplo:

```javascript
/* ship_controller.gs
   Mueve la nave espacial en el eje X
*/

var speed = 300.0

func update_ship(delta) {
    if (is_key_pressed("right")) {
        self.position.x = self.position.x + (speed * delta)
    }
    if (is_key_pressed("left")) {
        self.position.x = self.position.x - (speed * delta)
    }
}
```
