from pathlib import Path

from egas.core.logger import Logger
from lib.gos.lexer.lexer import Lexer
from lib.gos.parser.parser import Parser
from lib.gos.runtime.interpreter import Interpreter


class ScriptBridge:
    """
    Puente de enlace entre los nodos de EGAS y el runtime de GOS.
    """

    def __init__(self, owner_node):
        self.owner_node = owner_node
        self.interpreter = Interpreter()
        self.is_compiled = False
        self.ast = []
        self.script_path = None
        self.virtual_script_path = None

    def attach_script(self, script_path: str):
        """
        Lee un script .gs, lo parsea, registra sus funciones globales y lo deja listo.
        """
        try:
            clean_path = script_path.replace("res://", "")
            absolute_path = Path(clean_path).resolve()

            with absolute_path.open("r", encoding="utf-8") as file_handle:
                code = file_handle.read()

            lexer = Lexer(code)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            self.ast = parser.parse()

            self.interpreter = Interpreter()
            self.interpreter.environment.define("self", self.owner_node)
            self.interpreter.run(self.ast)

            self.script_path = str(absolute_path)
            self.virtual_script_path = script_path
            self.is_compiled = True
            Logger.success("ScriptBridge", f"Script '{script_path}' compilado para '{self.owner_node.get_name()}'")
        except Exception as exc:
            self.is_compiled = False
            Logger.error("ScriptBridge", f"Error compilando script {script_path}: {exc}")

    def call(self, func_name: str, *args):
        if not self.is_compiled:
            return None
        return self.interpreter.call_function(func_name, list(args))

    def execute_ready(self):
        self.call("_ready")

    def execute_tick(self, delta: float):
        if not self.is_compiled:
            return
        self.interpreter.environment.define("delta", delta)
        self.call("_process", delta)
