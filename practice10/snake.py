"""
=============================================================
  SNAKE GAME — Extended Version
  Features:
    - Wall (border) collision detection
    - Random food placement (not on wall or snake)
    - Levels system — every 3 foods eaten = new level
    - Speed increases per level
    - Score and level counter on screen
    - Fully commented code
=============================================================
"""

import pygame
import random
import sys

# ─────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────
CELL        = 20          # pixel size of one grid cell
COLS        = 30          # grid columns
ROWS        = 30          # grid rows
WIDTH       = COLS * CELL # window width  (600)
HEIGHT      = ROWS * CELL # window height (600)
FPS_BASE    = 60          # pygame clock tick (constant)

# How many game-logic updates per second at each level
# (real speed the snake moves)
LEVEL_SPEEDS = {
    1: 8,
    2: 10,
    3: 13,
    4: 16,
    5: 20,
}
MAX_LEVEL       = max(LEVEL_SPEEDS)
FOODS_PER_LEVEL = 3       # foods needed to advance a level

# Colours
BLACK      = (0,   0,   0)
WHITE      = (255, 255, 255)
DARK_GREEN = (0,   140, 0)
GREEN      = (0,   200, 0)
RED        = (220, 30,  30)
GOLD       = (255, 200, 0)
GRAY       = (50,  50,  50)
BG         = (15,  15,  15)
WALL_C     = (80,  80,  80)

# Directions (dx, dy)
UP    = (0,  -1)
DOWN  = (0,   1)
LEFT  = (-1,  0)
RIGHT = (1,   0)

# ─────────────────────────────────────────────
#  HELPER: draw a rounded cell
# ─────────────────────────────────────────────
def draw_cell(surface, color, col, row, shrink=2, radius=4):
    """Draw a slightly shrunk rounded rectangle for one grid cell."""
    rect = pygame.Rect(
        col * CELL + shrink,
        row * CELL + shrink,
        CELL - shrink * 2,
        CELL - shrink * 2,
    )
    pygame.draw.rect(surface, color, rect, border_radius=radius)


