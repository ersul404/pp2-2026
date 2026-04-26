"""
ui.py — All Pygame screens for TSIS 4 Snake:
  MainMenu, NameEntry, SettingsScreen, GameOverScreen, LeaderboardScreen
"""

import pygame
import sys
from config import (WIDTH, HEIGHT, FPS, BLACK, WHITE, GRAY, LGRAY, DGRAY,
                    GOLD, TEAL, PANEL, ACTIVE_C, POWERUP_COLORS,
                    SETTINGS_FILE, DEFAULT_SETTINGS)
from db import get_leaderboard
from game import load_settings, save_settings

SW, SH = WIDTH, HEIGHT

# ── Selectable snake colours ──────────────────────────────────────────────────
SNAKE_COLORS = [
    ([0,   200, 0],   "Green"),
    ([0,   160, 220], "Blue"),
    ([220, 50,  50],  "Red"),
    ([200, 150, 0],   "Gold"),
    ([160, 0,   200], "Purple"),
    ([0,   200, 180], "Teal"),
    ([220, 220, 220], "White"),
    ([255, 120, 0],   "Orange"),
]

RED_C  = (200, 40,  40)
GREEN_C= (50,  200, 80)
BLUE_C = (60,  120, 220)


# ─────────────────────────────────────────────
#  UI BUTTON
# ─────────────────────────────────────────────
class UIButton:
    def __init__(self, rect, text, color=GRAY, text_color=WHITE):
        self.rect       = pygame.Rect(rect)
        self.text       = text
        self.color      = color
        self.text_color = text_color
        self.hover      = False

    def draw(self, surface, font):
        c = tuple(min(255, v+30) for v in self.color) if self.hover else self.color
        pygame.draw.rect(surface, c,     self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 2,  border_radius=10)
        lbl = font.render(self.text, True, self.text_color)
        surface.blit(lbl, lbl.get_rect(center=self.rect.center))

    def update(self, mp):
        self.hover = self.rect.collidepoint(mp)

    def is_clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and self.rect.collidepoint(event.pos))


