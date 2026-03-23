import pygame
from config.settings import Settings
from egas.core.logger import Logger

class InputSystem:
    """
    Gestor de periféricos de entrada (Teclado/Mouse).
    Traduce Scancodes de Pygame a las acciones semánticas del motor (ej: ui_left).
    """
    _pressed_keys = set()
    _just_pressed_keys = set()
    _just_released_keys = set()

    @classmethod
    def update(cls):
        """
        Limpia los estados de 'un solo frame' (just_pressed / just_released).
        Se debe llamar al inicio de cada frame en el Engine principal.
        """
        cls._just_pressed_keys.clear()
        cls._just_released_keys.clear()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                key_name = pygame.key.name(event.key)
                cls._pressed_keys.add(key_name)
                cls._just_pressed_keys.add(key_name)

            elif event.type == pygame.KEYUP:
                key_name = pygame.key.name(event.key)
                if key_name in cls._pressed_keys:
                    cls._pressed_keys.remove(key_name)
                cls._just_released_keys.add(key_name)

            elif event.type == pygame.QUIT:
                Logger.system("Evento de cierre de ventana detectado.")
                return False # Señal para apagar el motor

        return True

    @classmethod
    def is_action_pressed(cls, action_name: str) -> bool:
        """Retorna True si la acción se mantiene presionada."""
        keys = Settings.INPUT_MAP.get(action_name, [])
        for k in keys:
            if k in cls._pressed_keys:
                return True
        return False

    @classmethod
    def is_action_just_pressed(cls, action_name: str) -> bool:
        """Retorna True solo en el frame exacto en que se presionó la tecla."""
        keys = Settings.INPUT_MAP.get(action_name, [])
        for k in keys:
            if k in cls._just_pressed_keys:
                return True
        return False

    @classmethod
    def is_action_just_released(cls, action_name: str) -> bool:
        """Retorna True solo en el frame exacto en que se soltó la tecla."""
        keys = Settings.INPUT_MAP.get(action_name, [])
        for k in keys:
            if k in cls._just_released_keys:
                return True
        return False

    @classmethod
    def get_mouse_pos(cls) -> Vector2:
        """Retorna la posición del mouse en coordenadas de pantalla."""
        from thirdparty.math2d import Vector2
        mx, my = pygame.mouse.get_pos()
        return Vector2(mx, my)