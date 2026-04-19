"""
=============================================================
  PAINT APPLICATION — Extended Version
  Based on: https://nerdparadise.com/programming/pygame/part6
  Extra features:
    - Draw rectangle (R key or button)
    - Draw circle   (C key or button)
    - Eraser tool   (E key or button)
    - Color palette picker (click to select)
    - Brush-size slider
    - Clear canvas  (Delete key)
    - Fully commented code
=============================================================
"""

import pygame
import sys
import math

# ─────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────
SCREEN_W   = 900
SCREEN_H   = 650
PANEL_H    = 90        # height of the tool panel at the bottom
CANVAS_H   = SCREEN_H - PANEL_H

FPS        = 60

# Tool identifiers
TOOL_PEN       = "pen"
TOOL_RECT      = "rect"
TOOL_CIRCLE    = "circle"
TOOL_ERASER    = "eraser"

# Predefined colour palette
PALETTE = [
    (0,   0,   0),    # black
    (255, 255, 255),  # white
    (220, 30,  30),   # red
    (30,  180, 30),   # green
    (30,  30,  220),  # blue
    (255, 200, 0),    # yellow
    (255, 140, 0),    # orange
    (180, 0,   180),  # purple
    (0,   200, 200),  # cyan
    (180, 100, 40),   # brown
    (255, 182, 193),  # pink
    (128, 128, 128),  # gray
    (0,   100, 0),    # dark green
    (0,   0,   128),  # navy
    (255, 69,  0),    # orange-red
    (173, 216, 230),  # light blue
]

# Panel colours
PANEL_BG   = (45,  45,  45)
PANEL_LINE = (80,  80,  80)
ACTIVE_C   = (255, 220, 50)     # highlight for active tool/colour


# ─────────────────────────────────────────────
#  BUTTON (UI element in the panel)
# ─────────────────────────────────────────────
class Button:
    """Simple clickable rectangle with a text label."""

    def __init__(self, rect, label, tool_id):
        self.rect    = pygame.Rect(rect)
        self.label   = label
        self.tool_id = tool_id
        self.font    = pygame.font.SysFont("consolas", 13, bold=True)

    def draw(self, surface, active_tool):
        """Draw button; highlight if it is the currently active tool."""
        color  = ACTIVE_C if self.tool_id == active_tool else (90, 90, 90)
        border = (255, 255, 255) if self.tool_id == active_tool else (60, 60, 60)
        pygame.draw.rect(surface, color,  self.rect, border_radius=6)
        pygame.draw.rect(surface, border, self.rect, 2, border_radius=6)

        txt = self.font.render(self.label, True, BLACK if self.tool_id == active_tool else (220, 220, 220))
        surface.blit(txt, txt.get_rect(center=self.rect.center))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


# ─────────────────────────────────────────────
#  PAINT APPLICATION
# ─────────────────────────────────────────────

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

