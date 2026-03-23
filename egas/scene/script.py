from lib.gos.lexer.lexer import Lexer
from lib.gos.parser.parser import Parser
from lib.gos.runtime.interpreter import Interpreter
from egas.core.logger import Logger

class ScriptBridge:
    """
    Puente de enlace entre los Nodos de EGAS y el Intérprete del Lenguaje GOS.
    """
    def __init__(self, owner_node):
        self.owner_node = owner_node
        self.interpreter = Interpreter()
        self.is_compiled = False

    def attach_script(self, script_path: str):
        """
        Lee el archivo de texto .gs y lo procesa a través del Lexer y Parser de GOS.
        """
        try:
            # En GOS, res:// se traduce a la ruta real de tu proyecto
            clean_path = script_path.replace("res://", "")
            
            with open(clean_path, 'r', encoding='utf-8') as f:
                code = f.read()

            # --- LLAMADA A TU LENGUAJE GOS NATIVO ---
            lexer = Lexer(code)
            tokens = lexer.tokenize()

            parser = Parser(tokens)
            self.ast = parser.parse()

            # Vinculamos el nodo actual al entorno de variables del Runtime de GOS
            self.interpreter.environment.define("self", self.owner_node)
            
            self.is_compiled = True
            Logger.success("ScriptBridge", f"Script '{script_path}' compilado con GOS para '{self.owner_node.get_name()}'")

        except Exception as e:
            Logger.error("ScriptBridge", f"Error compilando script {script_path} en GOS: {e}")

    def execute_tick(self, delta: float):
        """Ejecuta la lógica del script por frame (si GOS tiene un bucle _process)."""
        if not self.is_compiled:
            return

        # Le pasamos el Delta Time a GOS
        self.interpreter.environment.define("delta", delta)
        self.interpreter.run(self.ast)