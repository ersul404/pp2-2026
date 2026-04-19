"""
=============================================================
  RACER GAME — Practice 11 (extends Practice 10 Mercedes)
  NEW features for Practice 11:
    1. Randomly generated coins with DIFFERENT WEIGHTS
       - Bronze  (common,   weight=60) → +1  coin,  +5  score
       - Silver  (uncommon, weight=30) → +3  coins, +15 score
       - Gold    (rare,     weight=10) → +5  coins, +30 score
       Each coin type has a unique size, colour and label.
    2. Enemy speed INCREASES every N=5 collected coins
       (separate from the passive level system).
       A flash message is shown on screen when it triggers.
    3. Fully commented code
=============================================================
"""

import pygame
import random
import sys
import math

# ─────────────────────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────────────────────
SCREEN_WIDTH  = 600
SCREEN_HEIGHT = 700
FPS           = 60

# Road geometry
ROAD_LEFT  = 80
ROAD_RIGHT = 480
ROAD_W     = ROAD_RIGHT - ROAD_LEFT   # 400 px total road width
LANE_W     = ROAD_W // 4              # 4 equal lanes
LANES      = [ROAD_LEFT + LANE_W * i + LANE_W // 2 for i in range(4)]

# Basic colours
WHITE      = (255, 255, 255)
BLACK      = (0,   0,   0)
ASPHALT    = (50,  52,  55)
GOLD_C     = (255, 185, 0)
SILVER_C   = (192, 192, 210)
BRONZE_C   = (180, 100, 30)
GRASS_D    = (34,  90,  34)
GRASS_L    = (45,  120, 45)
CURB       = (210, 200, 185)

# Mercedes body colours
MERC_BODY  = (28,  32,  38)
MERC_SHINE = (60,  70,  80)
MERC_GLASS = (140, 200, 230)
LED_WHITE  = (230, 240, 255)
LED_RED    = (255, 60,  60)

BUILDING_COLORS = [
    (60, 65, 80), (75, 70, 85), (55, 75, 90),
    (80, 60, 60), (65, 80, 65), (90, 80, 55),
]
ENEMY_PALETTES = [
    (200, 30,  30), (30, 160, 30), (255, 140, 0),
    (160, 0,  160), (0, 140, 200), (200, 200, 50),
]

# ── Coin weight table ──────────────────────────────────────────
# Each entry: (tier_name, colour, radius, coin_value, score_value, spawn_weight)
# spawn_weight is used in random.choices() — higher = more common
COIN_TIERS = [
    ("bronze", BRONZE_C, 10, 1,  5,  60),   # common
    ("silver", SILVER_C, 13, 3,  15, 30),   # uncommon
    ("gold",   GOLD_C,   16, 5,  30, 10),   # rare
]

# Every N coins collected, enemy speed increases
ENEMY_SPEED_UP_EVERY = 5


# ─────────────────────────────────────────────────────────────
#  ASPHALT TEXTURE (pre-rendered once)
# ─────────────────────────────────────────────────────────────
def make_asphalt_tile(w, h):
    """
    Generate a static asphalt-like surface using fixed-seed noise.
    Blit twice with a scrolling offset to create seamless movement.
    """
    surf = pygame.Surface((w, h))
    surf.fill(ASPHALT)
    rng = random.Random(42)          # fixed seed → same texture every run
    for _ in range(w * h // 7):
        x = rng.randint(0, w - 1)
        y = rng.randint(0, h - 1)
        v = rng.randint(-10, 10)     # small brightness variation
        c = tuple(max(0, min(255, ASPHALT[i] + v)) for i in range(3))
        surf.set_at((x, y), c)
    return surf


# ─────────────────────────────────────────────────────────────
#  PLAYER CAR  (Mercedes top-down style)
# ─────────────────────────────────────────────────────────────
class PlayerCar(pygame.sprite.Sprite):
    """
    Player-controlled car drawn to resemble a top-down Mercedes.
    Moves with arrow keys, clamped inside road boundaries.
    """
    W, H = 48, 88

    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        self._draw()
        self.rect = self.image.get_rect()
        self.rect.centerx = LANES[1]          # start in 2nd lane from left
        self.rect.bottom   = SCREEN_HEIGHT - 30
        self.speed = 5                         # pixels per frame

    def _draw(self):
        """Paint all car parts onto self.image."""
        s, W, H = self.image, self.W, self.H

        # Drop shadow (semi-transparent dark rectangle)
        sh = pygame.Surface((W - 6, H - 10), pygame.SRCALPHA)
        sh.fill((0, 0, 0, 55))
        s.blit(sh, (3, 8))

        # Tyres (four corners)
        for tx, ty, tw, th in [(0,8,10,18),(W-10,8,10,18),(0,H-26,10,18),(W-10,H-26,10,18)]:
            pygame.draw.rect(s, (22, 22, 22), (tx, ty, tw, th), border_radius=3)
            pygame.draw.rect(s, (155, 155, 170), (tx+2, ty+4, tw-4, th-8), border_radius=2)

        # Main body
        pygame.draw.rect(s, MERC_BODY, (8, 4, W-16, H-8), border_radius=10)

        # Centre specular highlight
        hi = pygame.Surface((8, H-20), pygame.SRCALPHA)
        hi.fill((255, 255, 255, 22))
        s.blit(hi, (W//2-4, 10))

        # Hood crease lines
        pygame.draw.line(s, MERC_SHINE, (16, 6),   (16, 30),   1)
        pygame.draw.line(s, MERC_SHINE, (W-16, 6), (W-16, 30), 1)

        # Windshield + wiper line
        pygame.draw.rect(s, MERC_GLASS, (11, 12, W-22, 18), border_radius=4)
        pygame.draw.line(s, MERC_BODY, (14, 22), (W-14, 22), 1)

        # Rear window
        pygame.draw.rect(s, MERC_GLASS, (11, H-30, W-22, 14), border_radius=4)

        # Side windows
        pygame.draw.rect(s, MERC_GLASS, (8,    34, 5, 22), border_radius=2)
        pygame.draw.rect(s, MERC_GLASS, (W-13, 34, 5, 22), border_radius=2)

        # Front LED strip
        for lx in (10, W-18):
            pygame.draw.rect(s, LED_WHITE, (lx, 5, 8, 4), border_radius=1)
        pygame.draw.rect(s, LED_WHITE, (11, 4, W-22, 2))

        # Rear tail-light strip
        for lx in (10, W-18):
            pygame.draw.rect(s, LED_RED, (lx, H-9, 8, 4), border_radius=1)
        pygame.draw.rect(s, (180, 20, 20), (11, H-8, W-22, 2))

        # Three-pointed Mercedes star (hood ornament)
        cx, cy, r = W//2, 9, 5
        for i in range(3):
            a = math.radians(i * 120 - 90)
            pygame.draw.line(s, SILVER_C,
                             (cx, cy),
                             (int(cx + r*math.cos(a)), int(cy + r*math.sin(a))), 2)
        pygame.draw.circle(s, SILVER_C, (cx, cy), r, 1)

        # Boot badge
        pygame.draw.rect(s, SILVER_C, (W//2-6, H-11, 12, 3), border_radius=1)

    def update(self, keys):
        """Move with arrow keys; stay within road edges."""
        if keys[pygame.K_LEFT]:  self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]: self.rect.x += self.speed
        if keys[pygame.K_UP]:    self.rect.y -= self.speed
        if keys[pygame.K_DOWN]:  self.rect.y += self.speed
        # Clamp to road area
        self.rect.left   = max(ROAD_LEFT + 4,  self.rect.left)
        self.rect.right  = min(ROAD_RIGHT - 4, self.rect.right)
        self.rect.top    = max(0,               self.rect.top)
        self.rect.bottom = min(SCREEN_HEIGHT,   self.rect.bottom)


# ─────────────────────────────────────────────────────────────
#  ENEMY CAR
# ─────────────────────────────────────────────────────────────
class EnemyCar(pygame.sprite.Sprite):
    """
    Oncoming traffic. Spawns above screen in a random lane.
    Two shape variants: sedan (rounded) and SUV (boxy).
    Speed is passed in from the game so it can be increased.
    """
    W, H = 48, 88

    def __init__(self, speed):
        super().__init__()
        self.image = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        self.color = random.choice(ENEMY_PALETTES)
        self.shape = random.choice(["sedan", "suv"])
        self._draw()
        self.rect = self.image.get_rect()
        self.rect.centerx = random.choice(LANES)
        self.rect.bottom   = -10
        self.speed = speed   # pixels per frame (can be updated mid-game)

    def _draw(self):
        s, W, H, c = self.image, self.W, self.H, self.color

        # Tyres
        for tx, ty, tw, th in [(0,8,10,18),(W-10,8,10,18),(0,H-26,10,18),(W-10,H-26,10,18)]:
            pygame.draw.rect(s, (22, 22, 22), (tx, ty, tw, th), border_radius=3)
            pygame.draw.rect(s, (140,140,155), (tx+2, ty+4, tw-4, th-8), border_radius=2)

        if self.shape == "sedan":
            pygame.draw.rect(s, c, (8, 4, W-16, H-8), border_radius=9)
            pygame.draw.rect(s, (160,210,240), (11,12,W-22,16), border_radius=4)
            pygame.draw.rect(s, (160,210,240), (11,H-28,W-22,12), border_radius=4)
            pygame.draw.rect(s, (160,210,240), (8,34,5,20), border_radius=2)
            pygame.draw.rect(s, (160,210,240), (W-13,34,5,20), border_radius=2)
        else:   # boxy SUV
            pygame.draw.rect(s, c, (7, 3, W-14, H-6), border_radius=5)
            dc = tuple(max(0, x-45) for x in c)
            pygame.draw.rect(s, dc, (12, 5, W-24, 3))   # roof rack bar 1
            pygame.draw.rect(s, dc, (12,10, W-24, 3))   # roof rack bar 2
            pygame.draw.rect(s, (160,210,240), (10,15,W-20,20), border_radius=3)
            pygame.draw.rect(s, (160,210,240), (10,H-32,W-20,16), border_radius=3)

        # Tail lights visible at top (enemy comes toward player)
        for lx in (10, W-18):
            pygame.draw.rect(s, LED_RED, (lx, 5, 8, 4), border_radius=1)
        pygame.draw.rect(s, (200,20,20), (11, 4, W-22, 2))

        # Headlights at bottom
        for lx in (10, W-18):
            pygame.draw.rect(s, LED_WHITE, (lx, H-9, 8, 4), border_radius=1)
        pygame.draw.rect(s, (220,230,255), (11, H-8, W-22, 2))

    def update(self, *args):
        """Scroll downward; self-remove when below screen."""
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


# ─────────────────────────────────────────────────────────────
#  WEIGHTED COIN  (Practice 11 — Task 1)
# ─────────────────────────────────────────────────────────────
class Coin(pygame.sprite.Sprite):
    """
    A collectible coin with THREE possible tiers:
      Bronze (common)   → small,  +1 coin,  +5  score
      Silver (uncommon) → medium, +3 coins, +15 score
      Gold   (rare)     → large,  +5 coins, +30 score

    Tier is chosen via weighted random selection so rare coins
    appear less frequently than common ones.
    Each coin pulses (animates scale) to attract attention.
    """

    def __init__(self, road_speed):
        super().__init__()

        # ── Weighted random tier selection ──────────────────────────
        # Unpack the weight column for random.choices()
        weights = [t[5] for t in COIN_TIERS]
        tier    = random.choices(COIN_TIERS, weights=weights, k=1)[0]
        name, colour, radius, self.coin_value, self.score_value, _ = tier
        self.tier = name   # "bronze" / "silver" / "gold"

        # ── Build base image ────────────────────────────────────────
        size = radius * 2 + 4          # surface side length
        self._radius = radius
        self._colour = colour
        self._base   = self._make_surface(radius, colour)
        self.image   = self._base.copy()
        self.rect    = self.image.get_rect()

        # Spawn above screen in a random lane
        self.rect.centerx = random.choice(LANES)
        self.rect.bottom   = -10
        self.road_speed    = road_speed   # scrolls at same speed as road

        # Animation phase (randomised so not all coins pulse together)
        self._phase = random.uniform(0, 2 * math.pi)

    @staticmethod
    def _make_surface(radius, colour):
        """Draw a shiny coin onto a transparent surface."""
        size = radius * 2 + 6
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        cx = cy = size // 2

        # Outer rim (slightly darker)
        rim = tuple(max(0, c - 40) for c in colour)
        pygame.draw.circle(surf, rim,    (cx, cy), radius)
        # Face
        pygame.draw.circle(surf, colour, (cx, cy), radius - 2)
        # Inner highlight
        hi = tuple(min(255, c + 60) for c in colour)
        pygame.draw.circle(surf, hi,     (cx - radius//4, cy - radius//4), radius // 3)
        return surf

    def update(self, *args):
        """Scroll down and pulse in size every frame."""
        self.rect.y += self.road_speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()
            return

        # Pulsing scale animation using a sine wave
        t     = pygame.time.get_ticks() / 1000.0
        scale = 1.0 + 0.15 * math.sin(t * 4 + self._phase)
        r     = max(1, int(self._radius * scale))
        self.image = self._make_surface(r, self._colour)
        cx, cy = self.rect.center
        self.rect  = self.image.get_rect(center=(cx, cy))


# ─────────────────────────────────────────────────────────────
#  SCENERY: Buildings & Trees
# ─────────────────────────────────────────────────────────────
class Building:
    """Scrolling city building on the left side of the road."""

    def __init__(self, speed, y=None):
        self.w     = random.randint(28, 55)
        self.h     = random.randint(60, 160)
        self.x     = random.randint(2, max(2, ROAD_LEFT - self.w - 4))
        self.y     = y if y is not None else random.randint(-200, SCREEN_HEIGHT)
        self.color = random.choice(BUILDING_COLORS)
        self.speed = speed
        # Pre-generate window positions and lit/dark state
        self.wins  = [
            (random.randint(5, self.w - 11), random.randint(8, self.h - 16),
             random.random() > 0.4)
            for _ in range(random.randint(4, 10))
        ]

    def update(self, speed):
        self.speed = speed
        self.y    += speed
        if self.y > SCREEN_HEIGHT:
            self.__init__(speed)   # recycle off-screen buildings

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.w, self.h))
        edge = tuple(min(255, v + 20) for v in self.color)
        pygame.draw.rect(surface, edge, (self.x, self.y, self.w, self.h), 1)
        for wx, wy, lit in self.wins:
            wc = (255, 240, 150) if lit else (30, 30, 40)
            pygame.draw.rect(surface, wc, (self.x + wx, self.y + wy, 6, 8))


class Tree:
    """Scrolling tree on the right-side grass."""

    def __init__(self, speed, y=None):
        self.x = random.randint(ROAD_RIGHT + 6, SCREEN_WIDTH - 16)
        self.r = random.randint(12, 22)
        self.y = y if y is not None else random.randint(-self.r, SCREEN_HEIGHT)

    def update(self, speed):
        self.y += speed
        if self.y - self.r > SCREEN_HEIGHT:
            self.__init__(speed)

    def draw(self, surface):
        pygame.draw.rect(surface, (90, 55, 20), (self.x - 3, self.y, 6, self.r))
        pygame.draw.circle(surface, GRASS_D, (self.x, self.y), self.r)
        pygame.draw.circle(surface, GRASS_L, (self.x - 4, self.y - 4), max(1, self.r - 4))


class LaneDash:
    """One animated dashed white lane-separator line."""

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def update(self, speed):
        self.y += speed
        if self.y > SCREEN_HEIGHT:
            self.y -= SCREEN_HEIGHT + 50   # wrap to top

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, (self.x - 3, self.y, 6, 38), border_radius=2)


# ─────────────────────────────────────────────────────────────
#  GAME
# ─────────────────────────────────────────────────────────────
class RacerGame:
    """
    Main game controller.
    Orchestrates: input, physics, spawning, collision, rendering, HUD.
    """

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Mercedes Racer — Practice 11")
        self.clock  = pygame.time.Clock()

        # Fonts
        self.font_big   = pygame.font.SysFont("arial", 38, bold=True)
        self.font_med   = pygame.font.SysFont("arial", 22, bold=True)
        self.font_small = pygame.font.SysFont("arial", 17)
        self.font_tiny  = pygame.font.SysFont("arial", 14)

        # Pre-render road texture once (expensive, avoid every frame)
        self.asphalt = make_asphalt_tile(ROAD_W, SCREEN_HEIGHT)

        self._init_game()

    # ── Init / Reset ──────────────────────────────────────────────────────
    def _init_game(self):
        """Reset all state for a fresh game."""
        # Sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.enemy_group = pygame.sprite.Group()
        self.coin_group  = pygame.sprite.Group()

        # Player
        self.player = PlayerCar()
        self.all_sprites.add(self.player)

        # Lane dashes (3 inner separators for 4 lanes)
        self.dashes = []
        for lx in [ROAD_LEFT + LANE_W * i for i in range(1, 4)]:
            for sy in range(0, SCREEN_HEIGHT, 68):
                self.dashes.append(LaneDash(lx, sy))

        # Scenery
        self.buildings   = [Building(5) for _ in range(7)]
        self.trees       = [Tree(5)     for _ in range(9)]
        self.road_offset = 0   # scroll offset for the asphalt texture

        # Spawn timers
        self.enemy_timer    = 0
        self.enemy_interval = 90    # frames between enemy spawns
        self.coin_timer     = 0
        self.coin_interval  = 120   # frames between coin spawns

        # Scoring
        self.score = 0
        self.coins = 0   # total coin UNITS collected (not count of pickups)

        # Speed / difficulty
        self.road_speed   = 5       # base scroll speed (also given to enemies)
        self.enemy_speed  = 5       # separate enemy speed (increased by coins)
        self.level        = 1

        # Practice 11 — Task 2: track coins for enemy speed-up threshold
        self.coins_at_last_speedup = 0   # coins value at the last speed increase

        # Flash message shown when enemy speed increases
        self.flash_msg      = ""
        self.flash_timer    = 0      # frames remaining for the flash

        self.game_over = False
        self.paused    = False

    # ── Main Loop ─────────────────────────────────────────────────────────
    def run(self):
        while True:
            self.clock.tick(FPS)
            self._handle_events()
            if not self.game_over and not self.paused:
                self._update()
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

    # ── Update ────────────────────────────────────────────────────────────
    def _update(self):
        """One frame of game logic."""
        keys = pygame.key.get_pressed()
        self.player.update(keys)

        # Advance road texture scroll
        self.road_offset = (self.road_offset + self.road_speed) % SCREEN_HEIGHT

        # Animate lane dashes and scenery
        for d in self.dashes:    d.update(self.road_speed)
        for b in self.buildings: b.update(self.road_speed)
        for t in self.trees:     t.update(self.road_speed)

        # ── Spawn enemies ────────────────────────────────────────────
        self.enemy_timer += 1
        if self.enemy_timer >= self.enemy_interval:
            e = EnemyCar(self.enemy_speed)   # use current enemy speed
            self.enemy_group.add(e)
            self.all_sprites.add(e)
            self.enemy_timer = 0

        # ── Spawn weighted coins (Practice 11 — Task 1) ──────────────
        self.coin_timer += 1
        if self.coin_timer >= self.coin_interval:
            c = Coin(self.road_speed)
            self.coin_group.add(c)
            self.all_sprites.add(c)
            self.coin_timer = 0

        # Update all moving sprites
        self.enemy_group.update()
        self.coin_group.update()

        # ── Collision: player ↔ enemy ────────────────────────────────
        if pygame.sprite.spritecollideany(self.player, self.enemy_group):
            self.game_over = True

        # ── Collision: player ↔ coin ─────────────────────────────────
        collected = pygame.sprite.spritecollide(self.player, self.coin_group, True)
        for coin in collected:
            # Add the coin's weight-specific value (not just 1 per pickup)
            self.coins += coin.coin_value
            self.score += coin.score_value

        # ── Practice 11 Task 2: increase enemy speed every N coins ───
        coins_since_last = self.coins - self.coins_at_last_speedup
        if coins_since_last >= ENEMY_SPEED_UP_EVERY:
            self.coins_at_last_speedup = self.coins
            self.enemy_speed = min(self.enemy_speed + 1, 20)
            # Update speed of all currently active enemies
            for e in self.enemy_group:
                e.speed = self.enemy_speed
            # Show flash message to inform the player
            self.flash_msg   = f"⚡ Enemies faster! Speed {self.enemy_speed}"
            self.flash_timer = 120   # show for 2 seconds (120 frames)

        # ── Passive score + road speed ramp every ~5 s ──────────────
        self.score += 1
        if self.score % 300 == 0:
            self.road_speed      = min(self.road_speed + 1, 15)
            self.enemy_interval  = max(40, self.enemy_interval - 5)
            self.level          += 1

        # Tick down the flash message timer
        if self.flash_timer > 0:
            self.flash_timer -= 1

    # ── Draw ──────────────────────────────────────────────────────────────
    def _draw(self):
        # Left side: city pavement base colour
        self.screen.fill((105, 98, 88))

        # Scrolling tile grid on pavement
        tile_h = 40
        for ty in range(-tile_h, SCREEN_HEIGHT + tile_h, tile_h):
            oty = (ty + self.road_offset) % (SCREEN_HEIGHT + tile_h) - tile_h
            pygame.draw.line(self.screen, CURB, (0, oty), (ROAD_LEFT, oty), 1)
        for tx in range(0, ROAD_LEFT, 20):
            pygame.draw.line(self.screen, CURB, (tx, 0), (tx, SCREEN_HEIGHT), 1)

        # Scrolling buildings
        for b in self.buildings:
            b.draw(self.screen)

        # Right side: grass
        pygame.draw.rect(self.screen, GRASS_D,
                         (ROAD_RIGHT, 0, SCREEN_WIDTH - ROAD_RIGHT, SCREEN_HEIGHT))
        for t in self.trees:
            t.draw(self.screen)

        # Asphalt texture (two blits for seamless scroll)
        self.screen.blit(self.asphalt, (ROAD_LEFT, self.road_offset - SCREEN_HEIGHT))
        self.screen.blit(self.asphalt, (ROAD_LEFT, self.road_offset))

        # Road edge markings
        pygame.draw.rect(self.screen, (215, 185, 0),
                         (ROAD_LEFT - 6, 0, 6, SCREEN_HEIGHT))   # yellow kerb
        pygame.draw.rect(self.screen, WHITE,
                         (ROAD_RIGHT, 0, 5, SCREEN_HEIGHT))      # white solid

        # Lane dashes
        for d in self.dashes:
            d.draw(self.screen)

        # Coins, enemies, player
        self.coin_group.draw(self.screen)
        self.enemy_group.draw(self.screen)
        self.screen.blit(self.player.image, self.player.rect)

        # HUD
        self._draw_hud()

        # Flash message (enemy speed-up notification)
        if self.flash_timer > 0:
            self._draw_flash()

        # Game state overlays
        if self.paused:
            self._draw_overlay("PAUSED", "Press P to resume")
        if self.game_over:
            self._draw_overlay(
                "GAME OVER",
                f"Score: {self.score}   Coins: {self.coins}   Press R"
            )

        pygame.display.flip()

    # ── HUD ───────────────────────────────────────────────────────────────
    def _draw_hud(self):
        """Render score, level, and coin counter with tier legend."""
        # Semi-transparent background pill for left HUD
        pill = pygame.Surface((170, 62), pygame.SRCALPHA)
        pill.fill((0, 0, 0, 115))
        self.screen.blit(pill, (4, 4))

        self.screen.blit(
            self.font_med.render(f"Score: {self.score}", True, WHITE), (10, 8))
        self.screen.blit(
            self.font_med.render(f"Level: {self.level}", True, (170, 215, 255)), (10, 34))

        # Coin counter (top-right)
        cs = self.font_med.render(str(self.coins), True, GOLD_C)
        cr = cs.get_rect(topright=(SCREEN_WIDTH - 14, 12))
        self.screen.blit(cs, cr)

        # Coin icon
        ix, iy = cr.left - 18, cr.centery
        pygame.draw.circle(self.screen, GOLD_C,        (ix, iy), 12)
        pygame.draw.circle(self.screen, (195, 150, 0), (ix, iy), 12, 2)
        lbl = self.font_small.render("$", True, (120, 80, 0))
        self.screen.blit(lbl, lbl.get_rect(center=(ix, iy)))

        # Coin tier legend (bottom-right corner)
        legend_x = SCREEN_WIDTH - 110
        legend_y = SCREEN_HEIGHT - 60
        for name, colour, _, coin_val, _, _ in reversed(COIN_TIERS):
            pygame.draw.circle(self.screen, colour, (legend_x, legend_y + 8), 8)
            txt = self.font_tiny.render(f"{name}: +{coin_val}", True, (200, 200, 200))
            self.screen.blit(txt, (legend_x + 14, legend_y))
            legend_y -= 18

        # Next speed-up countdown
        remaining = ENEMY_SPEED_UP_EVERY - (self.coins - self.coins_at_last_speedup)
        tip = self.font_tiny.render(
            f"Spd up in {remaining} coins", True, (200, 160, 100))
        self.screen.blit(tip, tip.get_rect(topright=(SCREEN_WIDTH - 10, 44)))

    def _draw_flash(self):
        """Draw the enemy-speed-up flash notification."""
        alpha = min(255, self.flash_timer * 4)   # fade out as timer decreases
        surf  = self.font_med.render(self.flash_msg, True, (255, 80, 80))
        surf.set_alpha(alpha)
        self.screen.blit(surf, surf.get_rect(center=(SCREEN_WIDTH // 2, 80)))

    def _draw_overlay(self, title, sub):
        """Full-screen translucent overlay with centred title and subtitle."""
        o = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        o.fill((0, 0, 0, 165))
        self.screen.blit(o, (0, 0))
        t = self.font_big.render(title, True, WHITE)
        self.screen.blit(t, t.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 35)))
        s = self.font_small.render(sub, True, (210, 210, 210))
        self.screen.blit(s, s.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20)))


# ─────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    RacerGame().run()