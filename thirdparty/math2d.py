import math
from typing import Union, Tuple

class Vector2:
    """
    Clase matemática para representar vectores y posiciones en un plano 2D.
    Inspirado en los vectores de Godot y Unity.
    """
    def __init__(self, x: float = 0.0, y: float = 0.0):
        self.x = float(x)
        self.y = float(y)

    # --- Operaciones Aritméticas Básicas ---
    def __add__(self, other: 'Vector2') -> 'Vector2':
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: 'Vector2') -> 'Vector2':
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: Union[float, int]) -> 'Vector2':
        return Vector2(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar: Union[float, int]) -> 'Vector2':
        if scalar == 0:
            raise ZeroDivisionError("No se puede dividir un Vector2 por cero.")
        return Vector2(self.x / scalar, self.y / scalar)

    # --- Funciones Geométricas ---
    def length(self) -> float:
        """Calcula la magnitud/longitud del vector."""
        return math.hypot(self.x, self.y)

    def normalized(self) -> 'Vector2':
        """Devuelve un vector con longitud 1 manteniendo la dirección."""
        l = self.length()
        if l == 0:
            return Vector2(0.0, 0.0)
        return self / l

    def distance_to(self, other: 'Vector2') -> float:
        """Calcula la distancia flotante hacia otro Vector2."""
        return math.hypot(self.x - other.x, self.y - other.y)

    def angle_to(self, other: 'Vector2') -> float:
        """Calcula el ángulo en radianes entre este vector y otro."""
        return math.atan2(other.y - self.y, other.x - self.x)

    # --- Utilidades de conversión ---
    def to_tuple(self) -> Tuple[float, float]:
        return (self.x, self.y)

    def __str__(self) -> str:
        return f"Vector2({self.x:.2f}, {self.y:.2f})"

    # Constantes útiles
    @staticmethod
    def ZERO(): return Vector2(0, 0)
    @staticmethod
    def UP(): return Vector2(0, -1)
    @staticmethod
    def DOWN(): return Vector2(0, 1)
    @staticmethod
    def LEFT(): return Vector2(-1, 0)
    @staticmethod
    def RIGHT(): return Vector2(1, 0)