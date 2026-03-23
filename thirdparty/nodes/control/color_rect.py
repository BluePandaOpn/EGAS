from thirdparty.nodes.control.control import Control


class ColorRect(Control):
    """
    Panel simple coloreado para HUD y overlays.
    """

    def __init__(self, name: str = "ColorRect"):
        super().__init__(name)
        self.color = (24, 28, 34)
        self.border_color = (74, 86, 102)
        self.border_width = 0
        self.border_radius = 12

    def draw(self, render_server):
        if not self.visible:
            return

        rect = self.get_rect()
        render_server.draw_rect(rect, self.color, border_radius=int(self.border_radius))

        if int(self.border_width) > 0:
            render_server.draw_rect(
                rect,
                self.border_color,
                width=int(self.border_width),
                border_radius=int(self.border_radius),
            )
