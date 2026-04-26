"""
ui.py — All non-game Pygame screens:
  MainMenu, NameEntry, SettingsScreen, GameOverScreen, LeaderboardScreen
Each screen has a run(screen, clock) method that returns a string action.
"""

import pygame
import sys
from persistence import load_leaderboard, load_settings, save_settings

# ── Colours ───────────────────────────────────────────────────────────────────
BLACK   = (0,   0,   0)
WHITE   = (255, 255, 255)
GRAY    = (80,  80,  80)
LGRAY   = (140, 140, 140)
DGRAY   = (30,  30,  30)
GOLD    = (255, 200, 0)
RED     = (220, 50,  50)
GREEN   = (50,  200, 80)
BLUE    = (60,  120, 220)
TEAL    = (0,   180, 180)
PANEL   = (25,  25,  35)

SW, SH  = 600, 700
FPS     = 60

# ── Palette of selectable car colours ────────────────────────────────────────
CAR_COLORS = [
    ((28,  32,  38),  "Dark"),
    ((180, 30,  30),  "Red"),
    ((30,  80,  180), "Blue"),
    ((30,  150, 60),  "Green"),
    ((200, 150, 0),   "Gold"),
    ((120, 0,   160), "Purple"),
    ((200, 200, 200), "Silver"),
    ((255, 100, 0),   "Orange"),
]


# ─────────────────────────────────────────────
#  HELPER — simple button
# ─────────────────────────────────────────────
class UIButton:
    def __init__(self, rect, text, color=GRAY, text_color=WHITE):
        self.rect       = pygame.Rect(rect)
        self.text       = text
        self.color      = color
        self.text_color = text_color
        self.hover      = False

    def draw(self, surface, font):
        c = tuple(min(255, v + 30) for v in self.color) if self.hover else self.color
        pygame.draw.rect(surface, c,     self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=10)
        lbl = font.render(self.text, True, self.text_color)
        surface.blit(lbl, lbl.get_rect(center=self.rect.center))

    def update(self, mouse_pos):
        self.hover = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and self.rect.collidepoint(event.pos))


