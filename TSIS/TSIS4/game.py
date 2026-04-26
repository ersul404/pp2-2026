"""
game.py — Core Snake game logic for TSIS 4.
Extends Practice 10 & 11 with:
  - Poison food (shortens snake by 2)
  - Three power-ups: Speed Boost, Slow Motion, Shield
  - Obstacle blocks from Level 3
  - Personal best display
  - DB save on game over
"""

import pygame
import random
import math
import json
import os
from config import *
from db import save_result, get_personal_best


# ─────────────────────────────────────────────
#  SETTINGS  helpers
# ─────────────────────────────────────────────
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE) as f:
                data = json.load(f)
            for k, v in DEFAULT_SETTINGS.items():
                data.setdefault(k, v)
            return data
        except Exception:
            pass
    return dict(DEFAULT_SETTINGS)


def save_settings(settings: dict):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)


# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def draw_cell(surface, color, col, row, shrink=2, radius=4):
    rect = pygame.Rect(
        col * CELL + shrink,
        row * CELL + shrink,
        CELL - shrink * 2,
        CELL - shrink * 2,
    )
    pygame.draw.rect(surface, color, rect, border_radius=radius)


# ─────────────────────────────────────────────
#  FOOD ITEM  (weighted + disappearing, from P11)
# ─────────────────────────────────────────────
class FoodItem:
    def __init__(self, col, row):
        weights = [t[5] for t in FOOD_TIERS]
        tier    = random.choices(FOOD_TIERS, weights=weights, k=1)[0]
        name, colour, score, grow, lifespan, _ = tier
        self.col      = col
        self.row      = row
        self.tier     = name
        self.colour   = colour
        self.score    = score
        self.grow     = grow
        self.lifespan = lifespan
        self.age      = 0.0
        self.alive    = True

    def update(self, dt):
        self.age += dt
        if self.age >= self.lifespan:
            self.alive = False

    @property
    def fraction_remaining(self):
        return max(0.0, 1.0 - self.age / self.lifespan)

    def draw(self, surface):
        cx = self.col * CELL + CELL // 2
        cy = self.row * CELL + CELL // 2
        r  = CELL // 2 - 1
        pygame.draw.circle(surface, self.colour, (cx, cy), r)
        hi = tuple(min(255, c + 80) for c in self.colour)
        pygame.draw.circle(surface, hi, (cx - r//3, cy - r//3), r // 3)

        # Countdown arc
        frac = self.fraction_remaining
        ring_r = r + 4
        if frac > 0.5:
            t  = (1.0 - frac) * 2
            rc = (int(255 * t), 220, 0)
        else:
            t  = (0.5 - frac) * 2
            rc = (255, int(220 * (1 - t)), 0)
        arc_rect = pygame.Rect(cx - ring_r, cy - ring_r, ring_r*2, ring_r*2)
        if frac > 0.01:
            pygame.draw.arc(surface, rc, arc_rect,
                            -math.pi/2,
                            -math.pi/2 + 2*math.pi*frac, 2)
        font = pygame.font.SysFont("consolas", 11, bold=True)
        lbl  = font.render(self.tier[0].upper(), True, BLACK)
        surface.blit(lbl, lbl.get_rect(center=(cx, cy)))


# ─────────────────────────────────────────────
#  POISON FOOD
# ─────────────────────────────────────────────
class PoisonFood:
    """
    Dark-red item. Eating it shortens the snake by 2 segments.
    If snake length drops to ≤ 1 → game over.
    Disappears after FOOD_SPAWN_INTERVAL * 2 seconds.
    """
    LIFESPAN = FOOD_SPAWN_INTERVAL * 2

    def __init__(self, col, row):
        self.col   = col
        self.row   = row
        self.age   = 0.0
        self.alive = True

    def update(self, dt):
        self.age += dt
        if self.age >= self.LIFESPAN:
            self.alive = False

    def draw(self, surface):
        cx = self.col * CELL + CELL // 2
        cy = self.row * CELL + CELL // 2
        r  = CELL // 2 - 1
        # Dark red circle with skull-like cross
        pygame.draw.circle(surface, POISON_C, (cx, cy), r)
        pygame.draw.circle(surface, (200, 0, 30), (cx, cy), r, 2)
        font = pygame.font.SysFont("consolas", 12, bold=True)
        lbl  = font.render("☠", True, (255, 80, 80))
        surface.blit(lbl, lbl.get_rect(center=(cx, cy)))


# ─────────────────────────────────────────────
#  POWER-UP
# ─────────────────────────────────────────────
class PowerUpItem:
    """
    One of: "speed", "slow", "shield".
    Disappears from the field after POWERUP_FIELD_LIFE seconds.
    """
    def __init__(self, kind, col, row):
        self.kind    = kind
        self.col     = col
        self.row     = row
        self.age     = 0.0
        self.alive   = True
        self.colour  = POWERUP_COLORS[kind]

    def update(self, dt):
        self.age += dt
        if self.age >= POWERUP_FIELD_LIFE:
            self.alive = False

    @property
    def fraction_remaining(self):
        return max(0.0, 1.0 - self.age / POWERUP_FIELD_LIFE)

    def draw(self, surface):
        cx = self.col * CELL + CELL // 2
        cy = self.row * CELL + CELL // 2
        r  = CELL // 2 - 1

        # Pulsing glow
        t     = pygame.time.get_ticks() / 1000.0
        scale = 1.0 + 0.15 * math.sin(t * 5)
        pr    = max(1, int(r * scale))
        glow  = pygame.Surface((pr*2+4, pr*2+4), pygame.SRCALPHA)
        gc    = (*self.colour, 60)
        pygame.draw.circle(glow, gc, (pr+2, pr+2), pr+2)
        surface.blit(glow, (cx - pr - 2, cy - pr - 2))

        pygame.draw.circle(surface, self.colour, (cx, cy), r)
        pygame.draw.circle(surface, WHITE, (cx, cy), r, 2)

        labels = {"speed": "▲", "slow": "▼", "shield": "S"}
        font = pygame.font.SysFont("consolas", 12, bold=True)
        lbl  = font.render(labels[self.kind], True, WHITE)
        surface.blit(lbl, lbl.get_rect(center=(cx, cy)))

        # Timeout arc
        frac     = self.fraction_remaining
        ring_r   = r + 4
        arc_rect = pygame.Rect(cx - ring_r, cy - ring_r, ring_r*2, ring_r*2)
        if frac > 0.01:
            pygame.draw.arc(surface, self.colour, arc_rect,
                            -math.pi/2,
                            -math.pi/2 + 2*math.pi*frac, 2)


# ─────────────────────────────────────────────
#  OBSTACLE BLOCK
# ─────────────────────────────────────────────
class ObstacleBlock:
    def __init__(self, col, row):
        self.col = col
        self.row = row

    def draw(self, surface):
        rect = pygame.Rect(self.col*CELL, self.row*CELL, CELL, CELL)
        pygame.draw.rect(surface, OBSTACLE_C, rect)
        pygame.draw.rect(surface, (140, 110, 80), rect, 2)
        # Cross pattern to look like a wall brick
        pygame.draw.line(surface, (80, 60, 40),
                         (rect.left, rect.centery), (rect.right, rect.centery), 1)
        pygame.draw.line(surface, (80, 60, 40),
                         (rect.centerx, rect.top), (rect.centerx, rect.bottom), 1)


# ─────────────────────────────────────────────
#  SNAKE GAME
# ─────────────────────────────────────────────
class SnakeGame:
    def __init__(self, screen, clock, username, settings):
        self.screen   = screen
        self.clock    = clock
        self.username = username
        self.settings = settings

        # Fonts
        self.font_hud  = pygame.font.SysFont("consolas", 20, bold=True)
        self.font_big  = pygame.font.SysFont("consolas", 42, bold=True)
        self.font_med  = pygame.font.SysFont("consolas", 24, bold=True)
        self.font_tiny = pygame.font.SysFont("consolas", 15)

        self.personal_best = get_personal_best(username)
        self._init_game()

    def _init_game(self):
        mid_col = COLS // 2
        mid_row = ROWS // 2

        self.snake          = [(mid_col - i, mid_row) for i in range(3)]
        self.direction      = RIGHT
        self.next_direction = RIGHT

        self.score       = 0
        self.level       = 1
        self.foods_eaten = 0

        self.ticks_per_second = LEVEL_SPEEDS[self.level]
        self._frame_acc       = 0.0

        # Food / poison
        self.foods           = []
        self.poison          = None
        self.food_spawn_acc  = 0.0
        self.poison_spawn_acc = 0.0

        # Power-up on field and active effect
        self.field_powerup      = None    # PowerUpItem or None
        self.powerup_spawn_acc  = 0.0
        self.active_powerup     = None    # "speed" | "slow" | "shield" | None
        self.powerup_effect_end = 0       # ms (get_ticks)
        self.shield_ready       = False   # shield absorbed one hit

        # Obstacles
        self.obstacles    = set()   # set of (col, row)
        self.obs_cells    = []      # list of ObstacleBlock

        self.game_over = False
        self.paused    = False
        self.saved     = False      # prevent double-save

        # Spawn initial food
        self._spawn_food()

    # ── Occupied cells ────────────────────────────────────────────────────
    def _occupied(self):
        occ = set(self.snake) | self.obstacles
        for f in self.foods:
            occ.add((f.col, f.row))
        if self.poison:
            occ.add((self.poison.col, self.poison.row))
        if self.field_powerup:
            occ.add((self.field_powerup.col, self.field_powerup.row))
        return occ

    def _random_free_cell(self):
        occ = self._occupied()
        # Exclude border
        for _ in range(500):
            col = random.randint(1, COLS - 2)
            row = random.randint(1, ROWS - 2)
            if (col, row) not in occ:
                return col, row
        return None

    # ── Spawning ──────────────────────────────────────────────────────────
    def _spawn_food(self):
        if len(self.foods) >= MAX_FOODS:
            return
        cell = self._random_free_cell()
        if cell:
            self.foods.append(FoodItem(*cell))

    def _spawn_poison(self):
        if self.poison and self.poison.alive:
            return
        cell = self._random_free_cell()
        if cell:
            self.poison = PoisonFood(*cell)

    def _spawn_powerup(self):
        if self.field_powerup and self.field_powerup.alive:
            return
        cell = self._random_free_cell()
        if cell:
            kind = random.choice(["speed", "slow", "shield"])
            self.field_powerup = PowerUpItem(kind, *cell)

    def _place_obstacles(self):
        """
        Place OBSTACLES_PER_LEVEL * (level - MIN_LEVEL_FOR_OBS + 1) blocks,
        guaranteed not to be on the snake's head area (3x3 safe zone).
        """
        count    = OBSTACLES_PER_LEVEL * (self.level - MIN_LEVEL_FOR_OBS + 1)
        hc, hr   = self.snake[0]
        safe_zone = {(hc+dc, hr+dr)
                     for dc in range(-3, 4) for dr in range(-3, 4)}

        for _ in range(count):
            for attempt in range(300):
                col = random.randint(1, COLS - 2)
                row = random.randint(1, ROWS - 2)
                pos = (col, row)
                if (pos not in self.obstacles
                        and pos not in set(self.snake)
                        and pos not in safe_zone):
                    self.obstacles.add(pos)
                    self.obs_cells.append(ObstacleBlock(col, row))
                    break

    # ── Main run loop ─────────────────────────────────────────────────────
    def run(self):
        """Returns "retry" or "menu"."""
        from ui import GameOverScreen
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self._handle_events()
            if not self.game_over and not self.paused:
                self._update(dt)
            self._draw()

            if self.game_over:
                if not self.saved:
                    save_result(self.username, self.score, self.level)
                    self.saved = True
                    if self.score > self.personal_best:
                        self.personal_best = self.score
                return GameOverScreen().run(
                    self.screen, self.clock,
                    self.score, self.level, self.personal_best, self.username
                )

    # ── Events ────────────────────────────────────────────────────────────
    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                import sys; pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    self.paused = not self.paused
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
        now = pygame.time.get_ticks()

        # ── Power-up effect expiry ────────────────────────────────────
        if self.active_powerup in ("speed", "slow"):
            if now >= self.powerup_effect_end:
                self.active_powerup = None

        # ── Current speed (modified by power-up) ─────────────────────
        base_tps = LEVEL_SPEEDS[self.level]
        if self.active_powerup == "speed":
            tps = base_tps + SPEED_BOOST_EXTRA
        elif self.active_powerup == "slow":
            tps = max(2, base_tps - SLOW_MOTION_REDUCE)
        else:
            tps = base_tps
        self.ticks_per_second = tps

        # ── Food / poison / power-up timers ──────────────────────────
        for food in self.foods:
            food.update(dt)
        self.foods = [f for f in self.foods if f.alive]

        if self.poison:
            self.poison.update(dt)
            if not self.poison.alive:
                self.poison = None

        if self.field_powerup:
            self.field_powerup.update(dt)
            if not self.field_powerup.alive:
                self.field_powerup = None

        # ── Spawn timers ──────────────────────────────────────────────
        self.food_spawn_acc += dt
        if self.food_spawn_acc >= FOOD_SPAWN_INTERVAL:
            self.food_spawn_acc = 0.0
            self._spawn_food()

        self.poison_spawn_acc += dt
        if self.poison_spawn_acc >= FOOD_SPAWN_INTERVAL * 1.5:
            self.poison_spawn_acc = 0.0
            self._spawn_poison()

        self.powerup_spawn_acc += dt
        if self.powerup_spawn_acc >= FOOD_SPAWN_INTERVAL * 2:
            self.powerup_spawn_acc = 0.0
            self._spawn_powerup()

        # ── Snake movement ────────────────────────────────────────────
        self._frame_acc += dt
        step_time = 1.0 / self.ticks_per_second
        while self._frame_acc >= step_time:
            self._frame_acc -= step_time
            self._step()

    def _step(self):
        self.direction = self.next_direction
        hc, hr = self.snake[0]
        dc, dr = self.direction
        new_head = (hc + dc, hr + dr)
        nc, nr   = new_head

        # ── Wall collision ────────────────────────────────────────────
        hit_wall = (nc <= 0 or nc >= COLS - 1 or nr <= 0 or nr >= ROWS - 1)
        if hit_wall:
            if self.shield_ready:
                self.shield_ready   = False
                self.active_powerup = None
                return   # skip this step (absorb hit)
            self.game_over = True
            return

        # ── Obstacle collision ────────────────────────────────────────
        if new_head in self.obstacles:
            if self.shield_ready:
                self.shield_ready   = False
                self.active_powerup = None
                return
            self.game_over = True
            return

        # ── Self collision ────────────────────────────────────────────
        if new_head in self.snake:
            if self.shield_ready:
                self.shield_ready   = False
                self.active_powerup = None
                return
            self.game_over = True
            return

        # Move
        self.snake.insert(0, new_head)

        # ── Poison collision ──────────────────────────────────────────
        if self.poison and (self.poison.col, self.poison.row) == new_head:
            self.poison = None
            # Shorten by 2 (already added head, remove 2 from tail)
            for _ in range(min(2, len(self.snake) - 1)):
                self.snake.pop()
            if len(self.snake) <= 1:
                self.game_over = True
                return
            self.snake.pop()   # normal tail removal
            return

        # ── Power-up collection ───────────────────────────────────────
        if (self.field_powerup
                and (self.field_powerup.col, self.field_powerup.row) == new_head):
            kind = self.field_powerup.kind
            self.field_powerup = None
            now = pygame.time.get_ticks()
            if kind == "shield":
                self.active_powerup = "shield"
                self.shield_ready   = True
            else:
                self.active_powerup     = kind
                self.powerup_effect_end = now + int(POWERUP_DURATION * 1000)
            self.snake.pop()   # normal move (no growth)
            return

        # ── Food collision ────────────────────────────────────────────
        eaten = None
        for food in self.foods:
            if (food.col, food.row) == new_head:
                eaten = food
                break

        if eaten:
            self.score       += eaten.score
            self.foods_eaten += 1
            self.foods.remove(eaten)
            # Grow extra segments
            for _ in range(eaten.grow - 1):
                self.snake.append(self.snake[-1])
            # Level up?
            if self.foods_eaten >= FOODS_PER_LEVEL and self.level < MAX_LEVEL:
                self.level       += 1
                self.foods_eaten  = 0
                # Place obstacles starting from level 3
                if self.level >= MIN_LEVEL_FOR_OBS:
                    self._place_obstacles()
            self._spawn_food()
        else:
            self.snake.pop()

    # ── Draw ──────────────────────────────────────────────────────────────
    def _draw(self):
        self.screen.fill(BG)
        snake_color = tuple(self.settings.get("snake_color", [0, 200, 0]))

        # Grid overlay
        if self.settings.get("grid", True):
            for c in range(COLS):
                for r in range(ROWS):
                    pygame.draw.circle(self.screen, GRAY,
                                       (c*CELL + CELL//2, r*CELL + CELL//2), 1)

        # Wall border
        pygame.draw.rect(self.screen, WALL_C,
                         pygame.Rect(0, 0, WIDTH, HEIGHT), CELL)

        # Obstacles
        for ob in self.obs_cells:
            ob.draw(self.screen)

        # Food items
        for food in self.foods:
            food.draw(self.screen)

        # Poison
        if self.poison and self.poison.alive:
            self.poison.draw(self.screen)

        # Power-up on field
        if self.field_powerup and self.field_powerup.alive:
            self.field_powerup.draw(self.screen)

        # Snake
        head_col, _ = self.snake[0], None
        dark = tuple(max(0, c - 60) for c in snake_color)
        for i, (col, row) in enumerate(self.snake):
            color = snake_color if i == 0 else dark
            draw_cell(self.screen, color, col, row)
            if i == 0:
                self._draw_eyes(col, row)

        # Shield glow around head
        if self.shield_ready:
            t   = pygame.time.get_ticks() / 1000.0
            a   = int(140 + 80 * math.sin(t * 6))
            hc, hr = self.snake[0]
            glow = pygame.Surface((CELL + 10, CELL + 10), pygame.SRCALPHA)
            pygame.draw.rect(glow, (0, 220, 120, a), glow.get_rect(), 3)
            self.screen.blit(glow, (hc*CELL - 5, hr*CELL - 5))

        self._draw_hud()

        if self.paused:
            self._draw_overlay("PAUSED", "P — resume")

        pygame.display.flip()

    def _draw_eyes(self, col, row):
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
        # Score / level / personal best
        self.screen.blit(
            self.font_hud.render(f"Score: {self.score}", True, WHITE), (CELL+4, 4))
        ls = self.font_hud.render(f"Level: {self.level}", True, GOLD)
        self.screen.blit(ls, (WIDTH//2 - ls.get_width()//2, 4))

        pb = self.font_tiny.render(f"Best: {self.personal_best}", True, LGRAY)
        self.screen.blit(pb, (WIDTH - pb.get_width() - CELL - 4, 4))

        # Foods to next level
        if self.level < MAX_LEVEL:
            rem = FOODS_PER_LEVEL - self.foods_eaten
            ps  = self.font_tiny.render(
                f"Next lvl: {rem} food{'s' if rem != 1 else ''}",
                True, (180, 180, 180))
        else:
            ps = self.font_tiny.render("MAX LEVEL", True, GOLD)
        self.screen.blit(ps, (WIDTH - ps.get_width() - CELL - 4, 24))

        # Active power-up indicator
        if self.active_powerup:
            now = pygame.time.get_ticks()
            col = POWERUP_COLORS.get(self.active_powerup, WHITE)
            if self.active_powerup == "shield":
                txt = "SHIELD ready"
            else:
                remaining = max(0, (self.powerup_effect_end - now) / 1000)
                txt = f"{self.active_powerup.upper()} {remaining:.1f}s"
            pu_s = self.font_tiny.render(f"⚡ {txt}", True, col)
            pygame.draw.rect(self.screen, (0, 0, 0),
                             (WIDTH//2 - pu_s.get_width()//2 - 6, HEIGHT - 24,
                              pu_s.get_width() + 12, 20))
            self.screen.blit(pu_s,
                             (WIDTH//2 - pu_s.get_width()//2, HEIGHT - 22))

        # Legend bottom-left
        lx, ly = CELL + 4, HEIGHT - CELL - 4
        for name, colour, score, grow, life, _ in reversed(FOOD_TIERS):
            pygame.draw.circle(self.screen, colour, (lx + 6, ly - 4), 6)
            txt = self.font_tiny.render(
                f"{name}: +{score}pts  +{grow}seg", True, (160, 160, 160))
            self.screen.blit(txt, (lx + 16, ly - 12))
            ly -= 18

    def _draw_overlay(self, title, sub):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        self.screen.blit(overlay, (0, 0))
        t = self.font_big.render(title, True, WHITE)
        self.screen.blit(t, t.get_rect(center=(WIDTH//2, HEIGHT//2 - 30)))
        s = self.font_med.render(sub, True, (200, 200, 200))
        self.screen.blit(s, s.get_rect(center=(WIDTH//2, HEIGHT//2 + 25)))