class PaintApp:
    """Main paint application."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Paint — Pen / Rect / Circle / Eraser")
        self.clock  = pygame.font.SysFont("consolas", 14)
        self.fps    = pygame.time.Clock()

        # Canvas — a separate surface we draw on permanently
        self.canvas = pygame.Surface((SCREEN_W, CANVAS_H))
        self.canvas.fill(WHITE)

        # Tool state
        self.tool        = TOOL_PEN
        self.color       = (0, 0, 0)          # current drawing colour
        self.brush_size  = 5                  # radius in pixels
        self.eraser_size = 20

        # Shape-drag state (for rect and circle)
        self.dragging      = False
        self.drag_start    = None             # (x, y) where mouse went down
        self.drag_snapshot = None             # copy of canvas before drag

        # Last pen position (for smooth lines)
        self.last_pos = None

        # Build UI buttons and palette
        self._build_ui()

    # ── UI Layout ────────────────────────────────────────────────────────
    def _build_ui(self):
        """Create tool buttons and colour-swatch layout."""
        # Y position of panel top
        py = CANVAS_H + 5

        # Tool buttons
        btn_w, btn_h = 80, 36
        gap = 8
        x0  = 10
        self.buttons = [
            Button((x0 + i * (btn_w + gap), py + 5, btn_w, btn_h), label, tool)
            for i, (label, tool) in enumerate([
                ("✏  Pen",    TOOL_PEN),
                ("▭  Rect",   TOOL_RECT),
                ("○  Circle", TOOL_CIRCLE),
                ("⌫  Eraser", TOOL_ERASER),
            ])
        ]

        # Brush-size controls (+/-)
        self.size_dec_rect = pygame.Rect(x0 + 4 * (btn_w + gap), py + 5,  32, btn_h)
        self.size_inc_rect = pygame.Rect(x0 + 4 * (btn_w + gap) + 36, py + 5, 32, btn_h)

        # Clear button
        self.clear_rect = pygame.Rect(x0 + 4 * (btn_w + gap) + 76, py + 5, 70, btn_h)

        # Colour palette swatches
        swatch_size = 26
        swatch_gap  = 4
        palette_x   = x0 + 5 * (btn_w + gap) + 76 + 10
        palette_y   = py + 6
        self.swatches = []
        cols_per_row = 8
        for i, c in enumerate(PALETTE):
            cx = palette_x + (i % cols_per_row) * (swatch_size + swatch_gap)
            cy = palette_y + (i // cols_per_row) * (swatch_size + swatch_gap)
            self.swatches.append((pygame.Rect(cx, cy, swatch_size, swatch_size), c))

        # Font for labels
        self.label_font = pygame.font.SysFont("consolas", 13, bold=True)

    # ── Main Loop ────────────────────────────────────────────────────────
    def run(self):
        while True:
            self.fps.tick(FPS)
            self._handle_events()
            self._draw()

    # ── Events ───────────────────────────────────────────────────────────
    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # ── Keyboard shortcuts ──────────────────────────────────
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    self.tool = TOOL_PEN
                if event.key == pygame.K_r:
                    self.tool = TOOL_RECT
                if event.key == pygame.K_c:
                    self.tool = TOOL_CIRCLE
                if event.key == pygame.K_e:
                    self.tool = TOOL_ERASER
                if event.key == pygame.K_DELETE or event.key == pygame.K_BACKSPACE:
                    self.canvas.fill(WHITE)   # clear canvas

            # ── Mouse button DOWN ───────────────────────────────────
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos

                # Check tool buttons
                for btn in self.buttons:
                    if btn.is_clicked(event.pos):
                        self.tool = btn.tool_id
                        return

                # Brush size dec/inc
                if self.size_dec_rect.collidepoint(event.pos):
                    self.brush_size  = max(1, self.brush_size - 2)
                    self.eraser_size = max(5, self.eraser_size - 5)
                    return
                if self.size_inc_rect.collidepoint(event.pos):
                    self.brush_size  = min(50, self.brush_size + 2)
                    self.eraser_size = min(80, self.eraser_size + 5)
                    return

                # Clear button
                if self.clear_rect.collidepoint(event.pos):
                    self.canvas.fill(WHITE)
                    return

                # Colour swatches
                for rect, c in self.swatches:
                    if rect.collidepoint(event.pos):
                        self.color = c
                        # Switching to a colour automatically selects Pen
                        if self.tool == TOOL_ERASER:
                            self.tool = TOOL_PEN
                        return

                # Drawing on canvas
                if my < CANVAS_H:
                    if self.tool in (TOOL_RECT, TOOL_CIRCLE):
                        # Start shape drag: save canvas snapshot
                        self.dragging      = True
                        self.drag_start    = (mx, my)
                        self.drag_snapshot = self.canvas.copy()
                    elif self.tool == TOOL_PEN:
                        # Start pen stroke
                        self.last_pos = (mx, my)
                        pygame.draw.circle(self.canvas, self.color,
                                           (mx, my), self.brush_size)
                    elif self.tool == TOOL_ERASER:
                        self.last_pos = (mx, my)
                        pygame.draw.circle(self.canvas, WHITE,
                                           (mx, my), self.eraser_size)

            # ── Mouse button UP ─────────────────────────────────────
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mx, my = event.pos
                if self.dragging and self.drag_start and my < CANVAS_H:
                    # Commit the final shape to the canvas
                    self._draw_shape_on_canvas(self.drag_start, (mx, my))
                self.dragging   = False
                self.drag_start = None
                self.last_pos   = None

            # ── Mouse MOTION ────────────────────────────────────────
            if event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
                if my >= CANVAS_H:
                    continue   # cursor is in the panel, not the canvas

                buttons = pygame.mouse.get_pressed()
                if not buttons[0]:
                    continue   # left button not held

                if self.tool == TOOL_PEN and self.last_pos:
                    # Draw a line from last position to current
                    pygame.draw.line(self.canvas, self.color,
                                     self.last_pos, (mx, my),
                                     self.brush_size * 2)
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

                # For RECT / CIRCLE: preview is handled in _draw()

    # ── Shape Drawing ────────────────────────────────────────────────────
    def _draw_shape_on_canvas(self, start, end):
        """
        Permanently draw the selected shape (rect or circle)
        onto self.canvas using the drag start/end points.
        """
        x1, y1 = start
        x2, y2 = end

        if self.tool == TOOL_RECT:
            # Normalise so x1 < x2, y1 < y2
            left   = min(x1, x2)
            top    = min(y1, y2)
            width  = abs(x2 - x1)
            height = abs(y2 - y1)
            if width > 1 and height > 1:
                pygame.draw.rect(self.canvas, self.color,
                                 (left, top, width, height),
                                 max(1, self.brush_size))

        elif self.tool == TOOL_CIRCLE:
            # Use the distance from start to end as the radius
            cx    = (x1 + x2) // 2
            cy    = (y1 + y2) // 2
            radius = int(math.hypot(x2 - x1, y2 - y1) / 2)
            if radius > 1:
                pygame.draw.circle(self.canvas, self.color,
                                   (cx, cy), radius,
                                   max(1, self.brush_size))

    def _draw_shape_preview(self, surface, start, end):
        """
        Draw a ghost preview of the shape being dragged,
        directly onto the display surface (not the canvas).
        """
        x1, y1 = start
        x2, y2 = end

        if self.tool == TOOL_RECT:
            left   = min(x1, x2)
            top    = min(y1, y2)
            width  = abs(x2 - x1)
            height = abs(y2 - y1)
            if width > 1 and height > 1:
                pygame.draw.rect(surface, self.color,
                                 (left, top, width, height),
                                 max(1, self.brush_size))

        elif self.tool == TOOL_CIRCLE:
            cx     = (x1 + x2) // 2
            cy     = (y1 + y2) // 2
            radius = int(math.hypot(x2 - x1, y2 - y1) / 2)
            if radius > 1:
                pygame.draw.circle(surface, self.color,
                                   (cx, cy), radius,
                                   max(1, self.brush_size))

    # ── Draw ─────────────────────────────────────────────────────────────
    def _draw(self):
        # Copy canvas to screen
        if self.dragging and self.drag_snapshot:
            # Show snapshot + live preview
            self.screen.blit(self.drag_snapshot, (0, 0))
            mx, my = pygame.mouse.get_pos()
            self._draw_shape_preview(self.screen, self.drag_start, (mx, my))
        else:
            self.screen.blit(self.canvas, (0, 0))

        # Panel background
        pygame.draw.rect(self.screen, PANEL_BG,
                         (0, CANVAS_H, SCREEN_W, PANEL_H))
        pygame.draw.line(self.screen, PANEL_LINE,
                         (0, CANVAS_H), (SCREEN_W, CANVAS_H), 2)

        # Tool buttons
        for btn in self.buttons:
            btn.draw(self.screen, self.tool)

        # Brush size controls
        self._draw_size_controls()

        # Clear button
        pygame.draw.rect(self.screen, (160, 40, 40), self.clear_rect, border_radius=6)
        pygame.draw.rect(self.screen, (220, 80, 80), self.clear_rect, 2, border_radius=6)
        clr_t = self.label_font.render("Clear", True, WHITE)
        self.screen.blit(clr_t, clr_t.get_rect(center=self.clear_rect.center))

        # Colour swatches
        for rect, c in self.swatches:
            pygame.draw.rect(self.screen, c, rect, border_radius=4)
            # Highlight active colour
            if c == self.color and self.tool != TOOL_ERASER:
                pygame.draw.rect(self.screen, ACTIVE_C, rect, 3, border_radius=4)
            else:
                pygame.draw.rect(self.screen, (30, 30, 30), rect, 1, border_radius=4)

        # Current colour preview square
        preview_rect = pygame.Rect(SCREEN_W - 60, CANVAS_H + 10, 48, 48)
        pygame.draw.rect(self.screen, self.color if self.tool != TOOL_ERASER else WHITE,
                         preview_rect, border_radius=6)
        pygame.draw.rect(self.screen, (200, 200, 200), preview_rect, 2, border_radius=6)

        # Eraser cursor circle
        if self.tool == TOOL_ERASER:
            mx, my = pygame.mouse.get_pos()
            if my < CANVAS_H:
                pygame.draw.circle(self.screen, (150, 150, 150),
                                   (mx, my), self.eraser_size, 2)

        # Keyboard hint
        hint = self.label_font.render(
            "P=Pen  R=Rect  C=Circle  E=Eraser  Del=Clear", True, (160, 160, 160))
        self.screen.blit(hint, (10, SCREEN_H - 18))

        pygame.display.flip()

    def _draw_size_controls(self):
        """Draw the + / - buttons for brush size and the current size label."""
        # Dec button  (−)
        pygame.draw.rect(self.screen, (80, 80, 80),  self.size_dec_rect, border_radius=6)
        pygame.draw.rect(self.screen, (120, 120, 120), self.size_dec_rect, 1, border_radius=6)
        t = self.label_font.render("−", True, WHITE)
        self.screen.blit(t, t.get_rect(center=self.size_dec_rect.center))

        # Inc button  (+)
        pygame.draw.rect(self.screen, (80, 80, 80),  self.size_inc_rect, border_radius=6)
        pygame.draw.rect(self.screen, (120, 120, 120), self.size_inc_rect, 1, border_radius=6)
        t = self.label_font.render("+", True, WHITE)
        self.screen.blit(t, t.get_rect(center=self.size_inc_rect.center))

        # Size label between the two buttons
        size_val = self.eraser_size if self.tool == TOOL_ERASER else self.brush_size
        lbl = self.label_font.render(f"Size:{size_val}", True, (200, 200, 200))
        lbl_x = self.size_inc_rect.right + 4
        lbl_y = self.size_dec_rect.centery - lbl.get_height() // 2
        self.screen.blit(lbl, (lbl_x, lbl_y))


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = PaintApp()
    app.run()