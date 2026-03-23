import pygame
from typing import List

from config.settings import Settings
from egas.core.logger import Logger
from thirdparty.math2d import Vector2


class InputEvent:
    """Clase base para todos los eventos del motor EGAS."""

    pass


class InputEventKey(InputEvent):
    """Evento de teclado."""

    def __init__(self, key_name: str, pressed: bool):
        self.key_name = key_name
        self.pressed = pressed


class InputEventMouseButton(InputEvent):
    """Evento de boton del raton."""

    def __init__(self, button_index: int, pos_x: float, pos_y: float, pressed: bool):
        self.button_index = button_index
        self.position_x = pos_x
        self.position_y = pos_y
        self.pressed = pressed


class InputEventMouseMotion(InputEvent):
    """Evento de movimiento del cursor."""

    def __init__(self, pos_x: float, pos_y: float, rel_x: float, rel_y: float):
        self.position_x = pos_x
        self.position_y = pos_y
        self.relative_x = rel_x
        self.relative_y = rel_y


class InputEventWindowClose(InputEvent):
    """Evento emitido cuando el usuario solicita cerrar la ventana."""

    pass


class InputSystem:
    """
    Gestor de entrada de teclado y raton.
    """

    _pressed_keys = set()
    _just_pressed_keys = set()
    _just_released_keys = set()
    _pressed_mouse_buttons = set()
    _just_pressed_mouse_buttons = set()
    _just_released_mouse_buttons = set()

    @classmethod
    def update(cls) -> List[InputEvent]:
        cls._just_pressed_keys.clear()
        cls._just_released_keys.clear()
        cls._just_pressed_mouse_buttons.clear()
        cls._just_released_mouse_buttons.clear()

        eventos_despachados: List[InputEvent] = []

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                key_name = pygame.key.name(event.key)
                cls._pressed_keys.add(key_name)
                cls._just_pressed_keys.add(key_name)
                eventos_despachados.append(InputEventKey(key_name, pressed=True))

            elif event.type == pygame.KEYUP:
                key_name = pygame.key.name(event.key)
                cls._pressed_keys.discard(key_name)
                cls._just_released_keys.add(key_name)
                eventos_despachados.append(InputEventKey(key_name, pressed=False))

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                cls._pressed_mouse_buttons.add(event.button)
                cls._just_pressed_mouse_buttons.add(event.button)
                eventos_despachados.append(
                    InputEventMouseButton(event.button, mx, my, pressed=True)
                )

            elif event.type == pygame.MOUSEBUTTONUP:
                mx, my = event.pos
                cls._pressed_mouse_buttons.discard(event.button)
                cls._just_released_mouse_buttons.add(event.button)
                eventos_despachados.append(
                    InputEventMouseButton(event.button, mx, my, pressed=False)
                )

            elif event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
                rx, ry = event.rel
                eventos_despachados.append(InputEventMouseMotion(mx, my, rx, ry))

            elif event.type == pygame.QUIT:
                Logger.system(
                    "Evento de cierre de ventana detectado. Se iniciara el apagado del motor."
                )
                eventos_despachados.append(InputEventWindowClose())

        return eventos_despachados

    @classmethod
    def is_key_pressed(cls, key_name: str) -> bool:
        return key_name in cls._pressed_keys

    @classmethod
    def is_key_just_pressed(cls, key_name: str) -> bool:
        return key_name in cls._just_pressed_keys

    @classmethod
    def is_key_just_released(cls, key_name: str) -> bool:
        return key_name in cls._just_released_keys

    @classmethod
    def is_action_pressed(cls, action_name: str) -> bool:
        keys = Settings.INPUT_MAP.get(action_name, [])
        return any(key in cls._pressed_keys for key in keys)

    @classmethod
    def is_action_just_pressed(cls, action_name: str) -> bool:
        keys = Settings.INPUT_MAP.get(action_name, [])
        return any(key in cls._just_pressed_keys for key in keys)

    @classmethod
    def is_action_just_released(cls, action_name: str) -> bool:
        keys = Settings.INPUT_MAP.get(action_name, [])
        return any(key in cls._just_released_keys for key in keys)

    @classmethod
    def is_mouse_button_pressed(cls, button_index: int) -> bool:
        return button_index in cls._pressed_mouse_buttons

    @classmethod
    def is_mouse_button_just_pressed(cls, button_index: int) -> bool:
        return button_index in cls._just_pressed_mouse_buttons

    @classmethod
    def is_mouse_button_just_released(cls, button_index: int) -> bool:
        return button_index in cls._just_released_mouse_buttons

    @classmethod
    def get_mouse_pos(cls) -> Vector2:
        mx, my = pygame.mouse.get_pos()
        return Vector2(mx, my)
