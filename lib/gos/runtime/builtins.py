import builtins as py_builtins
import math
import random

from egas.core.logger import Logger
from egas.core.runtime_services import RuntimeServices
from thirdparty.input_system import InputSystem


class BuiltInFunctions:
    """
    Coleccion de funciones globales expuestas al runtime de GOS.
    """

    @staticmethod
    def print_gos(*args):
        """
        `print()` mantiene un comportamiento simple y directo.
        """
        py_builtins.print(*args)
        return None

    @staticmethod
    def print_console(*args):
        """
        `printc()` envia mensajes formateados a la consola del motor.
        """
        message = " ".join(str(arg) for arg in args)
        Logger.info("GOS Console", message)
        return None

    @staticmethod
    def sin_deg(deg):
        return math.sin(math.radians(deg))

    @staticmethod
    def cos_deg(deg):
        return math.cos(math.radians(deg))

    @staticmethod
    def random_range(min_val, max_val):
        return random.uniform(min_val, max_val)

    @staticmethod
    def key_pressed(key_name):
        return InputSystem.is_key_pressed(str(key_name))

    @staticmethod
    def key_just_pressed(key_name):
        return InputSystem.is_key_just_pressed(str(key_name))

    @staticmethod
    def key_just_released(key_name):
        return InputSystem.is_key_just_released(str(key_name))

    @staticmethod
    def action_pressed(action_name):
        return InputSystem.is_action_pressed(str(action_name))

    @staticmethod
    def action_just_pressed(action_name):
        return InputSystem.is_action_just_pressed(str(action_name))

    @staticmethod
    def action_just_released(action_name):
        return InputSystem.is_action_just_released(str(action_name))

    @staticmethod
    def mouse_pressed(button_index=1):
        return InputSystem.is_mouse_button_pressed(int(button_index))

    @staticmethod
    def mouse_just_pressed(button_index=1):
        return InputSystem.is_mouse_button_just_pressed(int(button_index))

    @staticmethod
    def mouse_just_released(button_index=1):
        return InputSystem.is_mouse_button_just_released(int(button_index))

    @staticmethod
    def mouse_x():
        return InputSystem.get_mouse_pos().x

    @staticmethod
    def mouse_y():
        return InputSystem.get_mouse_pos().y

    @staticmethod
    def load_scene(scene_path):
        return RuntimeServices.load_scene(str(scene_path))

    @staticmethod
    def change_scene(scene_path):
        return RuntimeServices.change_scene(str(scene_path))

    @staticmethod
    def get_root():
        return RuntimeServices.get_root()

    @staticmethod
    def get_node(node_path):
        return RuntimeServices.get_node(str(node_path))


BUILTINS = {
    "print": BuiltInFunctions.print_gos,
    "printc": BuiltInFunctions.print_console,
    "sin": BuiltInFunctions.sin_deg,
    "cos": BuiltInFunctions.cos_deg,
    "rand": BuiltInFunctions.random_range,
    "key_pressed": BuiltInFunctions.key_pressed,
    "key_just_pressed": BuiltInFunctions.key_just_pressed,
    "key_just_released": BuiltInFunctions.key_just_released,
    "action_pressed": BuiltInFunctions.action_pressed,
    "action_just_pressed": BuiltInFunctions.action_just_pressed,
    "action_just_released": BuiltInFunctions.action_just_released,
    "mouse_pressed": BuiltInFunctions.mouse_pressed,
    "mouse_just_pressed": BuiltInFunctions.mouse_just_pressed,
    "mouse_just_released": BuiltInFunctions.mouse_just_released,
    "mouse_x": BuiltInFunctions.mouse_x,
    "mouse_y": BuiltInFunctions.mouse_y,
    "load_scene": BuiltInFunctions.load_scene,
    "change_scene": BuiltInFunctions.change_scene,
    "get_root": BuiltInFunctions.get_root,
    "get_node": BuiltInFunctions.get_node,
}
