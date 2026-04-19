"""
=============================================================
  RACER GAME — Mercedes Edition
  Changes vs original:
    - Player car redrawn to look like a Mercedes (top-down):
        sleek long body, star hood ornament, LED-style lights
    - Road completely reworked:
        * Asphalt texture (random noise squares, scrolling)
        * Left side: city pavement with tile grid + buildings
        * Right side: grass + scrolling trees
        * Yellow kerb left edge, solid white right edge
        * White dashed lane separators
    - Enemy cars have two shapes: sedan & boxy SUV
    - Coins animate (pulse scale)
=============================================================
"""

import pygame
import random
import sys
import math

# ─────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────
SCREEN_WIDTH  = 600
SCREEN_HEIGHT = 700
FPS           = 60

ROAD_LEFT  = 80
ROAD_RIGHT = 480
ROAD_W     = ROAD_RIGHT - ROAD_LEFT   # 400 px
LANE_W     = ROAD_W // 4              # 4 lanes
LANES      = [ROAD_LEFT + LANE_W * i + LANE_W // 2 for i in range(4)]

WHITE      = (255, 255, 255)
BLACK      = (0,   0,   0)
ASPHALT    = (50,  52,  55)
GOLD       = (255, 185, 0)
SILVER     = (192, 192, 210)
GRASS_D    = (34,  90,  34)
GRASS_L    = (45,  120, 45)
CURB       = (210, 200, 185)
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


# ─────────────────────────────────────────────
#  ASPHALT TEXTURE
# ─────────────────────────────────────────────
def make_asphalt_tile(w, h):
    """Return a surface with subtle asphalt noise."""
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
#  PLAYER  (Mercedes-style)
# ─────────────────────────────────────────────
class PlayerCar(pygame.sprite.Sprite):
    W, H = 48, 88

    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        self._draw()
        self.rect = self.image.get_rect()
        self.rect.centerx = LANES[1]
        self.rect.bottom   = SCREEN_HEIGHT - 30
        self.speed = 5

    def _draw(self):
        s, W, H = self.image, self.W, self.H

        # Shadow
        sh = pygame.Surface((W - 6, H - 10), pygame.SRCALPHA)
        sh.fill((0, 0, 0, 55))
        s.blit(sh, (3, 8))

        # Tyres
        for tx, ty, tw, th in [(0,8,10,18),(W-10,8,10,18),(0,H-26,10,18),(W-10,H-26,10,18)]:
            pygame.draw.rect(s, (22, 22, 22), (tx, ty, tw, th), border_radius=3)
            pygame.draw.rect(s, (155, 155, 170), (tx+2, ty+4, tw-4, th-8), border_radius=2)

        # Body
        pygame.draw.rect(s, MERC_BODY, (8, 4, W-16, H-8), border_radius=10)

        # Centre specular
        hi = pygame.Surface((8, H-20), pygame.SRCALPHA)
        hi.fill((255, 255, 255, 22))
        s.blit(hi, (W//2-4, 10))

        # Hood crease lines
        pygame.draw.line(s, MERC_SHINE, (16, 6),   (16, 30),   1)
        pygame.draw.line(s, MERC_SHINE, (W-16, 6), (W-16, 30), 1)

        # Windshield
        pygame.draw.rect(s, MERC_GLASS, (11, 12, W-22, 18), border_radius=4)
        pygame.draw.line(s, MERC_BODY, (14, 22), (W-14, 22), 1)  # wiper

        # Rear window
        pygame.draw.rect(s, MERC_GLASS, (11, H-30, W-22, 14), border_radius=4)

        # Side windows
        pygame.draw.rect(s, MERC_GLASS, (8, 34, 5, 22), border_radius=2)
        pygame.draw.rect(s, MERC_GLASS, (W-13, 34, 5, 22), border_radius=2)

        # Front LED headlights
        for lx in (10, W-18):
            pygame.draw.rect(s, LED_WHITE, (lx, 5, 8, 4), border_radius=1)
        pygame.draw.rect(s, LED_WHITE, (11, 4, W-22, 2))

        # Rear tail lights
        for lx in (10, W-18):
            pygame.draw.rect(s, LED_RED, (lx, H-9, 8, 4), border_radius=1)
        pygame.draw.rect(s, (180, 20, 20), (11, H-8, W-22, 2))

        # Mercedes three-pointed star
        cx, cy, r = W//2, 9, 5
        for i in range(3):
            a = math.radians(i * 120 - 90)
            ex = int(cx + r * math.cos(a))
            ey = int(cy + r * math.sin(a))
            pygame.draw.line(s, SILVER, (cx, cy), (ex, ey), 2)
        pygame.draw.circle(s, SILVER, (cx, cy), r, 1)

        # Boot badge
        pygame.draw.rect(s, SILVER, (W//2-6, H-11, 12, 3), border_radius=1)

    def update(self, keys):
        if keys[pygame.K_LEFT]:  self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]: self.rect.x += self.speed
        if keys[pygame.K_UP]:    self.rect.y -= self.speed
        if keys[pygame.K_DOWN]:  self.rect.y += self.speed
        self.rect.left   = max(ROAD_LEFT + 4,  self.rect.left)
        self.rect.right  = min(ROAD_RIGHT - 4, self.rect.right)
        self.rect.top    = max(0,               self.rect.top)
        self.rect.bottom = min(SCREEN_HEIGHT,   self.rect.bottom)


# ─────────────────────────────────────────────
#  ENEMY CARS
# ─────────────────────────────────────────────
class EnemyCar(pygame.sprite.Sprite):
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
        self.speed = speed

    def _draw(self):
        s, W, H, c = self.image, self.W, self.H, self.color

        # Tyres
        for tx, ty, tw, th in [(0,8,10,18),(W-10,8,10,18),(0,H-26,10,18),(W-10,H-26,10,18)]:
            pygame.draw.rect(s, (22,22,22), (tx,ty,tw,th), border_radius=3)
            pygame.draw.rect(s, (140,140,155), (tx+2,ty+4,tw-4,th-8), border_radius=2)

        if self.shape == "sedan":
            pygame.draw.rect(s, c, (8, 4, W-16, H-8), border_radius=9)
            pygame.draw.rect(s, (160,210,240), (11,12,W-22,16), border_radius=4)
            pygame.draw.rect(s, (160,210,240), (11,H-28,W-22,12), border_radius=4)
            pygame.draw.rect(s, (160,210,240), (8,34,5,20), border_radius=2)
            pygame.draw.rect(s, (160,210,240), (W-13,34,5,20), border_radius=2)
        else:  # SUV — boxy
            pygame.draw.rect(s, c, (7, 3, W-14, H-6), border_radius=5)
            dc = tuple(max(0, x-45) for x in c)
            pygame.draw.rect(s, dc, (12, 5, W-24, 3))
            pygame.draw.rect(s, dc, (12, 10, W-24, 3))
            pygame.draw.rect(s, (160,210,240), (10,15,W-20,20), border_radius=3)
            pygame.draw.rect(s, (160,210,240), (10,H-32,W-20,16), border_radius=3)

        # Headlights (top = oncoming, so lights at top)
        for lx in (10, W-18):
            pygame.draw.rect(s, LED_RED, (lx, 5, 8, 4), border_radius=1)
        pygame.draw.rect(s, (200,20,20), (11, 4, W-22, 2))

        # Tail lights (bottom)
        for lx in (10, W-18):
            pygame.draw.rect(s, LED_WHITE, (lx, H-9, 8, 4), border_radius=1)
        pygame.draw.rect(s, (220,230,255), (11, H-8, W-22, 2))

    def update(self, *args):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


# ─────────────────────────────────────────────
#  COIN
# ─────────────────────────────────────────────
class Coin(pygame.sprite.Sprite):

    def __init__(self, speed):
        super().__init__()
        self._frame = random.randint(0, 29)
        self._base  = self._make_base()
        self.image  = self._base.copy()
        self.rect   = self.image.get_rect()
        self.rect.centerx = random.choice(LANES)
        self.rect.bottom   = -10
        self.speed = speed

    @staticmethod
    def _make_base():
        surf = pygame.Surface((28, 28), pygame.SRCALPHA)
        pygame.draw.circle(surf, GOLD,           (14,14), 13)
        pygame.draw.circle(surf, (200,155,0),    (14,14), 13, 2)
        pygame.draw.circle(surf, (255,230,80),   (14,14), 8)
        for a in range(0, 360, 90):
            rad = math.radians(a)
            pygame.draw.line(surf, WHITE, (14,14),
                             (int(14+11*math.cos(rad)), int(14+11*math.sin(rad))), 1)
        return surf

    def update(self, *args):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill(); return
        self._frame = (self._frame + 1) % 30
        scale = 1.0 + 0.12 * math.sin(self._frame / 30 * 2 * math.pi)
        sz = max(1, int(28 * scale))
        self.image = pygame.transform.smoothscale(self._base, (sz, sz))
        cx, cy = self.rect.center
        self.rect = self.image.get_rect(center=(cx, cy))


# ─────────────────────────────────────────────
#  SCENERY
# ─────────────────────────────────────────────
class Building:
    def __init__(self, speed, y=None):
        self.w     = random.randint(28, 55)
        self.h     = random.randint(60, 160)
        self.x     = random.randint(2, max(2, ROAD_LEFT - self.w - 4))
        self.y     = y if y is not None else random.randint(-200, SCREEN_HEIGHT)
        self.color = random.choice(BUILDING_COLORS)
        self.speed = speed
        self.wins  = [(random.randint(5, self.w-11), random.randint(8, self.h-16),
                       random.random() > 0.4)
                      for _ in range(random.randint(4, 10))]

    def update(self, speed):
        self.speed = speed
        self.y += speed
        if self.y > SCREEN_HEIGHT:
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
        self.x = random.randint(ROAD_RIGHT + 6, SCREEN_WIDTH - 16)
        self.r = random.randint(12, 22)
        self.y = y if y is not None else random.randint(-self.r, SCREEN_HEIGHT)

    def update(self, speed):
        self.y += speed
        if self.y - self.r > SCREEN_HEIGHT:
            self.__init__(speed)

    def draw(self, surface):
        pygame.draw.rect(surface, (90, 55, 20), (self.x-3, self.y, 6, self.r))
        pygame.draw.circle(surface, GRASS_D, (self.x, self.y), self.r)
        pygame.draw.circle(surface, GRASS_L, (self.x-4, self.y-4), max(1, self.r-4))


class LaneDash:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def update(self, speed):
        self.y += speed
        if self.y > SCREEN_HEIGHT:
            self.y -= SCREEN_HEIGHT + 50

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, (self.x-3, self.y, 6, 38), border_radius=2)


# ─────────────────────────────────────────────
#  GAME
# ─────────────────────────────────────────────
class RacerGame:

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Mercedes Racer — Arrow Keys")
        self.clock  = pygame.time.Clock()
        self.font_big   = pygame.font.SysFont("arial", 38, bold=True)
        self.font_med   = pygame.font.SysFont("arial", 22, bold=True)
        self.font_small = pygame.font.SysFont("arial", 17)
        self.asphalt    = make_asphalt_tile(ROAD_W, SCREEN_HEIGHT)
        self._init_game()

    def _init_game(self):
        self.all_sprites = pygame.sprite.Group()
        self.enemy_group = pygame.sprite.Group()
        self.coin_group  = pygame.sprite.Group()

        self.player = PlayerCar()
        self.all_sprites.add(self.player)

        # Lane dashes for 3 inner separators
        self.dashes = []
        for lx in [ROAD_LEFT + LANE_W * i for i in range(1, 4)]:
            for sy in range(0, SCREEN_HEIGHT, 68):
                self.dashes.append(LaneDash(lx, sy))

        self.buildings   = [Building(5) for _ in range(7)]
        self.trees       = [Tree(5)     for _ in range(9)]
        self.road_offset = 0

        self.enemy_timer    = 0
        self.enemy_interval = 90
        self.coin_timer     = 0
        self.coin_interval  = 140

        self.score     = 0
        self.coins     = 0
        self.speed     = 5
        self.level     = 1
        self.game_over = False
        self.paused    = False

    def run(self):
        while True:
            self.clock.tick(FPS)
            self._handle_events()
            if not self.game_over and not self.paused:
                self._update()
            self._draw()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.game_over:
                    self._init_game()
                if event.key == pygame.K_p:
                    self.paused = not self.paused

    def _update(self):
        keys = pygame.key.get_pressed()
        self.player.update(keys)
        self.road_offset = (self.road_offset + self.speed) % SCREEN_HEIGHT

        for d in self.dashes:     d.update(self.speed)
        for b in self.buildings:  b.update(self.speed)
        for t in self.trees:      t.update(self.speed)

        self.enemy_timer += 1
        if self.enemy_timer >= self.enemy_interval:
            e = EnemyCar(self.speed)
            self.enemy_group.add(e); self.all_sprites.add(e)
            self.enemy_timer = 0

        self.coin_timer += 1
        if self.coin_timer >= self.coin_interval:
            c = Coin(self.speed)
            self.coin_group.add(c); self.all_sprites.add(c)
            self.coin_timer = 0

        self.enemy_group.update()
        self.coin_group.update()

        if pygame.sprite.spritecollideany(self.player, self.enemy_group):
            self.game_over = True

        collected     = pygame.sprite.spritecollide(self.player, self.coin_group, True)
        self.coins   += len(collected)
        self.score   += len(collected) * 10
        self.score   += 1
        if self.score % 300 == 0:
            self.speed          = min(self.speed + 1, 15)
            self.enemy_interval = max(40, self.enemy_interval - 5)
            self.level         += 1

    def _draw(self):
        # ── Left: city pavement ───────────────────────────────────────
        self.screen.fill((105, 98, 88))
        tile_h = 40
        for ty in range(-tile_h, SCREEN_HEIGHT + tile_h, tile_h):
            oty = (ty + self.road_offset) % (SCREEN_HEIGHT + tile_h) - tile_h
            pygame.draw.line(self.screen, CURB, (0, oty), (ROAD_LEFT, oty), 1)
        for tx in range(0, ROAD_LEFT, 20):
            pygame.draw.line(self.screen, CURB, (tx, 0), (tx, SCREEN_HEIGHT), 1)
        for b in self.buildings: b.draw(self.screen)

        # ── Right: grass + trees ──────────────────────────────────────
        pygame.draw.rect(self.screen, GRASS_D,
                         (ROAD_RIGHT, 0, SCREEN_WIDTH - ROAD_RIGHT, SCREEN_HEIGHT))
        for t in self.trees: t.draw(self.screen)

        # ── Asphalt texture (scrolling) ───────────────────────────────
        self.screen.blit(self.asphalt, (ROAD_LEFT, self.road_offset - SCREEN_HEIGHT))
        self.screen.blit(self.asphalt, (ROAD_LEFT, self.road_offset))

        # ── Road edges ────────────────────────────────────────────────
        pygame.draw.rect(self.screen, (215, 185, 0), (ROAD_LEFT-6, 0, 6, SCREEN_HEIGHT))  # yellow kerb
        pygame.draw.rect(self.screen, WHITE,          (ROAD_RIGHT,  0, 5, SCREEN_HEIGHT))  # white line

        # ── Lane dashes ───────────────────────────────────────────────
        for d in self.dashes: d.draw(self.screen)

        # ── Sprites ───────────────────────────────────────────────────
        self.coin_group.draw(self.screen)
        self.enemy_group.draw(self.screen)
        self.screen.blit(self.player.image, self.player.rect)

        self._draw_hud()

        if self.paused:
            self._draw_overlay("PAUSED", "Press P to resume")
        if self.game_over:
            self._draw_overlay("GAME OVER",
                               f"Score: {self.score}   Coins: {self.coins}   Press R")

        pygame.display.flip()

    def _draw_hud(self):
        # Dark pill background
        pill = pygame.Surface((165, 62), pygame.SRCALPHA)
        pill.fill((0, 0, 0, 115))
        self.screen.blit(pill, (4, 4))

        self.screen.blit(self.font_med.render(f"Score: {self.score}", True, WHITE), (10, 8))
        self.screen.blit(self.font_med.render(f"Level: {self.level}", True, (170, 215, 255)), (10, 34))

        # Coin counter top-right
        cs = self.font_med.render(str(self.coins), True, GOLD)
        cr = cs.get_rect(topright=(SCREEN_WIDTH - 14, 12))
        self.screen.blit(cs, cr)
        # Coin icon
        ix, iy = cr.left - 18, cr.centery
        pygame.draw.circle(self.screen, GOLD, (ix, iy), 12)
        pygame.draw.circle(self.screen, (195, 150, 0), (ix, iy), 12, 2)
        lbl = self.font_small.render("$", True, (120, 80, 0))
        self.screen.blit(lbl, lbl.get_rect(center=(ix, iy)))

    def _draw_overlay(self, title, sub):
        o = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        o.fill((0, 0, 0, 165))
        self.screen.blit(o, (0, 0))
        t = self.font_big.render(title, True, WHITE)
        self.screen.blit(t, t.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 35)))
        s = self.font_small.render(sub, True, (210, 210, 210))
        self.screen.blit(s, s.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20)))


if __name__ == "__main__":
    RacerGame().run()