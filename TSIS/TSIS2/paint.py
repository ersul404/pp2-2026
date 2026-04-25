"""
=============================================================
  PAINT APPLICATION — TSIS 2
  Extends Practice 10 & Practice 11 with:
    - Pencil (freehand) tool
    - Straight line tool with live preview
    - Three brush size levels: small(2), medium(5), large(10)
      switchable via keys 1/2/3 or on-screen buttons
    - Flood-fill tool (get_at / set_at, no extra libs)
    - Ctrl+S saves canvas as timestamped .png
    - Text tool: click → type → Enter to confirm / Escape to cancel
    - All Practice 10+11 shapes respect active brush size
=============================================================
"""

import pygame
import sys
from tools import (
    ToolManager, TOOL_PENCIL, TOOL_LINE, TOOL_RECT, TOOL_SQUARE,
    TOOL_CIRCLE, TOOL_RTRI, TOOL_ETRI, TOOL_RHOMBUS,
    TOOL_ERASER, TOOL_FILL, TOOL_TEXT,
    DRAG_TOOLS,
)
from datetime import datetime

# ─────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────
SCREEN_W  = 1100
SCREEN_H  = 720
PANEL_H   = 100
CANVAS_H  = SCREEN_H - PANEL_H
FPS       = 60

WHITE    = (255, 255, 255)
BLACK    = (0,   0,   0)
PANEL_BG = (35,  35,  35)
ACTIVE_C = (255, 215, 50)

PALETTE = [
    (0,   0,   0),   (255, 255, 255), (220, 30,  30),  (30,  180, 30),
    (30,  30,  220), (255, 200, 0),   (255, 140, 0),   (180, 0,   180),
    (0,   200, 200), (180, 100, 40),  (255, 182, 193), (128, 128, 128),
    (0,   100, 0),   (0,   0,   128), (255, 69,  0),   (173, 216, 230),
]

# Brush size presets
BRUSH_SIZES = {1: 2, 2: 5, 3: 10}


# ─────────────────────────────────────────────
#  BUTTON
# ─────────────────────────────────────────────
class Button:
    def __init__(self, rect, label, tool_id):
        self.rect    = pygame.Rect(rect)
        self.label   = label
        self.tool_id = tool_id
        self.font    = pygame.font.SysFont("consolas", 11, bold=True)

    def draw(self, surface, active_tool):
        active = self.tool_id == active_tool
        bg     = ACTIVE_C        if active else (80, 80, 80)
        border = (255, 255, 255) if active else (55, 55, 55)
        pygame.draw.rect(surface, bg,     self.rect, border_radius=6)
        pygame.draw.rect(surface, border, self.rect, 2, border_radius=6)
        txt = self.font.render(self.label, True, BLACK if active else (220, 220, 220))
        surface.blit(txt, txt.get_rect(center=self.rect.center))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


class SizeButton:
    """Button for selecting brush size preset (1/2/3)."""
    def __init__(self, rect, label, size_id):
        self.rect    = pygame.Rect(rect)
        self.label   = label
        self.size_id = size_id
        self.font    = pygame.font.SysFont("consolas", 11, bold=True)

    def draw(self, surface, active_size_id):
        active = self.size_id == active_size_id
        bg     = (100, 180, 255) if active else (70, 70, 70)
        border = (255, 255, 255) if active else (50, 50, 50)
        pygame.draw.rect(surface, bg,     self.rect, border_radius=5)
        pygame.draw.rect(surface, border, self.rect, 2, border_radius=5)
        txt = self.font.render(self.label, True, BLACK if active else (200, 200, 200))
        surface.blit(txt, txt.get_rect(center=self.rect.center))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