# ─────────────────────────────────────────────
#  BACKGROUND helper
# ─────────────────────────────────────────────
def draw_bg(surface, title, subtitle=""):
    surface.fill(DGRAY)
    # Top gradient strip
    for i in range(120):
        alpha = int(180 * (1 - i / 120))
        c = (0, max(0, 60 - i // 2), max(0, 80 - i // 2))
        pygame.draw.line(surface, c, (0, i), (SW, i))

    font_big = pygame.font.SysFont("arial", 52, bold=True)
    font_sub = pygame.font.SysFont("arial", 20)
    t = font_big.render(title, True, GOLD)
    surface.blit(t, t.get_rect(center=(SW // 2, 60)))
    if subtitle:
        s = font_sub.render(subtitle, True, LGRAY)
        surface.blit(s, s.get_rect(center=(SW // 2, 110)))


# ─────────────────────────────────────────────
#  MAIN MENU
# ─────────────────────────────────────────────
class MainMenu:
    def run(self, screen, clock):
        font  = pygame.font.SysFont("arial", 28, bold=True)
        font2 = pygame.font.SysFont("arial", 16)
        cx    = SW // 2

        buttons = [
            UIButton((cx - 120, 200, 240, 54), "▶  Play",        GREEN),
            UIButton((cx - 120, 270, 240, 54), "🏆  Leaderboard", BLUE),
            UIButton((cx - 120, 340, 240, 54), "⚙  Settings",    GRAY),
            UIButton((cx - 120, 410, 240, 54), "✕  Quit",        RED),
        ]
        actions = ["play", "leaderboard", "settings", "quit"]

        while True:
            clock.tick(FPS)
            mp = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                for btn, act in zip(buttons, actions):
                    if btn.is_clicked(event):
                        return act

            draw_bg(screen, "MERCEDES RACER", "Dodge traffic · Collect power-ups · Set records")
            for btn in buttons:
                btn.update(mp)
                btn.draw(screen, font)

            hint = font2.render("Arrow keys to drive", True, LGRAY)
            screen.blit(hint, hint.get_rect(center=(cx, SH - 30)))
            pygame.display.flip()


# ─────────────────────────────────────────────
#  NAME ENTRY
# ─────────────────────────────────────────────
class NameEntry:
    def run(self, screen, clock):
        font_big  = pygame.font.SysFont("arial", 36, bold=True)
        font_med  = pygame.font.SysFont("arial", 24)
        font_hint = pygame.font.SysFont("arial", 16)
        cx        = SW // 2
        name      = ""
        box_rect  = pygame.Rect(cx - 160, 280, 320, 54)
        btn_start = UIButton((cx - 100, 370, 200, 50), "Start Racing", GREEN)
        error     = ""

        while True:
            clock.tick(FPS)
            mp = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if name.strip():
                            return name.strip()
                        error = "Please enter a name!"
                    elif event.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    else:
                        ch = event.unicode
                        if ch.isprintable() and len(name) < 16:
                            name += ch
                if btn_start.is_clicked(event):
                    if name.strip():
                        return name.strip()
                    error = "Please enter a name!"

            draw_bg(screen, "ENTER YOUR NAME")
            lbl = font_med.render("Your racing name:", True, WHITE)
            screen.blit(lbl, lbl.get_rect(center=(cx, 250)))

            # Input box
            pygame.draw.rect(screen, (50, 50, 70), box_rect, border_radius=8)
            pygame.draw.rect(screen, GOLD, box_rect, 2, border_radius=8)
            name_surf = font_big.render(name + "|", True, WHITE)
            screen.blit(name_surf, name_surf.get_rect(center=box_rect.center))

            btn_start.update(mp)
            btn_start.draw(screen, font_med)

            if error:
                err_surf = font_hint.render(error, True, RED)
                screen.blit(err_surf, err_surf.get_rect(center=(cx, 440)))

            hint = font_hint.render("Max 16 characters · Press Enter to confirm", True, LGRAY)
            screen.blit(hint, hint.get_rect(center=(cx, SH - 30)))
            pygame.display.flip()


# ─────────────────────────────────────────────
#  SETTINGS SCREEN
# ─────────────────────────────────────────────
class SettingsScreen:
    def run(self, screen, clock):
        font     = pygame.font.SysFont("arial", 24, bold=True)
        font_sm  = pygame.font.SysFont("arial", 18)
        cx       = SW // 2
        settings = load_settings()

        # Find current car color index
        def color_index():
            cur = tuple(settings["car_color"])
            for i, (c, _) in enumerate(CAR_COLORS):
                if tuple(c) == cur:
                    return i
            return 0

        ci = color_index()

        btn_sound  = UIButton((cx - 80, 200, 160, 44), "", GRAY)
        btn_diff   = UIButton((cx - 80, 290, 160, 44), "", GRAY)
        btn_col_l  = UIButton((cx - 160, 375, 44, 44), "◀", GRAY)
        btn_col_r  = UIButton((cx + 116, 375, 44, 44), "▶", GRAY)
        btn_save   = UIButton((cx - 100, 490, 200, 50), "Save & Back", GREEN)
        btn_back   = UIButton((cx - 80,  555, 160, 40), "Cancel",      RED)

        diffs = ["easy", "normal", "hard"]

        def refresh_labels():
            btn_sound.text = f"Sound: {'ON' if settings['sound'] else 'OFF'}"
            btn_diff.text  = f"Difficulty: {settings['difficulty'].capitalize()}"

        refresh_labels()

        while True:
            clock.tick(FPS)
            mp = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()

                if btn_sound.is_clicked(event):
                    settings["sound"] = not settings["sound"]
                    refresh_labels()

                if btn_diff.is_clicked(event):
                    idx = diffs.index(settings["difficulty"])
                    settings["difficulty"] = diffs[(idx + 1) % len(diffs)]
                    refresh_labels()

                if btn_col_l.is_clicked(event):
                    ci = (ci - 1) % len(CAR_COLORS)
                    settings["car_color"] = list(CAR_COLORS[ci][0])

                if btn_col_r.is_clicked(event):
                    ci = (ci + 1) % len(CAR_COLORS)
                    settings["car_color"] = list(CAR_COLORS[ci][0])

                if btn_save.is_clicked(event):
                    save_settings(settings)
                    return "back"

                if btn_back.is_clicked(event):
                    return "back"

            draw_bg(screen, "SETTINGS")

            for btn in (btn_sound, btn_diff, btn_col_l, btn_col_r, btn_save, btn_back):
                btn.update(mp)
                btn.draw(screen, font_sm)

            # Section labels
            screen.blit(font_sm.render("Audio", True, LGRAY), (cx - 160, 175))
            screen.blit(font_sm.render("Difficulty", True, LGRAY), (cx - 160, 265))
            screen.blit(font_sm.render("Car Colour", True, LGRAY), (cx - 160, 350))

            # Car colour preview swatch
            col_rect = pygame.Rect(cx - 60, 375, 120, 44)
            pygame.draw.rect(screen, CAR_COLORS[ci][0], col_rect, border_radius=6)
            pygame.draw.rect(screen, WHITE, col_rect, 2, border_radius=6)
            name_lbl = font_sm.render(CAR_COLORS[ci][1], True, WHITE)
            screen.blit(name_lbl, name_lbl.get_rect(center=col_rect.center))

            pygame.display.flip()


# ─────────────────────────────────────────────
#  GAME OVER SCREEN
# ─────────────────────────────────────────────
class GameOverScreen:
    def run(self, screen, clock, score, distance, coins, player_name):
        font_big = pygame.font.SysFont("arial", 48, bold=True)
        font_med = pygame.font.SysFont("arial", 26, bold=True)
        font_sm  = pygame.font.SysFont("arial", 20)
        cx       = SW // 2

        btn_retry = UIButton((cx - 130, 460, 120, 50), "Retry",     GREEN)
        btn_menu  = UIButton((cx + 10,  460, 120, 50), "Main Menu", BLUE)

        while True:
            clock.tick(FPS)
            mp = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if btn_retry.is_clicked(event):
                    return "retry"
                if btn_menu.is_clicked(event):
                    return "menu"

            draw_bg(screen, "GAME OVER")

            # Player name
            ns = font_med.render(f"Driver: {player_name}", True, GOLD)
            screen.blit(ns, ns.get_rect(center=(cx, 155)))

            # Stats box
            box = pygame.Rect(cx - 180, 200, 360, 230)
            pygame.draw.rect(screen, PANEL, box, border_radius=12)
            pygame.draw.rect(screen, LGRAY, box, 2, border_radius=12)

            stats = [
                ("Score",    f"{score}",       GOLD),
                ("Distance", f"{distance} m",  TEAL),
                ("Coins",    f"{coins}",        (255, 210, 50)),
            ]
            for i, (label, val, col) in enumerate(stats):
                y = 225 + i * 62
                screen.blit(font_sm.render(label, True, LGRAY),
                            (box.x + 20, y))
                v = font_med.render(val, True, col)
                screen.blit(v, (box.right - v.get_width() - 20, y))

            for btn in (btn_retry, btn_menu):
                btn.update(mp)
                btn.draw(screen, font_sm)

            pygame.display.flip()


# ─────────────────────────────────────────────
#  LEADERBOARD SCREEN
# ─────────────────────────────────────────────
class LeaderboardScreen:
    def run(self, screen, clock):
        font_med = pygame.font.SysFont("consolas", 22, bold=True)
        font_sm  = pygame.font.SysFont("consolas", 17)
        font_hdr = pygame.font.SysFont("consolas", 16, bold=True)
        cx       = SW // 2
        btn_back = UIButton((cx - 80, SH - 70, 160, 46), "◀ Back", BLUE)
        board    = load_leaderboard()

        while True:
            clock.tick(FPS)
            mp = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if btn_back.is_clicked(event):
                    return "back"

            draw_bg(screen, "LEADERBOARD", "Top 10 Drivers")

            # Header row
            hdr_y = 140
            cols  = [50, 160, 340, 440, 530]
            hdrs  = ["#", "Name", "Score", "Dist", "Coins"]
            for hx, ht in zip(cols, hdrs):
                h = font_hdr.render(ht, True, GOLD)
                screen.blit(h, (hx, hdr_y))

            pygame.draw.line(screen, LGRAY, (30, hdr_y + 24), (SW - 30, hdr_y + 24), 1)

            if not board:
                empty = font_sm.render("No scores yet — go race!", True, LGRAY)
                screen.blit(empty, empty.get_rect(center=(cx, 300)))
            else:
                for rank, entry in enumerate(board, 1):
                    y   = hdr_y + 30 + (rank - 1) * 36
                    col = GOLD if rank == 1 else (LGRAY if rank > 3 else WHITE)

                    # Alternate row background
                    if rank % 2 == 0:
                        pygame.draw.rect(screen, (40, 40, 55),
                                         (30, y - 4, SW - 60, 30), border_radius=4)

                    vals = [
                        str(rank),
                        entry.get("name", "?")[:12],
                        str(entry.get("score", 0)),
                        str(entry.get("distance", 0)) + "m",
                        str(entry.get("coins", 0)),
                    ]
                    for hx, val in zip(cols, vals):
                        s = font_sm.render(val, True, col)
                        screen.blit(s, (hx, y))

            btn_back.update(mp)
            btn_back.draw(screen, font_sm)
            pygame.display.flip()