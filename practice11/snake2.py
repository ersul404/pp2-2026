"""
=============================================================
  SNAKE GAME — Practice 11 (extends Practice 10)
  NEW features for Practice 11:
    1. Randomly generated food with DIFFERENT WEIGHTS
       - Apple   (common,   weight=60) → +10 score, grows by 1
       - Cherry  (uncommon, weight=30) → +25 score, grows by 2
       - Diamond (rare,     weight=10) → +60 score, grows by 3
    2. Food DISAPPEARS after a timer (each tier has its own
       lifespan; rarer food disappears faster to add pressure).
       A shrinking countdown ring is drawn around each food item.
    3. Multiple food items can exist simultaneously on the board.
    4. Fully commented code
=============================================================
"""

import pygame
import random
import sys
import math

# ─────────────────────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────────────────────
CELL        = 20           # pixel side of one grid cell
COLS        = 30           # grid columns
ROWS        = 30           # grid rows
WIDTH       = COLS * CELL  # 600 px
HEIGHT      = ROWS * CELL  # 600 px
FPS_BASE    = 60           # display frame rate (fixed)

# Snake move speeds per level (logic steps per second)
LEVEL_SPEEDS = {1: 8, 2: 10, 3: 13, 4: 16, 5: 20}
MAX_LEVEL       = max(LEVEL_SPEEDS)
FOODS_PER_LEVEL = 3   # foods eaten to advance one level

# Colours
BLACK      = (0,   0,   0)
WHITE      = (255, 255, 255)
DARK_GREEN = (0,   140, 0)
GREEN      = (0,   200, 0)
GOLD       = (255, 200, 0)
GRAY       = (50,  50,  50)
BG         = (15,  15,  15)
WALL_C     = (80,  80,  80)

# Directions (column-delta, row-delta)
UP    = (0,  -1)
DOWN  = (0,   1)
LEFT  = (-1,  0)
RIGHT = (1,   0)

# ── Food tier definitions ─────────────────────────────────────
# (tier_name, colour, score_value, grow_by, lifespan_seconds, spawn_weight)
# lifespan_seconds: how long the food stays before disappearing
# spawn_weight: probability weight — higher means more common
FOOD_TIERS = [
    ("apple",   (220, 50,  50),  10, 1, 10.0, 60),   # common,   long life
    ("cherry",  (255, 20, 147),  25, 2,  7.0, 30),   # uncommon, medium life
    ("diamond", (100, 200, 255), 60, 3,  4.0, 10),   # rare,     short life
]

# Maximum number of food items allowed on board at once
MAX_FOODS = 3

# How many seconds between new food spawns
FOOD_SPAWN_INTERVAL = 3.5


# ─────────────────────────────────────────────────────────────
#  HELPER
# ─────────────────────────────────────────────────────────────
def draw_cell(surface, color, col, row, shrink=2, radius=4):
    """Draw a rounded rectangle for a single grid cell."""
    rect = pygame.Rect(
        col * CELL + shrink,
        row * CELL + shrink,
        CELL - shrink * 2,
        CELL - shrink * 2,
    )
    pygame.draw.rect(surface, color, rect, border_radius=radius)


