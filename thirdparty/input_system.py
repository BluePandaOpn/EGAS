import pygame
from typing import List
from config.settings import Settings
from egas.core.logger import Logger
from thirdparty.math2d import Vector2

# --- 🛰️ NUEVAS CLASES DE EVENTOS ENRIQUECIDOS ---

class InputEvent:
    """Clase base para todos los eventos del motor EGAS."""
    pass

class InputEventKey(InputEvent):
    """Eventos de teclado físicos."""
    def __init__(self, key_name: str, pressed: bool):
        self.key_name = key_name
        self.pressed = pressed  # True = Presionada, False = Soltada

class InputEventMouseButton(InputEvent):
    """Eventos de clics del mouse."""
    def __init__(self, button_index: int, pos_x: float, pos_y: float, pressed: bool):
        self.button_index = button_index  # 1: Izq, 2: Medio, 3: Der, 4: Rueda Arriba, 5: Rueda Abajo
        self.position_x = pos_x
        self.position_y = pos_y
        self.pressed = pressed

class InputEventMouseMotion(InputEvent):
    """Eventos de movimiento de cursor del mouse."""
    def __init__(self, pos_x: float, pos_y: float, rel_x: float, rel_y: float):
        self.position_x = pos_x
        self.position_y = pos_y
        self.relative_x = rel_x  # Cuánto se movió desde el frame anterior
        self.relative_y = rel_y


class InputSystem:
    """
    Gestor de periféricos de entrada (Teclado/Mouse).
    Traduce Scancodes de Pygame a las acciones semánticas del motor.
    Ahora genera eventos individuales para el ciclo de vida de los Nodos.
    """
    _pressed_keys = set()
    _just_pressed_keys = set()
    _just_released_keys = set()

    @classmethod
    def update(cls) -> List[InputEvent]:
        """
        Limpia estados antiguos, lee eventos de Pygame y devuelve una lista de 
        objetos de evento listos para que el motor se los envíe a los scripts de GOS.
        """
        cls._just_pressed_keys.clear()
        cls._just_released_keys.clear()
        
        eventos_despachados: List[InputEvent] = []

        for event in pygame.event.get():
            # --- ⌨️ 1. TECLADO ---
            if event.type == pygame.KEYDOWN:
                key_name = pygame.key.name(event.key)
                cls._pressed_keys.add(key_name)
                cls._just_pressed_keys.add(key_name)
                eventos_despachados.append(InputEventKey(key_name, pressed=True))

            elif event.type == pygame.KEYUP:
                key_name = pygame.key.name(event.key)
                if key_name in cls._pressed_keys:
                    cls._pressed_keys.remove(key_name)
                cls._just_released_keys.add(key_name)
                eventos_despachados.append(InputEventKey(key_name, pressed=False))

            # --- 🖱️ 2. MOUSE CLICS ---
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                eventos_despachados.append(InputEventMouseButton(event.button, mx, my, pressed=True))

            elif event.type == pygame.MOUSEBUTTONUP:
                mx, my = event.pos
                eventos_despachados.append(InputEventMouseButton(event.button, mx, my, pressed=False))

            # --- 🏹 3. MOUSE MOVIMIENTO ---
            elif event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
                rx, ry = event.rel
                eventos_despachados.append(InputEventMouseMotion(mx, my, rx, ry))

            # --- 🚪 4. SISTEMA ---
            elif event.type == pygame.QUIT:
                Logger.system("Evento de cierre de ventana detectado.")
                # Se envía un evento genérico None para indicarle al loop que cierre la app
                return [] 

        return eventos_despachados

    # --- 🔍 MÉTODOS TRADICIONALES DE BÚSQUEDA (Se mantienen intactos) ---

    @classmethod
    def is_action_pressed(cls, action_name: str) -> bool:
        keys = Settings.INPUT_MAP.get(action_name, [])
        for k in keys:
            if k in cls._pressed_keys:
                return True
        return False

    @classmethod
    def is_action_just_pressed(cls, action_name: str) -> bool:
        keys = Settings.INPUT_MAP.get(action_name, [])
        for k in keys:
            if k in cls._just_pressed_keys:
                return True
        return False

    @classmethod
    def is_action_just_released(cls, action_name: str) -> bool:
        keys = Settings.INPUT_MAP.get(action_name, [])
        for k in keys:
            if k in cls._just_released_keys:
                return True
        return False

    @classmethod
    def get_mouse_pos(cls) -> Vector2:
        mx, my = pygame.mouse.get_pos()
        return Vector2(mx, my)