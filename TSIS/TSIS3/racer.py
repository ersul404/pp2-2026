"""
racer.py — Core game logic for TSIS 3 Racer.
Extends Practice 10 & 11 with:
  - Lane hazards: oil spills, speed bumps, nitro strips
  - Road obstacles: barriers, potholes
  - Three power-ups: Nitro, Shield, Repair
  - Dynamic difficulty scaling
  - Score = distance + coins + power-up bonuses
  - Safe spawn logic (never on top of player)
"""

import pygame
import random
import sys
import math
from persistence import load_settings, save_score

# ── Colours ───────────────────────────────────────────────────────────────────
WHITE      = (255, 255, 255)
BLACK      = (0,   0,   0)
ASPHALT    = (50,  52,  55)
GOLD_C     = (255, 185, 0)
SILVER_C   = (192, 192, 210)
BRONZE_C   = (180, 100, 30)
GRASS_D    = (34,  90,  34)
GRASS_L    = (45,  120, 45)
CURB_C     = (210, 200, 185)
MERC_SHINE = (60,  70,  80)
MERC_GLASS = (140, 200, 230)
LED_WHITE  = (230, 240, 255)
LED_RED    = (255, 60,  60)
ORANGE     = (255, 140, 0)
RED        = (220, 40,  40)
TEAL       = (0,   200, 180)
PURPLE     = (160, 0,   200)

BUILDING_COLORS = [
    (60, 65, 80), (75, 70, 85), (55, 75, 90),
    (80, 60, 60), (65, 80, 65), (90, 80, 55),
]
ENEMY_PALETTES = [
    (200, 30, 30), (30, 160, 30), (255, 140, 0),
    (160, 0, 160), (0, 140, 200), (200, 200, 50),
]