# ─────────────────────────────────────────────
#  PAINT APP
# ─────────────────────────────────────────────
class PaintApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Paint — TSIS 2")
        self.clock = pygame.time.Clock()

        self.canvas = pygame.Surface((SCREEN_W, CANVAS_H))
        self.canvas.fill(WHITE)

        # Current state
        self.tool        = TOOL_PENCIL
        self.color       = BLACK
        self.size_id     = 2              # 1=small, 2=medium, 3=large
        self.brush_size  = BRUSH_SIZES[self.size_id]
        self.eraser_size = 18

        # Drag state (shapes, line)
        self.dragging      = False
        self.drag_start    = None
        self.drag_snapshot = None

        # Pencil trail
        self.last_pos = None

        # Text tool state
        self.text_active   = False
        self.text_pos      = None    # (x, y) on canvas
        self.text_buffer   = ""
        self.text_font     = pygame.font.SysFont("arial", 22)
        self.text_snapshot = None   # canvas before text

        # Tool manager (handles shapes, fill, etc.)
        self.tm = ToolManager()

        self._build_ui()

    # ── UI ────────────────────────────────────────────────────────────────
    def _build_ui(self):
        py    = CANVAS_H + 5
        btn_w = 74
        btn_h = 30
        gap   = 5
        x0    = 6

        tool_defs = [
            ("✏ Pencil",   TOOL_PENCIL),
            ("╱ Line",     TOOL_LINE),
            ("▭ Rect",     TOOL_RECT),
            ("■ Square",   TOOL_SQUARE),
            ("○ Circle",   TOOL_CIRCLE),
            ("◺ R.Tri",    TOOL_RTRI),
            ("△ Eq.Tri",   TOOL_ETRI),
            ("◇ Rhombus",  TOOL_RHOMBUS),
            ("⌫ Eraser",   TOOL_ERASER),
            ("🪣 Fill",     TOOL_FILL),
            ("T Text",     TOOL_TEXT),
        ]

        self.buttons = [
            Button((x0 + i * (btn_w + gap), py + 4, btn_w, btn_h), lbl, tid)
            for i, (lbl, tid) in enumerate(tool_defs)
        ]

        # Brush size buttons
        sz_x = x0
        sz_y = py + btn_h + 12
        self.size_buttons = [
            SizeButton((sz_x + i * 44, sz_y, 40, 22), lbl, sid)
            for i, (lbl, sid) in enumerate([
                ("S:2", 1), ("M:5", 2), ("L:10", 3)
            ])
        ]

        # Clear button
        self.clear_rect = pygame.Rect(sz_x + 3 * 44 + 6, sz_y, 56, 22)

        # Palette
        sw    = 22
        gap_s = 3
        pal_x = x0 + len(tool_defs) * (btn_w + gap) + 12
        pal_y = py + 4
        self.swatches = []
        for i, c in enumerate(PALETTE):
            cx = pal_x + (i % 8) * (sw + gap_s)
            cy = pal_y + (i // 8) * (sw + gap_s)
            self.swatches.append((pygame.Rect(cx, cy, sw, sw), c))

        self.lf = pygame.font.SysFont("consolas", 11, bold=True)

    # ── Main Loop ─────────────────────────────────────────────────────────
    def run(self):
        while True:
            self.clock.tick(FPS)
            self._handle_events()
            self._draw()

    # ── Events ────────────────────────────────────────────────────────────
    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            # ── Keyboard ─────────────────────────────────────────────
            if event.type == pygame.KEYDOWN:
                # Text tool active: capture typing
                if self.text_active:
                    self._handle_text_key(event)
                    return

                # Ctrl+S → save
                mods = pygame.key.get_mods()
                if event.key == pygame.K_s and (mods & pygame.KMOD_CTRL):
                    self._save_canvas()
                    return

                # Tool shortcuts
                shortcuts = {
                    pygame.K_p: TOOL_PENCIL,
                    pygame.K_l: TOOL_LINE,
                    pygame.K_r: TOOL_RECT,
                    pygame.K_q: TOOL_SQUARE,
                    pygame.K_c: TOOL_CIRCLE,
                    pygame.K_t: TOOL_RTRI,
                    pygame.K_g: TOOL_ETRI,
                    pygame.K_d: TOOL_RHOMBUS,
                    pygame.K_e: TOOL_ERASER,
                    pygame.K_f: TOOL_FILL,
                    pygame.K_x: TOOL_TEXT,
                }
                if event.key in shortcuts:
                    self.tool = shortcuts[event.key]

                # Brush size shortcuts
                if event.key == pygame.K_1:
                    self._set_size(1)
                if event.key == pygame.K_2:
                    self._set_size(2)
                if event.key == pygame.K_3:
                    self._set_size(3)

                if event.key in (pygame.K_DELETE, pygame.K_BACKSPACE):
                    self.canvas.fill(WHITE)

            # ── Mouse DOWN ────────────────────────────────────────────
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos

                # Panel UI clicks
                for btn in self.buttons:
                    if btn.is_clicked(event.pos):
                        # Commit any active text before switching
                        if self.text_active:
                            self._commit_text()
                        self.tool = btn.tool_id
                        return

                for sb in self.size_buttons:
                    if sb.is_clicked(event.pos):
                        self._set_size(sb.size_id)
                        return

                if self.clear_rect.collidepoint(event.pos):
                    self.canvas.fill(WHITE)
                    return

                for rect, c in self.swatches:
                    if rect.collidepoint(event.pos):
                        self.color = c
                        if self.tool == TOOL_ERASER:
                            self.tool = TOOL_PENCIL
                        return

                # Canvas click
                if my < CANVAS_H:
                    if self.tool == TOOL_TEXT:
                        # Start/move text cursor
                        if self.text_active:
                            self._commit_text()
                        self._start_text(mx, my)
                        return

                    if self.tool == TOOL_FILL:
                        self.tm.flood_fill(self.canvas, mx, my, self.color)
                        return

                    if self.tool in DRAG_TOOLS:
                        self.dragging      = True
                        self.drag_start    = (mx, my)
                        self.drag_snapshot = self.canvas.copy()

                    elif self.tool == TOOL_PENCIL:
                        self.last_pos = (mx, my)
                        pygame.draw.circle(self.canvas, self.color,
                                           (mx, my), self.brush_size)

                    elif self.tool == TOOL_ERASER:
                        self.last_pos = (mx, my)
                        pygame.draw.circle(self.canvas, WHITE,
                                           (mx, my), self.eraser_size)

            # ── Mouse UP ──────────────────────────────────────────────
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mx, my = event.pos
                if self.dragging and self.drag_start:
                    self.tm.draw_shape(
                        self.canvas, self.tool,
                        self.drag_start, (mx, my),
                        self.color, self.brush_size
                    )
                self.dragging   = False
                self.drag_start = None
                self.last_pos   = None

            # ── Mouse MOTION ──────────────────────────────────────────
            if event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
                if my >= CANVAS_H:
                    continue
                if not pygame.mouse.get_pressed()[0]:
                    continue

                if self.tool == TOOL_PENCIL and self.last_pos:
                    pygame.draw.line(self.canvas, self.color,
                                     self.last_pos, (mx, my),
                                     max(1, self.brush_size * 2))
                    pygame.draw.circle(self.canvas, self.color,
                                       (mx, my), self.brush_size)
                    self.last_pos = (mx, my)

                elif self.tool == TOOL_ERASER and self.last_pos:
                    pygame.draw.line(self.canvas, WHITE,
                                     self.last_pos, (mx, my),
                                     self.eraser_size * 2)
                    pygame.draw.circle(self.canvas, WHITE,
                                       (mx, my), self.eraser_size)
                    self.last_pos = (mx, my)

    # ── Text Tool Helpers ─────────────────────────────────────────────────
    def _start_text(self, x, y):
        self.text_active   = True
        self.text_pos      = (x, y)
        self.text_buffer   = ""
        self.text_snapshot = self.canvas.copy()

    def _handle_text_key(self, event):
        if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
            self._commit_text()
        elif event.key == pygame.K_ESCAPE:
            self._cancel_text()
        elif event.key == pygame.K_BACKSPACE:
            self.text_buffer = self.text_buffer[:-1]
        else:
            ch = event.unicode
            if ch and ch.isprintable():
                self.text_buffer += ch

    def _commit_text(self):
        """Render text permanently onto canvas."""
        if self.text_buffer and self.text_pos:
            rendered = self.text_font.render(self.text_buffer, True, self.color)
            self.canvas.blit(rendered, self.text_pos)
        self.text_active   = False
        self.text_pos      = None
        self.text_buffer   = ""
        self.text_snapshot = None

    def _cancel_text(self):
        """Restore canvas to before text was started."""
        if self.text_snapshot:
            self.canvas.blit(self.text_snapshot, (0, 0))
        self.text_active   = False
        self.text_pos      = None
        self.text_buffer   = ""
        self.text_snapshot = None

    # ── Save ──────────────────────────────────────────────────────────────
    def _save_canvas(self):
        ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"canvas_{ts}.png"
        pygame.image.save(self.canvas, filename)
        self._show_save_flash(filename)

    def _show_save_flash(self, filename):
        """Draw a brief 'Saved!' notification directly on screen."""
        self._save_msg   = f"✅ Saved: {filename}"
        self._save_timer = 150   # frames to show (2.5 s at 60fps)

    # ── Size helper ───────────────────────────────────────────────────────
    def _set_size(self, sid):
        self.size_id    = sid
        self.brush_size = BRUSH_SIZES[sid]

    # ── Draw ──────────────────────────────────────────────────────────────
    def _draw(self):
        # ── Canvas area ──────────────────────────────────────────────
        if self.dragging and self.drag_snapshot:
            self.screen.blit(self.drag_snapshot, (0, 0))
            mx, my = pygame.mouse.get_pos()
            self.tm.draw_shape(
                self.screen, self.tool,
                self.drag_start, (mx, my),
                self.color, self.brush_size
            )
        else:
            self.screen.blit(self.canvas, (0, 0))

        # Text preview (live typing)
        if self.text_active and self.text_snapshot:
            # Show snapshot + current typed text
            self.screen.blit(self.text_snapshot, (0, 0))
            rendered = self.text_font.render(
                self.text_buffer + "|", True, self.color)
            self.screen.blit(rendered, self.text_pos)

        # ── Panel ────────────────────────────────────────────────────
        pygame.draw.rect(self.screen, PANEL_BG,
                         (0, CANVAS_H, SCREEN_W, PANEL_H))
        pygame.draw.line(self.screen, (65, 65, 65),
                         (0, CANVAS_H), (SCREEN_W, CANVAS_H), 2)

        for btn in self.buttons:
            btn.draw(self.screen, self.tool)

        for sb in self.size_buttons:
            sb.draw(self.screen, self.size_id)

        # Clear button
        pygame.draw.rect(self.screen, (140, 35, 35), self.clear_rect, border_radius=5)
        pygame.draw.rect(self.screen, (210, 70, 70), self.clear_rect, 1, border_radius=5)
        ct = self.lf.render("Clear", True, WHITE)
        self.screen.blit(ct, ct.get_rect(center=self.clear_rect.center))

        # Current brush size display
        sz_lbl = self.lf.render(
            f"Brush: {self.brush_size}px", True, (160, 200, 255))
        self.screen.blit(sz_lbl, (self.clear_rect.right + 8,
                                   self.clear_rect.centery - sz_lbl.get_height() // 2))

        # Swatches
        for rect, c in self.swatches:
            pygame.draw.rect(self.screen, c, rect, border_radius=3)
            if c == self.color and self.tool != TOOL_ERASER:
                pygame.draw.rect(self.screen, ACTIVE_C, rect, 3, border_radius=3)
            else:
                pygame.draw.rect(self.screen, (20, 20, 20), rect, 1, border_radius=3)

        # Active colour preview
        prev = pygame.Rect(SCREEN_W - 58, CANVAS_H + 10, 46, 46)
        pygame.draw.rect(self.screen,
                         self.color if self.tool != TOOL_ERASER else WHITE,
                         prev, border_radius=6)
        pygame.draw.rect(self.screen, (180, 180, 180), prev, 2, border_radius=6)

        # Eraser cursor ring
        if self.tool == TOOL_ERASER:
            mx, my = pygame.mouse.get_pos()
            if my < CANVAS_H:
                pygame.draw.circle(self.screen, (160, 160, 160),
                                   (mx, my), self.eraser_size, 2)

        # Hint bar
        hint = self.lf.render(
            "P=Pencil  L=Line  R=Rect  Q=Square  C=Circle  T=R.Tri  G=Eq.Tri  "
            "D=Rhombus  E=Eraser  F=Fill  X=Text  1/2/3=Size  Del=Clear  Ctrl+S=Save",
            True, (110, 110, 110))
        self.screen.blit(hint, (6, SCREEN_H - 14))

        # Save flash notification
        if hasattr(self, '_save_timer') and self._save_timer > 0:
            self._save_timer -= 1
            alpha = min(255, self._save_timer * 5)
            fnt   = pygame.font.SysFont("consolas", 16, bold=True)
            msg   = fnt.render(self._save_msg, True, (80, 255, 120))
            msg.set_alpha(alpha)
            self.screen.blit(msg, (SCREEN_W // 2 - msg.get_width() // 2,
                                   CANVAS_H // 2 - 14))

        # Text mode indicator
        if self.text_active:
            ind = self.lf.render(
                "TEXT MODE — type, Enter=confirm, Esc=cancel", True, (255, 200, 50))
            self.screen.blit(ind, (SCREEN_W // 2 - ind.get_width() // 2,
                                   CANVAS_H - 22))

        pygame.display.flip()


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    PaintApp().run()