# ─────────────────────────────────────────────────────────────
#  FOOD ITEM  (Practice 11 — Tasks 1 & 2)
# ─────────────────────────────────────────────────────────────
class FoodItem:
    """
    One food piece on the board.
    Has a tier (weight), a score value, a grow amount, and a lifespan.
    After lifespan seconds it disappears automatically.
    A countdown ring is drawn around it to warn the player.
    """

    def __init__(self, col, row):
        # Choose tier by weighted random selection
        weights = [t[5] for t in FOOD_TIERS]
        tier    = random.choices(FOOD_TIERS, weights=weights, k=1)[0]
        name, colour, score, grow, lifespan, _ = tier

        self.col        = col
        self.row        = row
        self.tier       = name        # string label for debugging
        self.colour     = colour
        self.score      = score       # points awarded when eaten
        self.grow       = grow        # segments the snake gains
        self.lifespan   = lifespan    # total seconds this item lives
        self.age        = 0.0         # seconds this item has existed
        self.alive      = True        # set to False when expired or eaten

    def update(self, dt):
        """Advance age; mark as dead if lifespan exceeded."""
        self.age += dt
        if self.age >= self.lifespan:
            self.alive = False

    @property
    def fraction_remaining(self):
        """Returns 1.0 when fresh, 0.0 when about to expire."""
        return max(0.0, 1.0 - self.age / self.lifespan)

    def draw(self, surface):
        """Draw the food cell plus a countdown ring and tier label."""
        # Main food circle (slightly larger than a standard cell)
        cx = self.col * CELL + CELL // 2
        cy = self.row * CELL + CELL // 2
        r  = CELL // 2 - 1

        pygame.draw.circle(surface, self.colour, (cx, cy), r)
        # Lighter inner highlight
        hi = tuple(min(255, c + 80) for c in self.colour)
        pygame.draw.circle(surface, hi, (cx - r//3, cy - r//3), r // 3)

        # ── Countdown ring ────────────────────────────────────────
        # Draw an arc that shrinks as the food ages.
        # Full arc = 1.0 remaining; no arc = 0.0 remaining.
        frac    = self.fraction_remaining
        ring_r  = r + 4                         # slightly outside the food
        # Colour transitions: green → yellow → red as time runs out
        if frac > 0.5:
            # Green to yellow
            t   = (1.0 - frac) * 2              # 0 → 1 as frac goes 1.0 → 0.5
            rc  = (int(255 * t), 220, 0)
        else:
            # Yellow to red
            t   = (0.5 - frac) * 2              # 0 → 1 as frac goes 0.5 → 0.0
            rc  = (255, int(220 * (1 - t)), 0)

        # Draw the arc as a series of small line segments
        arc_rect = pygame.Rect(cx - ring_r, cy - ring_r, ring_r * 2, ring_r * 2)
        end_angle = -math.pi / 2 + 2 * math.pi * frac  # start at top, go clockwise

        # Use pygame.draw.arc (counterclockwise in pygame coords)
        if frac > 0.01:
            pygame.draw.arc(surface, rc, arc_rect,
                            -math.pi / 2,          # start angle (top)
                            -math.pi / 2 + 2 * math.pi * frac,  # end
                            2)

        # Tier initial label (A / C / D) drawn inside the cell
        font = pygame.font.SysFont("consolas", 11, bold=True)
        lbl  = font.render(self.tier[0].upper(), True, BLACK)
        surface.blit(lbl, lbl.get_rect(center=(cx, cy)))


# ─────────────────────────────────────────────────────────────
#  GAME CLASS
# ─────────────────────────────────────────────────────────────
class SnakeGame:
    """All game logic and rendering."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Snake — Practice 11")
        self.clock = pygame.time.Clock()

        # Fonts at different sizes for HUD / overlays
        self.font_hud  = pygame.font.SysFont("consolas", 20, bold=True)
        self.font_big  = pygame.font.SysFont("consolas", 42, bold=True)
        self.font_med  = pygame.font.SysFont("consolas", 24, bold=True)
        self.font_tiny = pygame.font.SysFont("consolas", 15)

        self._init_game()

    # ── Init / Reset ──────────────────────────────────────────────────────
    def _init_game(self):
        """Create/reset all game state."""
        mid_col = COLS // 2
        mid_row = ROWS // 2

        # Snake body: list of (col, row) tuples, head at index 0
        self.snake = [(mid_col - i, mid_row) for i in range(3)]
        self.direction      = RIGHT
        self.next_direction = RIGHT   # buffer direction from keypress

        # Scoring
        self.score       = 0
        self.level       = 1
        self.foods_eaten = 0    # count for level progression

        # Speed control via time accumulator
        self.ticks_per_second = LEVEL_SPEEDS[self.level]
        self._frame_acc = 0.0

        # ── Food list (Practice 11 — Tasks 1 & 2) ────────────────────
        self.foods           = []        # list of FoodItem objects
        self.food_spawn_acc  = 0.0       # accumulator for next spawn

        # Spawn the first food immediately
        self._spawn_food()

        self.game_over = False
        self.paused    = False

    # ── Food helpers ──────────────────────────────────────────────────────
    def _occupied_cells(self):
        """Return set of all grid cells currently taken (snake + foods)."""
        occupied = set(self.snake)
        for f in self.foods:
            occupied.add((f.col, f.row))
        return occupied

    def _spawn_food(self):
        """
        Spawn a new FoodItem at a random cell that is:
          - not on the border wall
          - not on the snake
          - not on an existing food
        Does nothing if MAX_FOODS is already reached.
        """
        if len(self.foods) >= MAX_FOODS:
            return

        occupied = self._occupied_cells()
        # Try up to 200 times to find a free cell
        for _ in range(200):
            col = random.randint(1, COLS - 2)
            row = random.randint(1, ROWS - 2)
            if (col, row) not in occupied:
                self.foods.append(FoodItem(col, row))
                return

    # ── Main loop ─────────────────────────────────────────────────────────
    def run(self):
        while True:
            dt = self.clock.tick(FPS_BASE) / 1000.0   # delta time in seconds
            self._handle_events()
            if not self.game_over and not self.paused:
                self._update(dt)
            self._draw()

    # ── Events ────────────────────────────────────────────────────────────
    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.game_over:
                    self._init_game()
                if event.key == pygame.K_p:
                    self.paused = not self.paused
                # Direction buffering — prevent 180° reversal
                if event.key == pygame.K_UP    and self.direction != DOWN:
                    self.next_direction = UP
                if event.key == pygame.K_DOWN  and self.direction != UP:
                    self.next_direction = DOWN
                if event.key == pygame.K_LEFT  and self.direction != RIGHT:
                    self.next_direction = LEFT
                if event.key == pygame.K_RIGHT and self.direction != LEFT:
                    self.next_direction = RIGHT

    # ── Update ────────────────────────────────────────────────────────────
    def _update(self, dt):
        """Update food timers, spawn new food, and advance snake logic."""
        # ── Update food ages (Practice 11 — Task 2) ──────────────────
        for food in self.foods:
            food.update(dt)

        # Remove expired food items
        before = len(self.foods)
        self.foods = [f for f in self.foods if f.alive]

        # ── Spawn new food periodically ───────────────────────────────
        self.food_spawn_acc += dt
        if self.food_spawn_acc >= FOOD_SPAWN_INTERVAL:
            self.food_spawn_acc = 0.0
            self._spawn_food()

        # ── Snake movement (time-accumulated) ────────────────────────
        self._frame_acc += dt
        step_time = 1.0 / self.ticks_per_second

        while self._frame_acc >= step_time:
            self._frame_acc -= step_time
            self._step()

    def _step(self):
        """Move the snake one cell and handle all collisions."""
        self.direction = self.next_direction

        # New head position
        hc, hr = self.snake[0]
        dc, dr = self.direction
        new_head = (hc + dc, hr + dr)
        nc, nr   = new_head

        # ── Wall collision ────────────────────────────────────────────
        if nc <= 0 or nc >= COLS - 1 or nr <= 0 or nr >= ROWS - 1:
            self.game_over = True
            return

        # ── Self collision ────────────────────────────────────────────
        if new_head in self.snake:
            self.game_over = True
            return

        # Tentatively add new head
        self.snake.insert(0, new_head)

        # ── Food collision (Practice 11 — Task 1 & 2) ────────────────
        eaten = None
        for food in self.foods:
            if (food.col, food.row) == new_head:
                eaten = food
                break

        if eaten:
            # Award score and grow snake by food.grow segments
            self.score       += eaten.score
            self.foods_eaten += 1
            self.foods.remove(eaten)

            # Grow extra segments (we already added head, now keep tail
            # and add grow-1 more by NOT removing tail for grow steps)
            for _ in range(eaten.grow - 1):
                # Duplicate the current tail to extend length
                self.snake.append(self.snake[-1])

            # Level up?
            if self.foods_eaten >= FOODS_PER_LEVEL and self.level < MAX_LEVEL:
                self.level       += 1
                self.foods_eaten  = 0
                self.ticks_per_second = LEVEL_SPEEDS[self.level]

            # Spawn a replacement food
            self._spawn_food()
        else:
            # No food eaten — remove tail to keep length constant
            self.snake.pop()

    # ── Draw ──────────────────────────────────────────────────────────────
    def _draw(self):
        self.screen.fill(BG)

        # Subtle grid dots
        for c in range(COLS):
            for r in range(ROWS):
                pygame.draw.circle(self.screen, GRAY,
                                   (c * CELL + CELL // 2, r * CELL + CELL // 2), 1)

        # Wall border (one cell thick)
        pygame.draw.rect(self.screen, WALL_C,
                         pygame.Rect(0, 0, WIDTH, HEIGHT), CELL)

        # Snake body
        for i, (col, row) in enumerate(self.snake):
            color = GREEN if i == 0 else DARK_GREEN
            draw_cell(self.screen, color, col, row)
            if i == 0:
                self._draw_eyes(col, row)

        # All food items (Practice 11)
        for food in self.foods:
            food.draw(self.screen)

        # HUD
        self._draw_hud()

        # Overlays
        if self.paused:
            self._draw_overlay("PAUSED", "P — resume")
        if self.game_over:
            self._draw_overlay(
                "GAME OVER",
                f"Score: {self.score}  Level: {self.level}  R — restart"
            )

        pygame.display.flip()

    def _draw_eyes(self, col, row):
        """Draw two tiny eyes on the snake's head."""
        cx = col * CELL + CELL // 2
        cy = row * CELL + CELL // 2
        dx, dy = self.direction
        perp   = (-dy, dx)
        for sign in (-1, 1):
            ex = cx + sign * perp[0] * 4 + dx * 4
            ey = cy + sign * perp[1] * 4 + dy * 4
            pygame.draw.circle(self.screen, WHITE, (ex, ey), 3)
            pygame.draw.circle(self.screen, BLACK, (ex + dx, ey + dy), 1)

    def _draw_hud(self):
        """Render score, level, food progress, and tier legend."""
        # Score
        self.screen.blit(
            self.font_hud.render(f"Score: {self.score}", True, WHITE),
            (CELL + 4, 4))

        # Level (centred)
        ls = self.font_hud.render(f"Level: {self.level}", True, GOLD)
        self.screen.blit(ls, (WIDTH // 2 - ls.get_width() // 2, 4))

        # Foods to next level (top-right)
        if self.level < MAX_LEVEL:
            rem = FOODS_PER_LEVEL - self.foods_eaten
            ps  = self.font_tiny.render(
                f"Next lvl: {rem} food{'s' if rem != 1 else ''}", True, (180, 180, 180))
        else:
            ps = self.font_tiny.render("MAX LEVEL", True, GOLD)
        self.screen.blit(ps, (WIDTH - ps.get_width() - CELL - 4, 4))

        # Food tier legend (bottom-left)
        lx, ly = CELL + 4, HEIGHT - CELL - 4
        for name, colour, score, grow, life, _ in reversed(FOOD_TIERS):
            pygame.draw.circle(self.screen, colour, (lx + 6, ly - 4), 6)
            txt = self.font_tiny.render(
                f"{name}: +{score}pts  +{grow}seg  {life}s", True, (180, 180, 180))
            self.screen.blit(txt, (lx + 16, ly - 12))
            ly -= 18

    def _draw_overlay(self, title, subtitle):
        """Semi-transparent full-screen overlay."""
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        self.screen.blit(overlay, (0, 0))
        t = self.font_big.render(title, True, WHITE)
        self.screen.blit(t, t.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30)))
        s = self.font_med.render(subtitle, True, (200, 200, 200))
        self.screen.blit(s, s.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 25)))


# ─────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    SnakeGame().run()