# ─────────────────────────────────────────────
#  BACKGROUND
# ─────────────────────────────────────────────
def draw_bg(surface, title, subtitle=""):
    surface.fill(DGRAY)
    for i in range(100):
        c = (0, max(0, 50 - i//2), max(0, 70 - i//2))
        pygame.draw.line(surface, c, (0, i), (SW, i))
    font_big = pygame.font.SysFont("consolas", 46, bold=True)
    font_sub = pygame.font.SysFont("consolas", 18)
    t = font_big.render(title, True, GOLD)
    surface.blit(t, t.get_rect(center=(SW//2, 55)))
    if subtitle:
        s = font_sub.render(subtitle, True, LGRAY)
        surface.blit(s, s.get_rect(center=(SW//2, 100)))


# ─────────────────────────────────────────────
#  MAIN MENU
# ─────────────────────────────────────────────
class MainMenu:
    def run(self, screen, clock):
        font  = pygame.font.SysFont("consolas", 26, bold=True)
        font2 = pygame.font.SysFont("consolas", 15)
        cx    = SW // 2

        buttons = [
            UIButton((cx-110, 190, 220, 52), "▶  Play",        GREEN_C),
            UIButton((cx-110, 258, 220, 52), "🏆  Leaderboard", BLUE_C),
            UIButton((cx-110, 326, 220, 52), "⚙  Settings",    GRAY),
            UIButton((cx-110, 394, 220, 52), "✕  Quit",        RED_C),
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

            draw_bg(screen, "SNAKE", "Arrow keys to move · Avoid poison · Grab power-ups")
            for btn in buttons:
                btn.update(mp)
                btn.draw(screen, font)

            hint = font2.render("P = Pause during game", True, LGRAY)
            screen.blit(hint, hint.get_rect(center=(cx, SH - 28)))
            pygame.display.flip()


# ─────────────────────────────────────────────
#  NAME ENTRY
# ─────────────────────────────────────────────
class NameEntry:
    def run(self, screen, clock):
        font_big  = pygame.font.SysFont("consolas", 34, bold=True)
        font_med  = pygame.font.SysFont("consolas", 22)
        font_hint = pygame.font.SysFont("consolas", 15)
        cx        = SW // 2
        name      = ""
        box       = pygame.Rect(cx - 150, 270, 300, 52)
        btn_start = UIButton((cx - 90, 350, 180, 48), "Start", GREEN_C)
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
                        error = "Please enter a username!"
                    elif event.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    else:
                        ch = event.unicode
                        if ch.isprintable() and len(name) < 20:
                            name += ch
                if btn_start.is_clicked(event):
                    if name.strip():
                        return name.strip()
                    error = "Please enter a username!"

            draw_bg(screen, "ENTER USERNAME")
            lbl = font_med.render("Your username:", True, WHITE)
            screen.blit(lbl, lbl.get_rect(center=(cx, 240)))

            pygame.draw.rect(screen, (45, 45, 65), box, border_radius=8)
            pygame.draw.rect(screen, GOLD, box, 2, border_radius=8)
            ns = font_big.render(name + "|", True, WHITE)
            screen.blit(ns, ns.get_rect(center=box.center))

            btn_start.update(mp)
            btn_start.draw(screen, font_med)

            if error:
                es = font_hint.render(error, True, (220, 80, 80))
                screen.blit(es, es.get_rect(center=(cx, 420)))

            hint = font_hint.render("Max 20 chars · Enter to confirm", True, LGRAY)
            screen.blit(hint, hint.get_rect(center=(cx, SH - 28)))
            pygame.display.flip()


# ─────────────────────────────────────────────
#  SETTINGS SCREEN
# ─────────────────────────────────────────────
class SettingsScreen:
    def run(self, screen, clock):
        font    = pygame.font.SysFont("consolas", 22, bold=True)
        font_sm = pygame.font.SysFont("consolas", 17)
        cx      = SW // 2
        s       = load_settings()

        # Find current color index
        def color_idx():
            cur = s["snake_color"]
            for i, (c, _) in enumerate(SNAKE_COLORS):
                if c == cur:
                    return i
            return 0

        ci = color_idx()

        btn_grid   = UIButton((cx - 70, 195, 140, 40), "", GRAY)
        btn_sound  = UIButton((cx - 70, 255, 140, 40), "", GRAY)
        btn_col_l  = UIButton((cx - 155, 335, 40, 40), "◀", GRAY)
        btn_col_r  = UIButton((cx + 115, 335, 40, 40), "▶", GRAY)
        btn_save   = UIButton((cx - 90,  430, 180, 48), "Save & Back", GREEN_C)
        btn_cancel = UIButton((cx - 70,  492, 140, 38), "Cancel",      RED_C)

        def refresh():
            btn_grid.text  = f"Grid: {'ON' if s['grid'] else 'OFF'}"
            btn_sound.text = f"Sound: {'ON' if s['sound'] else 'OFF'}"

        refresh()

        while True:
            clock.tick(FPS)
            mp = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if btn_grid.is_clicked(event):
                    s["grid"] = not s["grid"]; refresh()
                if btn_sound.is_clicked(event):
                    s["sound"] = not s["sound"]; refresh()
                if btn_col_l.is_clicked(event):
                    ci = (ci - 1) % len(SNAKE_COLORS)
                    s["snake_color"] = SNAKE_COLORS[ci][0]
                if btn_col_r.is_clicked(event):
                    ci = (ci + 1) % len(SNAKE_COLORS)
                    s["snake_color"] = SNAKE_COLORS[ci][0]
                if btn_save.is_clicked(event):
                    save_settings(s); return "back"
                if btn_cancel.is_clicked(event):
                    return "back"

            draw_bg(screen, "SETTINGS")

            # Section labels
            for y, lbl in [(170, "Grid overlay"), (230, "Sound"),
                           (310, "Snake colour")]:
                screen.blit(font_sm.render(lbl, True, LGRAY), (cx - 155, y))

            for btn in (btn_grid, btn_sound, btn_col_l, btn_col_r,
                        btn_save, btn_cancel):
                btn.update(mp)
                btn.draw(screen, font_sm)

            # Colour swatch
            swatch = pygame.Rect(cx - 70, 335, 140, 40)
            pygame.draw.rect(screen, SNAKE_COLORS[ci][0], swatch, border_radius=6)
            pygame.draw.rect(screen, WHITE, swatch, 2, border_radius=6)
            nl = font_sm.render(SNAKE_COLORS[ci][1], True, WHITE)
            screen.blit(nl, nl.get_rect(center=swatch.center))

            pygame.display.flip()


# ─────────────────────────────────────────────
#  GAME OVER SCREEN
# ─────────────────────────────────────────────
class GameOverScreen:
    def run(self, screen, clock, score, level, personal_best, username):
        font_big = pygame.font.SysFont("consolas", 44, bold=True)
        font_med = pygame.font.SysFont("consolas", 24, bold=True)
        font_sm  = pygame.font.SysFont("consolas", 19)
        cx       = SW // 2

        btn_retry = UIButton((cx - 125, 450, 115, 48), "Retry",     GREEN_C)
        btn_menu  = UIButton((cx + 10,  450, 115, 48), "Main Menu", BLUE_C)

        new_best = score >= personal_best and score > 0

        while True:
            clock.tick(FPS)
            mp = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if btn_retry.is_clicked(event): return "retry"
                if btn_menu.is_clicked(event):  return "menu"

            draw_bg(screen, "GAME OVER")

            # Driver name
            ns = font_med.render(f"Player: {username}", True, GOLD)
            screen.blit(ns, ns.get_rect(center=(cx, 145)))

            # Stats box
            box = pygame.Rect(cx - 170, 185, 340, 240)
            pygame.draw.rect(screen, PANEL, box, border_radius=12)
            pygame.draw.rect(screen, LGRAY, box, 2,  border_radius=12)

            stats = [
                ("Score",          str(score),        GOLD),
                ("Level Reached",  str(level),        TEAL),
                ("Personal Best",  str(personal_best),
                 (255, 200, 50) if new_best else LGRAY),
            ]
            for i, (lbl, val, col) in enumerate(stats):
                y = 210 + i * 64
                screen.blit(font_sm.render(lbl, True, LGRAY), (box.x + 16, y))
                v = font_med.render(val, True, col)
                screen.blit(v, (box.right - v.get_width() - 16, y))

            if new_best:
                nb = font_sm.render("🎉 New Personal Best!", True, (255, 220, 50))
                screen.blit(nb, nb.get_rect(center=(cx, 435)))

            for btn in (btn_retry, btn_menu):
                btn.update(mp)
                btn.draw(screen, font_sm)

            pygame.display.flip()


# ─────────────────────────────────────────────
#  LEADERBOARD SCREEN
# ─────────────────────────────────────────────
class LeaderboardScreen:
    def run(self, screen, clock):
        font_med = pygame.font.SysFont("consolas", 20, bold=True)
        font_sm  = pygame.font.SysFont("consolas", 16)
        font_hdr = pygame.font.SysFont("consolas", 15, bold=True)
        cx       = SW // 2
        btn_back = UIButton((cx - 75, SH - 62, 150, 44), "◀ Back", BLUE_C)
        board    = get_leaderboard(10)

        while True:
            clock.tick(FPS)
            mp = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if btn_back.is_clicked(event): return "back"

            draw_bg(screen, "LEADERBOARD", "Top 10 All-Time Scores")

            hdr_y = 130
            cols  = [28, 90, 270, 370, 460]
            hdrs  = ["#", "Username", "Score", "Level", "Date"]
            for hx, ht in zip(cols, hdrs):
                screen.blit(font_hdr.render(ht, True, GOLD), (hx, hdr_y))
            pygame.draw.line(screen, LGRAY, (20, hdr_y+22), (SW-20, hdr_y+22), 1)

            if not board:
                empty = font_sm.render("No scores yet — play a game!", True, LGRAY)
                screen.blit(empty, empty.get_rect(center=(cx, 280)))
            else:
                for rank, entry in enumerate(board, 1):
                    y   = hdr_y + 28 + (rank-1) * 34
                    col = GOLD if rank == 1 else (WHITE if rank <= 3 else LGRAY)
                    if rank % 2 == 0:
                        pygame.draw.rect(screen, (38, 38, 55),
                                         (20, y-3, SW-40, 28), border_radius=4)
                    vals = [
                        str(rank),
                        entry.get("username","?")[:14],
                        str(entry.get("score", 0)),
                        str(entry.get("level", 0)),
                        str(entry.get("date",""))[:10],
                    ]
                    for hx, val in zip(cols, vals):
                        screen.blit(font_sm.render(val, True, col), (hx, y))

            btn_back.update(mp)
            btn_back.draw(screen, font_sm)
            pygame.display.flip()