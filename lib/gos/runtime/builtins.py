import builtins as py_builtins
import copy
import math
import random

from egas.core.logger import Logger
from egas.core.runtime_services import RuntimeServices
from thirdparty.input_system import InputSystem


class BuiltInFunctions:
    @staticmethod
    def print_gos(*args):
        py_builtins.print(*args)
        return None

    @staticmethod
    def print_console(*args):
        Logger.info("GOS Console", " ".join(str(arg) for arg in args))
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

    @staticmethod
    def len_value(value):
        return len(value)

    @staticmethod
    def str_value(value):
        return str(value)

    @staticmethod
    def lower(value):
        return str(value).lower()

    @staticmethod
    def upper(value):
        return str(value).upper()

    @staticmethod
    def trim(value):
        return str(value).strip()

    @staticmethod
    def replace(value, old, new):
        return str(value).replace(str(old), str(new))

    @staticmethod
    def clamp(value, min_value, max_value):
        return max(min_value, min(value, max_value))

    @staticmethod
    def round_value(value):
        return round(value)

    @staticmethod
    def floor_value(value):
        return math.floor(value)

    @staticmethod
    def ceil_value(value):
        return math.ceil(value)

    @staticmethod
    def abs_value(value):
        return abs(value)

    @staticmethod
    def min_value(*values):
        return min(values)

    @staticmethod
    def max_value(*values):
        return max(values)

    @staticmethod
    def append_value(collection, value):
        collection.append(value)
        return collection

    @staticmethod
    def pop_value(collection, index=None):
        if index is None:
            return collection.pop()
        return collection.pop(int(index))

    @staticmethod
    def keys_value(mapping):
        return list(mapping.keys())

    @staticmethod
    def values_value(mapping):
        return list(mapping.values())

    @staticmethod
    def has_key(mapping, key):
        return key in mapping

    @staticmethod
    def duplicate(value):
        return copy.deepcopy(value)


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
    "len": BuiltInFunctions.len_value,
    "str": BuiltInFunctions.str_value,
    "lower": BuiltInFunctions.lower,
    "upper": BuiltInFunctions.upper,
    "trim": BuiltInFunctions.trim,
    "replace": BuiltInFunctions.replace,
    "clamp": BuiltInFunctions.clamp,
    "round": BuiltInFunctions.round_value,
    "floor": BuiltInFunctions.floor_value,
    "ceil": BuiltInFunctions.ceil_value,
    "abs": BuiltInFunctions.abs_value,
    "min": BuiltInFunctions.min_value,
    "max": BuiltInFunctions.max_value,
    "append": BuiltInFunctions.append_value,
    "pop": BuiltInFunctions.pop_value,
    "keys": BuiltInFunctions.keys_value,
    "values": BuiltInFunctions.values_value,
    "has_key": BuiltInFunctions.has_key,
    "duplicate": BuiltInFunctions.duplicate,
}
