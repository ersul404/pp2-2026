"""
config.py — All constants for TSIS 4 Snake game.
"""

# ── Grid ──────────────────────────────────────
CELL   = 20
COLS   = 30
ROWS   = 30
WIDTH  = COLS * CELL   # 600
HEIGHT = ROWS * CELL   # 600
FPS    = 60

# ── Snake speeds (logic steps per second) ─────
LEVEL_SPEEDS = {1: 8, 2: 10, 3: 13, 4: 16, 5: 20}
MAX_LEVEL       = max(LEVEL_SPEEDS)
FOODS_PER_LEVEL = 3

# ── Colours ───────────────────────────────────
BLACK      = (0,   0,   0)
WHITE      = (255, 255, 255)
DARK_GREEN = (0,   140, 0)
GREEN      = (0,   200, 0)
RED        = (220, 30,  30)
GOLD       = (255, 200, 0)
GRAY       = (50,  50,  50)
LGRAY      = (140, 140, 140)
DGRAY      = (25,  25,  35)
BG         = (15,  15,  15)
WALL_C     = (80,  80,  80)
PANEL      = (30,  30,  45)
ACTIVE_C   = (255, 215, 50)
TEAL       = (0,   180, 180)
PURPLE     = (160, 0,   200)
ORANGE     = (255, 140, 0)

# Poison food colour
POISON_C   = (120, 0,   20)

# Power-up colours
POWERUP_COLORS = {
    "speed":  (255, 160, 0),
    "slow":   (0,   160, 255),
    "shield": (0,   220, 120),
}

# Obstacle block colour
OBSTACLE_C = (100, 80, 60)

# ── Directions ────────────────────────────────
UP    = (0,  -1)
DOWN  = (0,   1)
LEFT  = (-1,  0)
RIGHT = (1,   0)

# ── Food tiers (name, colour, score, grow, lifespan_s, weight) ──
FOOD_TIERS = [
    ("apple",   (220, 50,  50),  10, 1, 10.0, 60),
    ("cherry",  (255, 20, 147),  25, 2,  7.0, 30),
    ("diamond", (100, 200, 255), 60, 3,  4.0, 10),
]

MAX_FOODS           = 3
FOOD_SPAWN_INTERVAL = 3.5   # seconds

# ── Power-up settings ─────────────────────────
POWERUP_DURATION    = 5.0   # seconds effect lasts
POWERUP_FIELD_LIFE  = 8.0   # seconds before disappears uncollected
SPEED_BOOST_EXTRA   = 6     # extra steps/sec when boosted
SLOW_MOTION_REDUCE  = 4     # steps/sec reduction when slowed

# ── Obstacles ────────────────────────────────
MIN_LEVEL_FOR_OBS   = 3     # obstacles start appearing from level 3
OBSTACLES_PER_LEVEL = 4     # extra blocks added each new level

# ── DB connection (edit to match your PostgreSQL setup) ──
DB_CONFIG = {
    "host":     "localhost",
    "port":     5432,
    "dbname":   "snake_db",
    "user":     "postgres",
    "password": "postgres",   # ← change to your password
}

SETTINGS_FILE = "settings.json"

DEFAULT_SETTINGS = {
    "snake_color": [0, 200, 0],
    "grid":        True,
    "sound":       False,
}