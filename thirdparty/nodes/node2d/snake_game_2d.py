import random

from egas.core.logger import Logger
from thirdparty.input_system import InputSystem
from thirdparty.nodes.node2d.node2d import Node2D


class SnakeGame2D(Node2D):
    """
    Minijuego Snake listo para usarse como nodo de escena.
    """

    def __init__(self, name: str = "SnakeGame2D"):
        super().__init__(name)
        self.cell_size = 28.0
        self.cols = 28
        self.rows = 18
        self.tick_time = 0.12
        self.board_color = (17, 21, 26)
        self.grid_color = (28, 35, 43)
        self.border_color = (76, 91, 110)
        self.snake_color = (87, 214, 118)
        self.head_color = (187, 255, 143)
        self.apple_color = (255, 96, 96)
        self.apple_stem_color = (84, 189, 87)
        self.score = 0
        self.best_score = 0
        self.score_label_node = None
        self.apple_label_node = None
        self.status_label_node = None
        self._elapsed = 0.0
        self._direction = (1, 0)
        self._queued_direction = (1, 0)
        self._snake = []
        self._apple = (0, 0)
        self._rng = random.Random()

    def ready(self):
        self._reset_round("Pulsa WASD o flechas para empezar.")

    def _custom_process(self, delta: float):
        self._read_input()
        self._elapsed += delta

        if self._elapsed < self.tick_time:
            return

        self._elapsed = 0.0
        self._step()

    def draw(self, render_server):
        pos = self.get_global_position()
        board_x = pos.x
        board_y = pos.y
        board_w = self.cols * self.cell_size
        board_h = self.rows * self.cell_size

        render_server.draw_rect((board_x, board_y, board_w, board_h), self.board_color, border_radius=16)
        render_server.draw_rect((board_x, board_y, board_w, board_h), self.border_color, width=3, border_radius=16)

        for col in range(1, self.cols):
            x = board_x + (col * self.cell_size)
            render_server.draw_rect((x, board_y, 1, board_h), self.grid_color)

        for row in range(1, self.rows):
            y = board_y + (row * self.cell_size)
            render_server.draw_rect((board_x, y, board_w, 1), self.grid_color)

        apple_x, apple_y = self._cell_origin(*self._apple)
        render_server.draw_circle(
            self.apple_color,
            (apple_x + (self.cell_size / 2), apple_y + (self.cell_size / 2)),
            self.cell_size * 0.34,
        )
        render_server.draw_rect(
            (
                apple_x + (self.cell_size * 0.48),
                apple_y + (self.cell_size * 0.16),
                self.cell_size * 0.08,
                self.cell_size * 0.22,
            ),
            self.apple_stem_color,
            border_radius=3,
        )

        for index, segment in enumerate(self._snake):
            seg_x, seg_y = self._cell_origin(*segment)
            color = self.head_color if index == 0 else self.snake_color
            inset = 4 if index == 0 else 5
            render_server.draw_rect(
                (
                    seg_x + inset,
                    seg_y + inset,
                    self.cell_size - (inset * 2),
                    self.cell_size - (inset * 2),
                ),
                color,
                border_radius=8,
            )

    def _read_input(self):
        if InputSystem.is_key_just_pressed("w") or InputSystem.is_key_just_pressed("up"):
            self._queue_direction((0, -1))
        if InputSystem.is_key_just_pressed("s") or InputSystem.is_key_just_pressed("down"):
            self._queue_direction((0, 1))
        if InputSystem.is_key_just_pressed("a") or InputSystem.is_key_just_pressed("left"):
            self._queue_direction((-1, 0))
        if InputSystem.is_key_just_pressed("d") or InputSystem.is_key_just_pressed("right"):
            self._queue_direction((1, 0))

    def _queue_direction(self, direction):
        if direction[0] == -self._direction[0] and direction[1] == -self._direction[1]:
            return
        self._queued_direction = direction

    def _step(self):
        self._direction = self._queued_direction
        head_x, head_y = self._snake[0]
        new_head = (head_x + self._direction[0], head_y + self._direction[1])

        if self._hits_bounds(new_head) or new_head in self._snake[:-1]:
            Logger.info("SnakeGame2D", "Colision detectada. Reiniciando partida.")
            self._reset_round("Game Over. Se reinicio la partida.")
            return

        self._snake.insert(0, new_head)
        ate_apple = new_head == self._apple

        if ate_apple:
            self.score += 1
            self.best_score = max(self.best_score, self.score)
            self.tick_time = max(0.06, 0.12 - (self.score * 0.004))
            self._spawn_apple()
            self._set_status("Manzana comida. La siguiente sale en una posicion aleatoria.")
            Logger.info("SnakeGame2D", f"Manzana recogida. Puntuacion actual: {self.score}")
        else:
            self._snake.pop()

        self._sync_collision_shape()
        self._update_hud()

    def _reset_round(self, status_text: str):
        start_x = max(4, self.cols // 4)
        start_y = max(4, self.rows // 2)
        self.score = 0
        self.tick_time = 0.12
        self._elapsed = 0.0
        self._direction = (1, 0)
        self._queued_direction = (1, 0)
        self._snake = [
            (start_x, start_y),
            (start_x - 1, start_y),
            (start_x - 2, start_y),
        ]
        self._spawn_apple()
        self._set_status(status_text)
        self._sync_collision_shape()
        self._update_hud()

    def _spawn_apple(self):
        free_cells = []
        for y in range(self.rows):
            for x in range(self.cols):
                if (x, y) not in self._snake:
                    free_cells.append((x, y))
        self._apple = self._rng.choice(free_cells) if free_cells else (0, 0)

    def _hits_bounds(self, cell) -> bool:
        return cell[0] < 0 or cell[0] >= self.cols or cell[1] < 0 or cell[1] >= self.rows

    def _cell_origin(self, grid_x: int, grid_y: int):
        pos = self.get_global_position()
        return pos.x + (grid_x * self.cell_size), pos.y + (grid_y * self.cell_size)

    def _sync_collision_shape(self):
        if not self.get_children():
            return

        head_x, head_y = self._snake[0]
        for child in self.get_children():
            if child.__class__.__name__ != "CollisionShape2D":
                continue
            child.set_position(head_x * self.cell_size, head_y * self.cell_size)
            if hasattr(child, "size"):
                child.size.x = self.cell_size
                child.size.y = self.cell_size

    def _update_hud(self):
        if self.score_label_node:
            self.score_label_node.set_text(f"Puntos: {self.score}   Record: {self.best_score}")

        if self.apple_label_node:
            apple_x, apple_y = self._apple
            self.apple_label_node.set_text(f"Manzana: ({apple_x}, {apple_y})")

    def _set_status(self, status_text: str):
        if self.status_label_node:
            self.status_label_node.set_text(status_text)