# Screen / road geometry
SW, SH     = 600, 700
FPS        = 60
ROAD_LEFT  = 80
ROAD_RIGHT = 480
ROAD_W     = ROAD_RIGHT - ROAD_LEFT
LANE_W     = ROAD_W // 4
LANES      = [ROAD_LEFT + LANE_W * i + LANE_W // 2 for i in range(4)]

# Difficulty presets  {name: (enemy_interval, obstacle_interval, base_speed)}
DIFF = {
    "easy":   (120, 180, 4),
    "normal": (90,  130, 5),
    "hard":   (60,  90,  7),
}

# Weighted coin tiers (same as Practice 11)
COIN_TIERS = [
    ("bronze", BRONZE_C, 10, 1,  5,  60),
    ("silver", SILVER_C, 13, 3,  15, 30),
    ("gold",   GOLD_C,   16, 5,  30, 10),
]


# ─────────────────────────────────────────────
#  ASPHALT TEXTURE
# ─────────────────────────────────────────────
def make_asphalt_tile(w, h):
    surf = pygame.Surface((w, h))
    surf.fill(ASPHALT)
    rng = random.Random(42)
    for _ in range(w * h // 7):
        x = rng.randint(0, w - 1)
        y = rng.randint(0, h - 1)
        v = rng.randint(-10, 10)
        c = tuple(max(0, min(255, ASPHALT[i] + v)) for i in range(3))
        surf.set_at((x, y), c)
    return surf


# ─────────────────────────────────────────────
#  PLAYER CAR
# ─────────────────────────────────────────────
class PlayerCar(pygame.sprite.Sprite):
    W, H = 48, 88

    def __init__(self, body_color):
        super().__init__()
        self.body_color = body_color
        self.image      = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        self._draw()
        self.rect        = self.image.get_rect()
        self.rect.centerx = LANES[1]
        self.rect.bottom  = SH - 30
        self.base_speed   = 5
        self.speed        = 5

    def _draw(self):
        s, W, H = self.image, self.W, self.H
        c = self.body_color

        # Shadow
        sh = pygame.Surface((W - 6, H - 10), pygame.SRCALPHA)
        sh.fill((0, 0, 0, 55))
        s.blit(sh, (3, 8))

        # Tyres
        for tx, ty, tw, th in [(0,8,10,18),(W-10,8,10,18),(0,H-26,10,18),(W-10,H-26,10,18)]:
            pygame.draw.rect(s, (22, 22, 22), (tx, ty, tw, th), border_radius=3)
            pygame.draw.rect(s, (155, 155, 170), (tx+2, ty+4, tw-4, th-8), border_radius=2)

        # Body
        pygame.draw.rect(s, c, (8, 4, W-16, H-8), border_radius=10)

        # Specular
        hi = pygame.Surface((8, H-20), pygame.SRCALPHA)
        hi.fill((255, 255, 255, 22))
        s.blit(hi, (W//2-4, 10))

        # Hood crease
        pygame.draw.line(s, MERC_SHINE, (16, 6),   (16, 30),   1)
        pygame.draw.line(s, MERC_SHINE, (W-16, 6), (W-16, 30), 1)

        # Windshield
        pygame.draw.rect(s, MERC_GLASS, (11, 12, W-22, 18), border_radius=4)
        pygame.draw.line(s, c, (14, 22), (W-14, 22), 1)

        # Rear window
        pygame.draw.rect(s, MERC_GLASS, (11, H-30, W-22, 14), border_radius=4)

        # Side windows
        pygame.draw.rect(s, MERC_GLASS, (8,    34, 5, 22), border_radius=2)
        pygame.draw.rect(s, MERC_GLASS, (W-13, 34, 5, 22), border_radius=2)

        # LED strips
        for lx in (10, W-18):
            pygame.draw.rect(s, LED_WHITE, (lx, 5, 8, 4), border_radius=1)
        pygame.draw.rect(s, LED_WHITE, (11, 4, W-22, 2))
        for lx in (10, W-18):
            pygame.draw.rect(s, LED_RED, (lx, H-9, 8, 4), border_radius=1)
        pygame.draw.rect(s, (180, 20, 20), (11, H-8, W-22, 2))

        # Mercedes star
        cx2, cy2, r = W//2, 9, 5
        for i in range(3):
            a = math.radians(i * 120 - 90)
            pygame.draw.line(s, SILVER_C, (cx2, cy2),
                             (int(cx2 + r*math.cos(a)), int(cy2 + r*math.sin(a))), 2)
        pygame.draw.circle(s, SILVER_C, (cx2, cy2), r, 1)
        pygame.draw.rect(s, SILVER_C, (W//2-6, H-11, 12, 3), border_radius=1)

    def update(self, keys):
        if keys[pygame.K_LEFT]:  self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]: self.rect.x += self.speed
        if keys[pygame.K_UP]:    self.rect.y -= self.speed
        if keys[pygame.K_DOWN]:  self.rect.y += self.speed
        self.rect.left   = max(ROAD_LEFT + 4,  self.rect.left)
        self.rect.right  = min(ROAD_RIGHT - 4, self.rect.right)
        self.rect.top    = max(0,               self.rect.top)
        self.rect.bottom = min(SH,              self.rect.bottom)


# ─────────────────────────────────────────────
#  ENEMY CAR  (traffic)
# ─────────────────────────────────────────────
class EnemyCar(pygame.sprite.Sprite):
    W, H = 48, 88

    def __init__(self, speed, player_rect=None):
        super().__init__()
        self.image = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        self.color = random.choice(ENEMY_PALETTES)
        self.shape = random.choice(["sedan", "suv"])
        self._draw()
        # Safe spawn: never directly above player
        self.rect = self.image.get_rect()
        lane = self._safe_lane(player_rect)
        self.rect.centerx = LANES[lane]
        self.rect.bottom   = -10
        self.speed = speed

    def _safe_lane(self, player_rect):
        lanes = list(range(4))
        if player_rect:
            for i, lx in enumerate(LANES):
                if abs(lx - player_rect.centerx) < LANE_W:
                    lanes = [l for l in lanes if l != i]
        return random.choice(lanes) if lanes else random.randint(0, 3)

    def _draw(self):
        s, W, H, c = self.image, self.W, self.H, self.color
        for tx, ty, tw, th in [(0,8,10,18),(W-10,8,10,18),(0,H-26,10,18),(W-10,H-26,10,18)]:
            pygame.draw.rect(s, (22,22,22), (tx,ty,tw,th), border_radius=3)
            pygame.draw.rect(s, (140,140,155), (tx+2,ty+4,tw-4,th-8), border_radius=2)
        if self.shape == "sedan":
            pygame.draw.rect(s, c, (8, 4, W-16, H-8), border_radius=9)
            pygame.draw.rect(s, (160,210,240), (11,12,W-22,16), border_radius=4)
            pygame.draw.rect(s, (160,210,240), (11,H-28,W-22,12), border_radius=4)
        else:
            pygame.draw.rect(s, c, (7, 3, W-14, H-6), border_radius=5)
            dc = tuple(max(0, x-45) for x in c)
            pygame.draw.rect(s, dc, (12, 5, W-24, 3))
            pygame.draw.rect(s, dc, (12,10, W-24, 3))
            pygame.draw.rect(s, (160,210,240), (10,15,W-20,20), border_radius=3)
            pygame.draw.rect(s, (160,210,240), (10,H-32,W-20,16), border_radius=3)
        for lx in (10, W-18):
            pygame.draw.rect(s, LED_RED, (lx, 5, 8, 4), border_radius=1)
        pygame.draw.rect(s, (200,20,20), (11, 4, W-22, 2))
        for lx in (10, W-18):
            pygame.draw.rect(s, LED_WHITE, (lx, H-9, 8, 4), border_radius=1)

    def update(self, *args):
        self.rect.y += self.speed
        if self.rect.top > SH:
            self.kill()


# ─────────────────────────────────────────────
#  WEIGHTED COIN  (same as Practice 11)
# ─────────────────────────────────────────────
class Coin(pygame.sprite.Sprite):
    def __init__(self, road_speed):
        super().__init__()
        weights   = [t[5] for t in COIN_TIERS]
        tier      = random.choices(COIN_TIERS, weights=weights, k=1)[0]
        name, colour, radius, self.coin_value, self.score_value, _ = tier
        self.tier     = name
        self._radius  = radius
        self._colour  = colour
        self._base    = self._make_surf(radius, colour)
        self.image    = self._base.copy()
        self.rect     = self.image.get_rect()
        self.rect.centerx = random.choice(LANES)
        self.rect.bottom   = -10
        self.road_speed    = road_speed
        self._phase        = random.uniform(0, 2 * math.pi)

    @staticmethod
    def _make_surf(radius, colour):
        size = radius * 2 + 6
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        cx = cy = size // 2
        rim = tuple(max(0, c - 40) for c in colour)
        pygame.draw.circle(surf, rim,    (cx, cy), radius)
        pygame.draw.circle(surf, colour, (cx, cy), radius - 2)
        hi = tuple(min(255, c + 60) for c in colour)
        pygame.draw.circle(surf, hi, (cx - radius//4, cy - radius//4), radius // 3)
        return surf

    def update(self, *args):
        self.rect.y += self.road_speed
        if self.rect.top > SH:
            self.kill(); return
        t     = pygame.time.get_ticks() / 1000.0
        scale = 1.0 + 0.12 * math.sin(t * 4 + self._phase)
        r     = max(1, int(self._radius * scale))
        self.image = self._make_surf(r, self._colour)
        cx, cy = self.rect.center
        self.rect  = self.image.get_rect(center=(cx, cy))


# ─────────────────────────────────────────────
#  POWER-UP
# ─────────────────────────────────────────────
POWERUP_DEFS = {
    "nitro":  {"color": (255, 80,  0),   "label": "N", "duration": 4.0},
    "shield": {"color": (0,   180, 255), "label": "S", "duration": 0},    # until hit
    "repair": {"color": (0,   220, 80),  "label": "R", "duration": 0},    # instant
}
POWERUP_TIMEOUT = 7.0   # seconds before power-up disappears


class PowerUp(pygame.sprite.Sprite):
    RADIUS = 18

    def __init__(self, kind, road_speed, player_rect=None):
        super().__init__()
        self.kind       = kind
        self.road_speed = road_speed
        self.spawned_at = pygame.time.get_ticks() / 1000.0

        r    = self.RADIUS
        size = r * 2 + 4
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        col = POWERUP_DEFS[kind]["color"]
        pygame.draw.circle(self.image, col,           (r+2, r+2), r)
        pygame.draw.circle(self.image, WHITE,         (r+2, r+2), r, 2)
        font = pygame.font.SysFont("arial", 20, bold=True)
        lbl  = font.render(POWERUP_DEFS[kind]["label"], True, WHITE)
        self.image.blit(lbl, lbl.get_rect(center=(r+2, r+2)))

        self.rect = self.image.get_rect()
        self.rect.centerx = random.choice(LANES)
        self.rect.bottom   = -10

    def update(self, *args):
        self.rect.y += self.road_speed
        if self.rect.top > SH:
            self.kill(); return
        # Timeout
        age = pygame.time.get_ticks() / 1000.0 - self.spawned_at
        if age > POWERUP_TIMEOUT:
            self.kill()


# ─────────────────────────────────────────────
#  LANE HAZARD  (oil spill / speed bump / nitro strip)
# ─────────────────────────────────────────────
HAZARD_TYPES = ["oil", "bump", "nitro_strip"]


class LaneHazard(pygame.sprite.Sprite):
    def __init__(self, road_speed, player_rect=None):
        super().__init__()
        self.htype      = random.choice(HAZARD_TYPES)
        self.road_speed = road_speed

        w, h = LANE_W - 10, 28
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)

        if self.htype == "oil":
            pygame.draw.ellipse(self.image, (20, 20, 40, 200), (0, 0, w, h))
            pygame.draw.ellipse(self.image, (80, 60, 120, 150), (4, 4, w-8, h-8))
            lbl = pygame.font.SysFont("arial", 13, bold=True).render("OIL", True, (150,100,255))
            self.image.blit(lbl, lbl.get_rect(center=(w//2, h//2)))
        elif self.htype == "bump":
            pygame.draw.rect(self.image, (180, 140, 60), (0, 6, w, 16), border_radius=4)
            pygame.draw.rect(self.image, (220, 180, 80), (0, 6, w, 8), border_radius=4)
            lbl = pygame.font.SysFont("arial", 11, bold=True).render("BUMP", True, BLACK)
            self.image.blit(lbl, lbl.get_rect(center=(w//2, h//2)))
        else:  # nitro_strip
            pygame.draw.rect(self.image, (255, 80, 0, 180), (0, 0, w, h), border_radius=4)
            lbl = pygame.font.SysFont("arial", 13, bold=True).render("NITRO", True, WHITE)
            self.image.blit(lbl, lbl.get_rect(center=(w//2, h//2)))

        self.rect = self.image.get_rect()
        lane = random.randint(0, 3)
        self.rect.centerx = LANES[lane]
        self.rect.bottom   = -10

    def update(self, *args):
        self.rect.y += self.road_speed
        if self.rect.top > SH:
            self.kill()


# ─────────────────────────────────────────────
#  ROAD OBSTACLE  (barrier / pothole)
# ─────────────────────────────────────────────
class RoadObstacle(pygame.sprite.Sprite):
    def __init__(self, road_speed, player_rect=None):
        super().__init__()
        self.otype      = random.choice(["barrier", "pothole"])
        self.road_speed = road_speed

        if self.otype == "barrier":
            w, h = 54, 22
            self.image = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (220, 60, 60), (0, 4, w, h-8), border_radius=4)
            for bx in range(0, w, 14):
                pygame.draw.rect(self.image, WHITE, (bx, 4, 7, h-8))
        else:  # pothole
            w = h = 36
            self.image = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.ellipse(self.image, (25, 20, 20, 230), (2, 2, w-4, h-4))
            pygame.draw.ellipse(self.image, (60, 50, 50, 180), (6, 6, w-12, h-12))

        self.rect = self.image.get_rect()
        lane = self._safe_lane(player_rect)
        self.rect.centerx = LANES[lane]
        self.rect.bottom   = -10

    def _safe_lane(self, player_rect):
        lanes = list(range(4))
        if player_rect:
            for i, lx in enumerate(LANES):
                if abs(lx - player_rect.centerx) < LANE_W:
                    lanes = [l for l in lanes if l != i]
        return random.choice(lanes) if lanes else random.randint(0, 3)

    def update(self, *args):
        self.rect.y += self.road_speed
        if self.rect.top > SH:
            self.kill()


# ─────────────────────────────────────────────
#  SCENERY
# ─────────────────────────────────────────────
class Building:
    def __init__(self, speed, y=None):
        self.w     = random.randint(28, 55)
        self.h     = random.randint(60, 160)
        self.x     = random.randint(2, max(2, ROAD_LEFT - self.w - 4))
        self.y     = y if y is not None else random.randint(-200, SH)
        self.color = random.choice(BUILDING_COLORS)
        self.speed = speed
        self.wins  = [(random.randint(5, self.w-11), random.randint(8, self.h-16),
                       random.random() > 0.4)
                      for _ in range(random.randint(4, 10))]

    def update(self, speed):
        self.y += speed
        if self.y > SH:
            self.__init__(speed)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.w, self.h))
        edge = tuple(min(255, v+20) for v in self.color)
        pygame.draw.rect(surface, edge, (self.x, self.y, self.w, self.h), 1)
        for wx, wy, lit in self.wins:
            wc = (255,240,150) if lit else (30,30,40)
            pygame.draw.rect(surface, wc, (self.x+wx, self.y+wy, 6, 8))


class Tree:
    def __init__(self, speed, y=None):
        self.x = random.randint(ROAD_RIGHT + 6, SW - 16)
        self.r = random.randint(12, 22)
        self.y = y if y is not None else random.randint(-self.r, SH)

    def update(self, speed):
        self.y += speed
        if self.y - self.r > SH:
            self.__init__(speed)

    def draw(self, surface):
        pygame.draw.rect(surface, (90, 55, 20), (self.x-3, self.y, 6, self.r))
        pygame.draw.circle(surface, GRASS_D, (self.x, self.y), self.r)
        pygame.draw.circle(surface, GRASS_L, (self.x-4, self.y-4), max(1, self.r-4))


class LaneDash:
    def __init__(self, x, y):
        self.x = x; self.y = y

    def update(self, speed):
        self.y += speed
        if self.y > SH:
            self.y -= SH + 50

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, (self.x-3, self.y, 6, 38), border_radius=2)


# ─────────────────────────────────────────────
#  MAIN GAME CLASS
# ─────────────────────────────────────────────
class RacerGame:
    def __init__(self, screen, clock, player_name, settings):
        self.screen      = screen
        self.clock       = clock
        self.player_name = player_name
        self.settings    = settings

        diff = settings.get("difficulty", "normal")
        self.enemy_interval_base, self.obs_interval_base, base_speed = DIFF[diff]
        self.base_speed = base_speed

        body_color = tuple(settings.get("car_color", [28, 32, 38]))
        self.asphalt = make_asphalt_tile(ROAD_W, SH)

        self.font_med   = pygame.font.SysFont("arial", 22, bold=True)
        self.font_small = pygame.font.SysFont("arial", 17)
        self.font_tiny  = pygame.font.SysFont("arial", 14)

        self._init(body_color)

    def _init(self, body_color=None):
        if body_color is None:
            body_color = tuple(self.settings.get("car_color", [28, 32, 38]))

        self.all_sprites    = pygame.sprite.Group()
        self.enemy_group    = pygame.sprite.Group()
        self.coin_group     = pygame.sprite.Group()
        self.powerup_group  = pygame.sprite.Group()
        self.hazard_group   = pygame.sprite.Group()
        self.obstacle_group = pygame.sprite.Group()

        self.player = PlayerCar(body_color)
        self.all_sprites.add(self.player)

        self.dashes    = [LaneDash(ROAD_LEFT + LANE_W * i, sy)
                          for i in range(1, 4) for sy in range(0, SH, 68)]
        self.buildings = [Building(self.base_speed) for _ in range(7)]
        self.trees     = [Tree(self.base_speed)     for _ in range(9)]
        self.road_offset = 0

        # Timers
        self.enemy_timer   = 0
        self.coin_timer    = 0
        self.hazard_timer  = 0
        self.obs_timer     = 0
        self.powerup_timer = 0

        self.enemy_interval   = self.enemy_interval_base
        self.obs_interval     = self.obs_interval_base
        self.hazard_interval  = 150
        self.coin_interval    = 110
        self.powerup_interval = 300

        # State
        self.road_speed  = self.base_speed
        self.enemy_speed = self.base_speed
        self.score       = 0
        self.coins       = 0
        self.distance    = 0
        self.level       = 1
        self.game_over   = False
        self.paused      = False

        # Power-up state
        self.active_powerup      = None   # "nitro" | "shield" | "repair" | None
        self.powerup_end_time    = 0.0
        self.shield_active       = False
        self.nitro_active        = False

        # Flash messages
        self.flash_msg   = ""
        self.flash_timer = 0

        # Coins since last enemy speed-up (Practice 11 mechanic kept)
        self.coins_at_last_speedup = 0

    # ── Run (returns "retry" | "menu") ───────────────────────────────────
    def run(self):
        from ui import GameOverScreen
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self._handle_events()
            if not self.game_over and not self.paused:
                self._update(dt)
            self._draw()
            if self.game_over:
                save_score(self.player_name, self.score, self.distance, self.coins)
                return GameOverScreen().run(
                    self.screen, self.clock,
                    self.score, self.distance, self.coins, self.player_name
                )

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    self.paused = not self.paused

    # ── Update ───────────────────────────────────────────────────────────
    def _update(self, dt):
        keys = pygame.key.get_pressed()

        # Nitro speed boost
        if self.nitro_active:
            self.player.speed = self.player.base_speed + 4
        else:
            self.player.speed = self.player.base_speed

        self.player.update(keys)
        self.road_offset = (self.road_offset + self.road_speed) % SH

        for d in self.dashes:    d.update(self.road_speed)
        for b in self.buildings: b.update(self.road_speed)
        for t in self.trees:     t.update(self.road_speed)

        self.distance += 1

        # ── Spawning ─────────────────────────────────────────────────
        self.enemy_timer += 1
        if self.enemy_timer >= self.enemy_interval:
            e = EnemyCar(self.enemy_speed, self.player.rect)
            self.enemy_group.add(e); self.all_sprites.add(e)
            self.enemy_timer = 0

        self.coin_timer += 1
        if self.coin_timer >= self.coin_interval:
            c = Coin(self.road_speed)
            self.coin_group.add(c); self.all_sprites.add(c)
            self.coin_timer = 0

        self.hazard_timer += 1
        if self.hazard_timer >= self.hazard_interval:
            h = LaneHazard(self.road_speed, self.player.rect)
            self.hazard_group.add(h); self.all_sprites.add(h)
            self.hazard_timer = 0

        self.obs_timer += 1
        if self.obs_timer >= self.obs_interval:
            o = RoadObstacle(self.road_speed, self.player.rect)
            self.obstacle_group.add(o); self.all_sprites.add(o)
            self.obs_timer = 0

        self.powerup_timer += 1
        if self.powerup_timer >= self.powerup_interval:
            # Only one power-up on screen at a time
            if len(self.powerup_group) == 0:
                kind = random.choice(["nitro", "shield", "repair"])
                pu   = PowerUp(kind, self.road_speed, self.player.rect)
                self.powerup_group.add(pu); self.all_sprites.add(pu)
            self.powerup_timer = 0

        # ── Update all sprites ────────────────────────────────────────
        self.enemy_group.update()
        self.coin_group.update()
        self.hazard_group.update()
        self.obstacle_group.update()
        self.powerup_group.update()

        # ── Collisions ───────────────────────────────────────────────
        # Enemy collision
        if pygame.sprite.spritecollideany(self.player, self.enemy_group):
            if self.shield_active:
                self.shield_active  = False
                self.active_powerup = None
                # Kill the enemy car
                hits = pygame.sprite.spritecollide(self.player, self.enemy_group, True)
                self.flash_msg   = "🛡 Shield absorbed the hit!"
                self.flash_timer = 120
            else:
                self.game_over = True

        # Obstacle collision
        hit_obs = pygame.sprite.spritecollide(self.player, self.obstacle_group, False)
        if hit_obs:
            if self.shield_active:
                self.shield_active  = False
                self.active_powerup = None
                for o in hit_obs: o.kill()
                self.flash_msg   = "🛡 Shield blocked obstacle!"
                self.flash_timer = 120
            else:
                self.game_over = True

        # Hazard collision
        hit_haz = pygame.sprite.spritecollide(self.player, self.hazard_group, True)
        for h in hit_haz:
            if h.htype == "oil":
                # Slow down briefly
                self.player.speed = max(2, self.player.base_speed - 2)
                self.flash_msg   = "🛢 Oil spill! Slowing down..."
                self.flash_timer = 90
            elif h.htype == "bump":
                self.score       = max(0, self.score - 10)
                self.flash_msg   = "🚧 Speed bump! -10 score"
                self.flash_timer = 90
            elif h.htype == "nitro_strip":
                self._activate_powerup("nitro")

        # Coin collision
        collected = pygame.sprite.spritecollide(self.player, self.coin_group, True)
        for coin in collected:
            self.coins += coin.coin_value
            self.score += coin.score_value

        # Power-up collision
        pu_hits = pygame.sprite.spritecollide(self.player, self.powerup_group, True)
        for pu in pu_hits:
            self._activate_powerup(pu.kind)

        # ── Power-up timer expiry ─────────────────────────────────────
        now = pygame.time.get_ticks() / 1000.0
        if self.nitro_active and now >= self.powerup_end_time:
            self.nitro_active   = False
            self.active_powerup = None

        # ── Difficulty scaling ────────────────────────────────────────
        # Every 500 distance units → faster, more spawns
        if self.distance % 500 == 0 and self.distance > 0:
            self.road_speed      = min(self.road_speed + 1, 16)
            self.enemy_speed     = min(self.enemy_speed + 1, 18)
            self.enemy_interval  = max(35, self.enemy_interval - 5)
            self.obs_interval    = max(60, self.obs_interval   - 5)
            self.hazard_interval = max(80, self.hazard_interval - 5)
            self.level          += 1
            self.flash_msg       = f"⬆ Level {self.level}! Speed up!"
            self.flash_timer     = 120

        # Practice 11: enemy speed-up every 5 coin units
        if self.coins - self.coins_at_last_speedup >= 5:
            self.coins_at_last_speedup = self.coins
            self.enemy_speed = min(self.enemy_speed + 1, 18)
            for e in self.enemy_group:
                e.speed = self.enemy_speed

        # Passive score
        self.score += 1

        if self.flash_timer > 0:
            self.flash_timer -= 1

    def _activate_powerup(self, kind):
        now = pygame.time.get_ticks() / 1000.0
        self.active_powerup = kind
        if kind == "nitro":
            self.nitro_active    = True
            self.shield_active   = False
            self.powerup_end_time = now + POWERUP_DEFS["nitro"]["duration"]
            self.flash_msg   = "⚡ NITRO! Speed boost!"
            self.flash_timer = 90
        elif kind == "shield":
            self.shield_active = True
            self.nitro_active  = False
            self.score        += 20
            self.flash_msg    = "🛡 Shield active!"
            self.flash_timer  = 90
        elif kind == "repair":
            self.active_powerup = None
            self.score         += 30
            # Clear all obstacles from screen
            self.obstacle_group.empty()
            self.flash_msg   = "🔧 Repair! Obstacles cleared! +30"
            self.flash_timer = 120

    # ── Draw ─────────────────────────────────────────────────────────────
    def _draw(self):
        # Left: city pavement
        self.screen.fill((105, 98, 88))
        tile_h = 40
        for ty in range(-tile_h, SH + tile_h, tile_h):
            oty = (ty + self.road_offset) % (SH + tile_h) - tile_h
            pygame.draw.line(self.screen, CURB_C, (0, oty), (ROAD_LEFT, oty), 1)
        for tx in range(0, ROAD_LEFT, 20):
            pygame.draw.line(self.screen, CURB_C, (tx, 0), (tx, SH), 1)
        for b in self.buildings: b.draw(self.screen)

        # Right: grass
        pygame.draw.rect(self.screen, GRASS_D, (ROAD_RIGHT, 0, SW - ROAD_RIGHT, SH))
        for t in self.trees: t.draw(self.screen)

        # Asphalt
        self.screen.blit(self.asphalt, (ROAD_LEFT, self.road_offset - SH))
        self.screen.blit(self.asphalt, (ROAD_LEFT, self.road_offset))

        # Road edges
        pygame.draw.rect(self.screen, (215,185,0), (ROAD_LEFT-6, 0, 6, SH))
        pygame.draw.rect(self.screen, WHITE,        (ROAD_RIGHT,  0, 5, SH))

        for d in self.dashes: d.draw(self.screen)

        # Sprites (draw order: hazards, coins, obstacles, power-ups, enemies, player)
        self.hazard_group.draw(self.screen)
        self.coin_group.draw(self.screen)
        self.obstacle_group.draw(self.screen)
        self.powerup_group.draw(self.screen)
        self.enemy_group.draw(self.screen)

        # Shield glow around player
        if self.shield_active:
            t    = pygame.time.get_ticks() / 1000.0
            alpha = int(140 + 80 * math.sin(t * 6))
            glow  = pygame.Surface((self.player.W + 16, self.player.H + 16), pygame.SRCALPHA)
            pygame.draw.ellipse(glow, (0, 180, 255, alpha), glow.get_rect(), 4)
            self.screen.blit(glow, (self.player.rect.x - 8, self.player.rect.y - 8))

        self.screen.blit(self.player.image, self.player.rect)

        self._draw_hud()

        if self.flash_timer > 0:
            alpha = min(255, self.flash_timer * 5)
            fs    = self.font_med.render(self.flash_msg, True, (255, 230, 80))
            fs.set_alpha(alpha)
            self.screen.blit(fs, fs.get_rect(center=(SW // 2, 90)))

        if self.paused:
            self._draw_overlay("PAUSED", "P — resume")

        pygame.display.flip()

    def _draw_hud(self):
        # Left pill
        pill = pygame.Surface((185, 85), pygame.SRCALPHA)
        pill.fill((0, 0, 0, 120))
        self.screen.blit(pill, (4, 4))

        self.screen.blit(self.font_med.render(f"Score:  {self.score}",    True, WHITE),         (10, 8))
        self.screen.blit(self.font_med.render(f"Level:  {self.level}",    True, (170,215,255)), (10, 34))
        self.screen.blit(self.font_small.render(f"Dist: {self.distance}m",True, (160,220,160)), (10, 62))

        # Coin counter top-right
        cs = self.font_med.render(str(self.coins), True, GOLD_C)
        cr = cs.get_rect(topright=(SW - 14, 12))
        self.screen.blit(cs, cr)
        ix, iy = cr.left - 18, cr.centery
        pygame.draw.circle(self.screen, GOLD_C,       (ix, iy), 12)
        pygame.draw.circle(self.screen, (195,150,0),  (ix, iy), 12, 2)
        lbl = self.font_small.render("$", True, (120, 80, 0))
        self.screen.blit(lbl, lbl.get_rect(center=(ix, iy)))

        # Active power-up HUD
        if self.active_powerup:
            now  = pygame.time.get_ticks() / 1000.0
            col  = POWERUP_DEFS[self.active_powerup]["color"]
            text = self.active_powerup.upper()
            if self.nitro_active:
                remaining = max(0, self.powerup_end_time - now)
                text = f"NITRO {remaining:.1f}s"
            elif self.shield_active:
                text = "SHIELD active"
            pu_s = self.font_small.render(f"⚡ {text}", True, col)
            pygame.draw.rect(self.screen, (0, 0, 0, 140),
                             (SW//2 - pu_s.get_width()//2 - 8, 8,
                              pu_s.get_width() + 16, 28))
            self.screen.blit(pu_s, pu_s.get_rect(center=(SW // 2, 22)))

        # Hint
        hint = self.font_tiny.render("P=Pause  Arrow keys=Drive", True, (100,100,100))
        self.screen.blit(hint, (ROAD_LEFT + 4, SH - 18))

    def _draw_overlay(self, title, sub):
        o = pygame.Surface((SW, SH), pygame.SRCALPHA)
        o.fill((0, 0, 0, 160))
        self.screen.blit(o, (0, 0))
        font_big = pygame.font.SysFont("arial", 44, bold=True)
        font_sm  = pygame.font.SysFont("arial", 22)
        t = font_big.render(title, True, WHITE)
        self.screen.blit(t, t.get_rect(center=(SW//2, SH//2 - 30)))
        s = font_sm.render(sub, True, (200, 200, 200))
        self.screen.blit(s, s.get_rect(center=(SW//2, SH//2 + 20)))