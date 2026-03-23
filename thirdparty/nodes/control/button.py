import pygame
from thirdparty.nodes.control.control import Control
from thirdparty.nodes.control.label import Label
from egas.core.logger import Logger

class Button(Control):
    """
    Nodo de UI interactivo que detecta clics de mouse y cambia de estado visual.
    """
    def __init__(self, name: str = "Button"):
        super().__init__(name)
        
        # Colores de estado
        self.normal_color = (70, 70, 70)
        self.hover_color = (100, 100, 100)
        self.pressed_color = (40, 40, 40)
        
        self.current_color = self.normal_color
        self.is_pressed: bool = False

        # Texto del botón interno
        self.label = Label("Label_Interno")
        self.label.set_text("Hacer Clic")
        self.add_child(self.label)

    def _custom_process(self, delta: float):
        from thirdparty.input_system import InputSystem
        
        # Lógica de detección de Mouse Hover y Clic
        if self.is_mouse_over():
            if pygame.mouse.get_pressed()[0]: # Botón izquierdo clickeado
                self.current_color = self.pressed_color
                if not self.is_pressed:
                    self.is_pressed = True
                    self.on_click()
            else:
                self.current_color = self.hover_color
                self.is_pressed = False
        else:
            self.current_color = self.normal_color
            self.is_pressed = False

        # Centrar el texto interno automáticamente
        self.label.position.x = (self.size.x / 2) - (self.label.size.x / 2)
        self.label.position.y = (self.size.y / 2) - (self.label.size.y / 2)

    def draw(self, render_server):
        if not self.visible:
            return

        # Dibujar el fondo del botón (Rectángulo coloreado)
        pos = self.get_global_position()
        
        # Generar superficie plana del botón al vuelo
        surf = pygame.Surface((int(self.size.x), int(self.size.y)))
        surf.fill(self.current_color)
        
        from egas.render.texture import PygameTexture
        btn_bg_texture = PygameTexture(surf, f"button_bg_{self.get_name()}")

        # Dibujar Fondo
        render_server.draw_texture(
            texture=btn_bg_texture,
            position=(pos.x + self.size.x/2, pos.y + self.size.y/2),
            scale=(1.0, 1.0),
            rotation=0.0
        )
        
        # Dibujar el Label hijo (Se dibuja automáticamente por el SceneTree gracias al árbol de herencia!)

    def on_click(self):
        """Función que se gatilla al apretar el botón. Sobrescribir o invocar desde GOS."""
        Logger.info("UI_Event", f"¡El botón '{self.get_name()}' fue presionado!")