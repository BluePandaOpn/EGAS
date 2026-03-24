from typing import List

import pygame

from config.settings import Settings
from egas.core.logger import Logger
from thirdparty.math2d import Vector2


class InputEvent:
    pass


class InputEventKey(InputEvent):
    def __init__(self, key_name: str, pressed: bool):
        self.key_name = key_name
        self.pressed = pressed
        self.action_names = InputSystem.get_actions_for_key(key_name)


class InputEventMouseButton(InputEvent):
    def __init__(self, button_index: int, pos_x: float, pos_y: float, pressed: bool):
        self.button_index = button_index
        self.position_x = pos_x
        self.position_y = pos_y
        self.pressed = pressed


class InputEventMouseMotion(InputEvent):
    def __init__(self, pos_x: float, pos_y: float, rel_x: float, rel_y: float):
        self.position_x = pos_x
        self.position_y = pos_y
        self.relative_x = rel_x
        self.relative_y = rel_y


class InputEventWindowClose(InputEvent):
    pass


class InputSystem:
    _pressed_keys = set()
    _just_pressed_keys = set()
    _just_released_keys = set()
    _pressed_mouse_buttons = set()
    _just_pressed_mouse_buttons = set()
    _just_released_mouse_buttons = set()
    _last_frame_events: List[InputEvent] = []

    @classmethod
    def update(cls) -> List[InputEvent]:
        cls._just_pressed_keys.clear()
        cls._just_released_keys.clear()
        cls._just_pressed_mouse_buttons.clear()
        cls._just_released_mouse_buttons.clear()

        dispatched_events: List[InputEvent] = []

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                key_name = cls.normalize_key_name(pygame.key.name(event.key))
                cls._pressed_keys.add(key_name)
                cls._just_pressed_keys.add(key_name)
                dispatched_events.append(InputEventKey(key_name, pressed=True))
            elif event.type == pygame.KEYUP:
                key_name = cls.normalize_key_name(pygame.key.name(event.key))
                cls._pressed_keys.discard(key_name)
                cls._just_released_keys.add(key_name)
                dispatched_events.append(InputEventKey(key_name, pressed=False))
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                cls._pressed_mouse_buttons.add(event.button)
                cls._just_pressed_mouse_buttons.add(event.button)
                dispatched_events.append(InputEventMouseButton(event.button, mx, my, pressed=True))
            elif event.type == pygame.MOUSEBUTTONUP:
                mx, my = event.pos
                cls._pressed_mouse_buttons.discard(event.button)
                cls._just_released_mouse_buttons.add(event.button)
                dispatched_events.append(InputEventMouseButton(event.button, mx, my, pressed=False))
            elif event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
                rx, ry = event.rel
                dispatched_events.append(InputEventMouseMotion(mx, my, rx, ry))
            elif event.type == pygame.QUIT:
                Logger.system("Evento de cierre de ventana detectado.")
                dispatched_events.append(InputEventWindowClose())

        cls._last_frame_events = dispatched_events
        if Settings.DEBUG_INPUT:
            cls._trace_events(dispatched_events)
        return dispatched_events

    @classmethod
    def normalize_key_name(cls, key_name: str) -> str:
        return Settings.normalize_key_name(key_name)

    @classmethod
    def get_actions_for_key(cls, key_name: str) -> List[str]:
        normalized = cls.normalize_key_name(key_name)
        return [action for action, keys in Settings.INPUT_MAP.items() if normalized in keys]

    @classmethod
    def is_key_pressed(cls, key_name: str) -> bool:
        return cls.normalize_key_name(key_name) in cls._pressed_keys

    @classmethod
    def is_key_just_pressed(cls, key_name: str) -> bool:
        return cls.normalize_key_name(key_name) in cls._just_pressed_keys

    @classmethod
    def is_key_just_released(cls, key_name: str) -> bool:
        return cls.normalize_key_name(key_name) in cls._just_released_keys

    @classmethod
    def is_action_pressed(cls, action_name: str) -> bool:
        keys = Settings.INPUT_MAP.get(action_name, [])
        return any(cls.normalize_key_name(key) in cls._pressed_keys for key in keys)

    @classmethod
    def is_action_just_pressed(cls, action_name: str) -> bool:
        keys = Settings.INPUT_MAP.get(action_name, [])
        return any(cls.normalize_key_name(key) in cls._just_pressed_keys for key in keys)

    @classmethod
    def is_action_just_released(cls, action_name: str) -> bool:
        keys = Settings.INPUT_MAP.get(action_name, [])
        return any(cls.normalize_key_name(key) in cls._just_released_keys for key in keys)

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

    @classmethod
    def get_last_frame_events(cls) -> List[InputEvent]:
        return list(cls._last_frame_events)

    @classmethod
    def _trace_events(cls, events: List[InputEvent]):
        if not events:
            return
        descriptions = []
        for event in events:
            if isinstance(event, InputEventKey):
                descriptions.append(
                    f"key={event.key_name} pressed={event.pressed} actions={','.join(event.action_names) or '-'}"
                )
            elif isinstance(event, InputEventMouseButton):
                descriptions.append(
                    f"mouse_button={event.button_index} pressed={event.pressed} pos=({event.position_x},{event.position_y})"
                )
            elif isinstance(event, InputEventMouseMotion):
                descriptions.append(f"mouse_motion=({event.position_x},{event.position_y}) rel=({event.relative_x},{event.relative_y})")
            elif isinstance(event, InputEventWindowClose):
                descriptions.append("window_close")
        Logger.debug("Input", " | ".join(descriptions))