# ─────────────────────────────────────────────
#  GAME CLASS
# ─────────────────────────────────────────────
class SnakeGame:
    """All game logic and rendering."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Snake — Levels & Speed")
        self.clock = pygame.time.Clock()

        # Fonts
        self.font_hud  = pygame.font.SysFont("consolas", 20, bold=True)
        self.font_big  = pygame.font.SysFont("consolas", 42, bold=True)
        self.font_med  = pygame.font.SysFont("consolas", 24, bold=True)
        self.font_tiny = pygame.font.SysFont("consolas", 16)

        self._init_game()

    # ── Init / Reset ────────────────────────────────────────────────────
    def _init_game(self):
        """Reset all state for a new game."""
        # Snake starts in the middle, length 3, moving right
        mid_col = COLS // 2
        mid_row = ROWS // 2
        self.snake = [(mid_col - i, mid_row) for i in range(3)]  # head first
        self.direction     = RIGHT
        self.next_direction = RIGHT   # buffered direction from keypress

        # Scoring / levels
        self.score       = 0
        self.level       = 1
        self.foods_eaten = 0          # foods eaten in current level

        # Timing: how many logic ticks per second at current level
        self.ticks_per_second = LEVEL_SPEEDS[self.level]
        self._frame_acc = 0.0         # accumulator for fractional frames

        # Place first food
        self.food = self._random_food()

        self.game_over = False
        self.paused    = False

    # ── Food placement ───────────────────────────────────────────────────
    def _random_food(self):
        """
        Return (col, row) for food that does NOT overlap:
          - the wall border (col/row == 0 or max-1)
          - any cell currently occupied by the snake
        """
        while True:
            col = random.randint(1, COLS - 2)   # stay inside wall
            row = random.randint(1, ROWS - 2)
            if (col, row) not in self.snake:
                return (col, row)

    # ── Main loop ────────────────────────────────────────────────────────
    def run(self):
        while True:
            dt = self.clock.tick(FPS_BASE) / 1000.0   # seconds since last frame

            self._handle_events()

            if not self.game_over and not self.paused:
                self._update(dt)

            self._draw()

    # ── Events ───────────────────────────────────────────────────────────
    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                # Restart
                if event.key == pygame.K_r and self.game_over:
                    self._init_game()
                # Pause
                if event.key == pygame.K_p:
                    self.paused = not self.paused
                # Direction input — prevent 180° reversal
                if event.key == pygame.K_UP    and self.direction != DOWN:
                    self.next_direction = UP
                if event.key == pygame.K_DOWN  and self.direction != UP:
                    self.next_direction = DOWN
                if event.key == pygame.K_LEFT  and self.direction != RIGHT:
                    self.next_direction = LEFT
                if event.key == pygame.K_RIGHT and self.direction != LEFT:
                    self.next_direction = RIGHT

    # ── Update (logic tick) ──────────────────────────────────────────────
    def _update(self, dt):
        """
        Accumulate time; when enough time has passed for one
        logic step, move the snake.
        """
        self._frame_acc += dt
        step_time = 1.0 / self.ticks_per_second   # seconds per step

        while self._frame_acc >= step_time:
            self._frame_acc -= step_time
            self._step()

    def _step(self):
        """Move the snake one cell, check collisions and food."""
        # Apply buffered direction
        self.direction = self.next_direction

        # Calculate new head position
        head_col, head_row = self.snake[0]
        dx, dy = self.direction
        new_head = (head_col + dx, head_row + dy)
        new_col, new_row = new_head

        # ── Wall collision ──────────────────────────────────────────
        # The border row/col (0 and COLS-1/ROWS-1) act as walls
        if new_col <= 0 or new_col >= COLS - 1 or \
           new_row <= 0 or new_row >= ROWS - 1:
            self.game_over = True
            return

        # ── Self collision ──────────────────────────────────────────
        if new_head in self.snake:
            self.game_over = True
            return

        # ── Move snake (insert new head, remove tail) ───────────────
        self.snake.insert(0, new_head)

        if new_head == self.food:
            # Ate food: grow (don't remove tail), update score
            self.score      += 10 * self.level   # more pts at higher levels
            self.foods_eaten += 1

            # Level up?
            if self.foods_eaten >= FOODS_PER_LEVEL and self.level < MAX_LEVEL:
                self.level       += 1
                self.foods_eaten  = 0
                self.ticks_per_second = LEVEL_SPEEDS[self.level]

            # Spawn new food
            self.food = self._random_food()
        else:
            # Normal move: remove the last tail cell
            self.snake.pop()

    # ── Draw ─────────────────────────────────────────────────────────────
    def _draw(self):
        self.screen.fill(BG)

        # Grid dots (subtle)
        for c in range(COLS):
            for r in range(ROWS):
                pygame.draw.circle(self.screen, GRAY,
                                   (c * CELL + CELL // 2,
                                    r * CELL + CELL // 2), 1)

        # ── Wall border ─────────────────────────────────────────────
        wall_rect = pygame.Rect(0, 0, WIDTH, HEIGHT)
        pygame.draw.rect(self.screen, WALL_C, wall_rect, CELL)

        # ── Snake ───────────────────────────────────────────────────
        for i, (col, row) in enumerate(self.snake):
            color = GREEN if i == 0 else DARK_GREEN   # head is brighter
            draw_cell(self.screen, color, col, row)
            # Eyes on the head
            if i == 0:
                self._draw_eyes(col, row)

        # ── Food ────────────────────────────────────────────────────
        fc, fr = self.food
        draw_cell(self.screen, RED, fc, fr, shrink=1, radius=CELL // 2)

        # ── HUD ─────────────────────────────────────────────────────
        self._draw_hud()

        # ── Overlays ────────────────────────────────────────────────
        if self.paused:
            self._draw_overlay("PAUSED", "P — resume")
        if self.game_over:
            self._draw_overlay(
                "GAME OVER",
                f"Score: {self.score}   Level: {self.level}   R — restart"
            )

        pygame.display.flip()

    def _draw_eyes(self, col, row):
        """Small white eyes on the snake head indicating direction."""
        cx = col * CELL + CELL // 2
        cy = row * CELL + CELL // 2
        dx, dy = self.direction
        # Offset eyes perpendicular to movement direction
        perp = (-dy, dx)
        for sign in (-1, 1):
            ex = cx + sign * perp[0] * 4 + dx * 4
            ey = cy + sign * perp[1] * 4 + dy * 4
            pygame.draw.circle(self.screen, WHITE, (ex, ey), 3)
            pygame.draw.circle(self.screen, BLACK, (ex + dx, ey + dy), 1)

    def _draw_hud(self):
        """Render score, level, and foods-to-next-level."""
        # Score
        score_s = self.font_hud.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_s, (CELL + 4, 4))

        # Level
        level_s = self.font_hud.render(f"Level: {self.level}", True, GOLD)
        self.screen.blit(level_s, (WIDTH // 2 - level_s.get_width() // 2, 4))

        # Foods to next level
        if self.level < MAX_LEVEL:
            remaining = FOODS_PER_LEVEL - self.foods_eaten
            prog_s = self.font_tiny.render(
                f"Next lvl in {remaining} food{'s' if remaining != 1 else ''}",
                True, (180, 180, 180)
            )
            self.screen.blit(prog_s, (WIDTH - prog_s.get_width() - CELL - 4, 4))
        else:
            max_s = self.font_tiny.render("MAX LEVEL", True, GOLD)
            self.screen.blit(max_s, (WIDTH - max_s.get_width() - CELL - 4, 4))

    def _draw_overlay(self, title, subtitle):
        """Dark translucent overlay with centred text."""
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        self.screen.blit(overlay, (0, 0))

        t = self.font_big.render(title, True, WHITE)
        self.screen.blit(t, t.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30)))

        s = self.font_med.render(subtitle, True, (200, 200, 200))
        self.screen.blit(s, s.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 25)))


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    game = SnakeGame()
    game.run()