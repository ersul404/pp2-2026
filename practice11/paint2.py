"""
=============================================================
  PAINT APPLICATION — Practice 11 (extends Practice 10)
  NEW tools added for Practice 11:
    1. Square          — drag to set side length (forced equal W & H)
    2. Right Triangle  — drag defines bounding box; right angle bottom-left
    3. Equilateral Triangle — drag sets base width; height auto-calculated
    4. Rhombus (Diamond) — drag defines bounding box; 4-sided polygon
  All four shapes show a live preview while dragging.
  Fully commented code.
=============================================================
"""

import pygame
import sys
import math

# ─────────────────────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────────────────────
SCREEN_W  = 1000          # wider to fit more tool buttons
SCREEN_H  = 680
PANEL_H   = 95            # tool panel at the bottom
CANVAS_H  = SCREEN_H - PANEL_H
FPS       = 60

# ── Tool IDs ─────────────────────────────────────────────────
TOOL_PEN       = "pen"
TOOL_RECT      = "rect"
TOOL_SQUARE    = "square"          # NEW Practice 11
TOOL_CIRCLE    = "circle"
TOOL_RTRI      = "right_tri"       # NEW Practice 11
TOOL_ETRI      = "equil_tri"       # NEW Practice 11
TOOL_RHOMBUS   = "rhombus"         # NEW Practice 11
TOOL_ERASER    = "eraser"

# Tools that use drag-to-draw interaction
DRAG_TOOLS = {TOOL_RECT, TOOL_SQUARE, TOOL_CIRCLE,
              TOOL_RTRI, TOOL_ETRI, TOOL_RHOMBUS}

# Colour palette (16 swatches)
PALETTE = [
    (0,   0,   0),   (255, 255, 255), (220, 30,  30),  (30,  180, 30),
    (30,  30,  220), (255, 200, 0),   (255, 140, 0),   (180, 0,   180),
    (0,   200, 200), (180, 100, 40),  (255, 182, 193), (128, 128, 128),
    (0,   100, 0),   (0,   0,   128), (255, 69,  0),   (173, 216, 230),
]

# UI colours
BLACK    = (0,   0,   0)
WHITE    = (255, 255, 255)
PANEL_BG = (40,  40,  40)
ACTIVE_C = (255, 220, 50)


# ─────────────────────────────────────────────────────────────
#  BUTTON
# ─────────────────────────────────────────────────────────────
class Button:
    """A labelled clickable button in the tool panel."""

    def __init__(self, rect, label, tool_id):
        self.rect    = pygame.Rect(rect)
        self.label   = label
        self.tool_id = tool_id
        self.font    = pygame.font.SysFont("consolas", 12, bold=True)

    def draw(self, surface, active_tool):
        """Render with highlight if this is the active tool."""
        active = self.tool_id == active_tool
        bg     = ACTIVE_C          if active else (85, 85, 85)
        border = (255, 255, 255)   if active else (55, 55, 55)
        pygame.draw.rect(surface, bg,     self.rect, border_radius=6)
        pygame.draw.rect(surface, border, self.rect, 2, border_radius=6)
        txt = self.font.render(self.label, True, BLACK if active else (220, 220, 220))
        surface.blit(txt, txt.get_rect(center=self.rect.center))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


# ─────────────────────────────────────────────────────────────
#  GEOMETRY HELPERS
# ─────────────────────────────────────────────────────────────
def square_points(x1, y1, x2, y2):
    """
    Return the four corners of a square whose diagonal goes from
    (x1,y1) to (x2,y2). The side length equals the smaller of
    |dx| and |dy| so the shape is always square.
    """
    dx = x2 - x1
    dy = y2 - y1
    side = min(abs(dx), abs(dy))
    sx   = side * (1 if dx >= 0 else -1)
    sy   = side * (1 if dy >= 0 else -1)
    return [(x1, y1), (x1 + sx, y1), (x1 + sx, y1 + sy), (x1, y1 + sy)]


def right_triangle_points(x1, y1, x2, y2):
    """
    Right triangle with:
      - right angle at bottom-left  (x1, y2)
      - top vertex at               (x1, y1)
      - bottom-right vertex at      (x2, y2)
    """
    return [(x1, y1), (x1, y2), (x2, y2)]


def equilateral_triangle_points(x1, y1, x2, y2):
    """
    Equilateral triangle whose base stretches from x1 to x2
    at the bottom row y2. The apex is centred above at the
    correct height: h = base * sqrt(3) / 2.
    The triangle is positioned so the drag rectangle
    tightly fits the shape.
    """
    base   = abs(x2 - x1)
    height = int(base * math.sqrt(3) / 2)
    # Ensure the apex direction follows the drag direction
    left  = min(x1, x2)
    right = max(x1, x2)
    bot   = max(y1, y2)
    apex  = (left + (right - left) // 2, bot - height)
    return [apex, (left, bot), (right, bot)]


def rhombus_points(x1, y1, x2, y2):
    """
    Rhombus (diamond) inscribed in the bounding rectangle
    defined by (x1,y1) – (x2,y2). The four vertices are at
    the midpoints of each side of the bounding box.
    """
    left   = min(x1, x2)
    right  = max(x1, x2)
    top    = min(y1, y2)
    bottom = max(y1, y2)
    cx     = (left + right)  // 2
    cy     = (top  + bottom) // 2
    return [(cx, top), (right, cy), (cx, bottom), (left, cy)]


# ─────────────────────────────────────────────────────────────
#  PAINT APPLICATION
# ─────────────────────────────────────────────────────────────
class PaintApp:
    """Main paint application — extended for Practice 11."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Paint — Practice 11")
        self.fps = pygame.time.Clock()

        # Persistent drawing canvas (separate surface)
        self.canvas = pygame.Surface((SCREEN_W, CANVAS_H))
        self.canvas.fill(WHITE)

        # Current tool state
        self.tool        = TOOL_PEN
        self.color       = BLACK
        self.brush_size  = 5     # pen/shape outline thickness
        self.eraser_size = 20

        # Drag state (used by all shape tools)
        self.dragging      = False
        self.drag_start    = None   # (x, y) of mouse-down
        self.drag_snapshot = None   # canvas snapshot before drag (for preview)

        # Pen trail tracking
        self.last_pos = None

        self._build_ui()

    # ── UI Layout ─────────────────────────────────────────────────────────
    def _build_ui(self):
        """Create all tool buttons, size controls, clear button, palette."""
        py    = CANVAS_H + 6    # top of panel content area
        btn_w = 80
        btn_h = 34
        gap   = 6
        x0    = 8

        # All tool buttons in one flat list
        # (Practice 10 tools + 4 new Practice 11 tools)
        tool_defs = [
            ("✏ Pen",     TOOL_PEN),
            ("▭ Rect",    TOOL_RECT),
            ("■ Square",  TOOL_SQUARE),     # NEW
            ("○ Circle",  TOOL_CIRCLE),
            ("◺ R.Tri",   TOOL_RTRI),       # NEW
            ("△ Eq.Tri",  TOOL_ETRI),       # NEW
            ("◇ Rhombus", TOOL_RHOMBUS),    # NEW
            ("⌫ Eraser",  TOOL_ERASER),
        ]

        self.buttons = [
            Button(
                (x0 + i * (btn_w + gap), py + 2, btn_w, btn_h),
                label, tool_id
            )
            for i, (label, tool_id) in enumerate(tool_defs)
        ]

        # Size dec / inc buttons (placed below the main row)
        row2_y = py + btn_h + 10
        self.size_dec_rect = pygame.Rect(x0,      row2_y, 30, 24)
        self.size_inc_rect = pygame.Rect(x0 + 34, row2_y, 30, 24)

        # Clear canvas button
        self.clear_rect = pygame.Rect(x0 + 72, row2_y, 64, 24)

        # Colour palette swatches (two rows of 8)
        sw    = 24
        gap_s = 4
        pal_x = x0 + len(tool_defs) * (btn_w + gap) + 12
        pal_y = py + 2
        self.swatches = []
        for i, c in enumerate(PALETTE):
            cx = pal_x + (i % 8) * (sw + gap_s)
            cy = pal_y + (i // 8) * (sw + gap_s)
            self.swatches.append((pygame.Rect(cx, cy, sw, sw), c))

        # Label font used for small UI text
        self.lf = pygame.font.SysFont("consolas", 12, bold=True)

    # ── Main Loop ─────────────────────────────────────────────────────────
    def run(self):
        while True:
            self.fps.tick(FPS)
            self._handle_events()
            self._draw()

    # ── Events ────────────────────────────────────────────────────────────
    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            # ── Keyboard shortcuts ────────────────────────────────────
            if event.type == pygame.KEYDOWN:
                shortcuts = {
                    pygame.K_p: TOOL_PEN,
                    pygame.K_r: TOOL_RECT,
                    pygame.K_s: TOOL_SQUARE,    # S = Square
                    pygame.K_c: TOOL_CIRCLE,
                    pygame.K_t: TOOL_RTRI,      # T = Triangle (right)
                    pygame.K_g: TOOL_ETRI,      # G = (e)Quilateral / G key
                    pygame.K_d: TOOL_RHOMBUS,   # D = Diamond/rhombus
                    pygame.K_e: TOOL_ERASER,
                }
                if event.key in shortcuts:
                    self.tool = shortcuts[event.key]
                if event.key in (pygame.K_DELETE, pygame.K_BACKSPACE):
                    self.canvas.fill(WHITE)     # clear canvas

            # ── Mouse down ────────────────────────────────────────────
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos

                # Tool buttons
                for btn in self.buttons:
                    if btn.is_clicked(event.pos):
                        self.tool = btn.tool_id
                        return

                # Size controls
                if self.size_dec_rect.collidepoint(event.pos):
                    self.brush_size  = max(1,  self.brush_size  - 1)
                    self.eraser_size = max(5,  self.eraser_size - 5)
                    return
                if self.size_inc_rect.collidepoint(event.pos):
                    self.brush_size  = min(50, self.brush_size  + 1)
                    self.eraser_size = min(80, self.eraser_size + 5)
                    return

                # Clear
                if self.clear_rect.collidepoint(event.pos):
                    self.canvas.fill(WHITE)
                    return

                # Palette
                for rect, c in self.swatches:
                    if rect.collidepoint(event.pos):
                        self.color = c
                        if self.tool == TOOL_ERASER:
                            self.tool = TOOL_PEN
                        return

                # Drawing on canvas
                if my < CANVAS_H:
                    if self.tool in DRAG_TOOLS:
                        # Save canvas snapshot so we can restore during preview
                        self.dragging      = True
                        self.drag_start    = (mx, my)
                        self.drag_snapshot = self.canvas.copy()
                    elif self.tool == TOOL_PEN:
                        self.last_pos = (mx, my)
                        pygame.draw.circle(self.canvas, self.color,
                                           (mx, my), self.brush_size)
                    elif self.tool == TOOL_ERASER:
                        self.last_pos = (mx, my)
                        pygame.draw.circle(self.canvas, WHITE,
                                           (mx, my), self.eraser_size)

            # ── Mouse up ──────────────────────────────────────────────
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mx, my = event.pos
                if self.dragging and self.drag_start:
                    # Commit final shape to canvas
                    self._draw_shape(self.canvas, self.drag_start, (mx, my))
                self.dragging   = False
                self.drag_start = None
                self.last_pos   = None

            # ── Mouse motion ──────────────────────────────────────────
            if event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
                if my >= CANVAS_H:
                    continue
                if not pygame.mouse.get_pressed()[0]:
                    continue

                if self.tool == TOOL_PEN and self.last_pos:
                    # Smooth stroke: line segment + circle cap
                    pygame.draw.line(self.canvas, self.color,
                                     self.last_pos, (mx, my), self.brush_size * 2)
                    pygame.draw.circle(self.canvas, self.color,
                                       (mx, my), self.brush_size)
                    self.last_pos = (mx, my)

                elif self.tool == TOOL_ERASER and self.last_pos:
                    pygame.draw.line(self.canvas, WHITE,
                                     self.last_pos, (mx, my), self.eraser_size * 2)
                    pygame.draw.circle(self.canvas, WHITE,
                                       (mx, my), self.eraser_size)
                    self.last_pos = (mx, my)
                # Shape tools: preview is handled in _draw()

    # ── Shape rendering ───────────────────────────────────────────────────
    def _draw_shape(self, surface, start, end):
        """
        Draw the active shape tool's geometry onto `surface`.
        Called both for the live preview (onto screen) and
        final commit (onto self.canvas).
        """
        x1, y1 = start
        x2, y2 = end
        t = self.brush_size   # outline thickness
        c = self.color

        if self.tool == TOOL_RECT:
            # Rectangle: normalise coords and draw
            left   = min(x1, x2)
            top    = min(y1, y2)
            w      = abs(x2 - x1)
            h      = abs(y2 - y1)
            if w > 1 and h > 1:
                pygame.draw.rect(surface, c, (left, top, w, h), max(1, t))

        elif self.tool == TOOL_SQUARE:
            # Square: force equal width and height
            pts = square_points(x1, y1, x2, y2)
            if len(pts) == 4:
                pygame.draw.polygon(surface, c, pts, max(1, t))

        elif self.tool == TOOL_CIRCLE:
            # Circle: centre = midpoint, radius = half-diagonal
            cx     = (x1 + x2) // 2
            cy     = (y1 + y2) // 2
            radius = int(math.hypot(x2 - x1, y2 - y1) / 2)
            if radius > 1:
                pygame.draw.circle(surface, c, (cx, cy), radius, max(1, t))

        elif self.tool == TOOL_RTRI:
            # Right triangle: right angle at bottom-left corner
            pts = right_triangle_points(x1, y1, x2, y2)
            pygame.draw.polygon(surface, c, pts, max(1, t))

        elif self.tool == TOOL_ETRI:
            # Equilateral triangle: base = drag width, height auto-computed
            pts = equilateral_triangle_points(x1, y1, x2, y2)
            if len(pts) == 3:
                pygame.draw.polygon(surface, c, pts, max(1, t))

        elif self.tool == TOOL_RHOMBUS:
            # Rhombus: 4 vertices at midpoints of the bounding box
            pts = rhombus_points(x1, y1, x2, y2)
            if abs(x2 - x1) > 2 and abs(y2 - y1) > 2:
                pygame.draw.polygon(surface, c, pts, max(1, t))

    # ── Draw ──────────────────────────────────────────────────────────────
    def _draw(self):
        # ── Canvas ───────────────────────────────────────────────────
        if self.dragging and self.drag_snapshot:
            # Restore snapshot and draw live preview on top
            self.screen.blit(self.drag_snapshot, (0, 0))
            mx, my = pygame.mouse.get_pos()
            self._draw_shape(self.screen, self.drag_start, (mx, my))
        else:
            self.screen.blit(self.canvas, (0, 0))

        # ── Panel ────────────────────────────────────────────────────
        pygame.draw.rect(self.screen, PANEL_BG,
                         (0, CANVAS_H, SCREEN_W, PANEL_H))
        pygame.draw.line(self.screen, (70, 70, 70),
                         (0, CANVAS_H), (SCREEN_W, CANVAS_H), 2)

        # Tool buttons
        for btn in self.buttons:
            btn.draw(self.screen, self.tool)

        # Size controls
        self._draw_size_controls()

        # Clear button
        pygame.draw.rect(self.screen, (150, 35, 35), self.clear_rect, border_radius=5)
        pygame.draw.rect(self.screen, (220, 80, 80), self.clear_rect, 1, border_radius=5)
        ct = self.lf.render("Clear", True, WHITE)
        self.screen.blit(ct, ct.get_rect(center=self.clear_rect.center))

        # Palette swatches
        for rect, c in self.swatches:
            pygame.draw.rect(self.screen, c, rect, border_radius=3)
            border_c = ACTIVE_C if (c == self.color and self.tool != TOOL_ERASER) \
                       else (20, 20, 20)
            bw = 3 if (c == self.color and self.tool != TOOL_ERASER) else 1
            pygame.draw.rect(self.screen, border_c, rect, bw, border_radius=3)

        # Current colour preview
        prev = pygame.Rect(SCREEN_W - 56, CANVAS_H + 8, 44, 44)
        pygame.draw.rect(self.screen, self.color if self.tool != TOOL_ERASER else WHITE,
                         prev, border_radius=6)
        pygame.draw.rect(self.screen, (180, 180, 180), prev, 2, border_radius=6)

        # Eraser cursor ring
        if self.tool == TOOL_ERASER:
            mx, my = pygame.mouse.get_pos()
            if my < CANVAS_H:
                pygame.draw.circle(self.screen, (150, 150, 150),
                                   (mx, my), self.eraser_size, 2)

        # Keyboard hint bar
        hint = self.lf.render(
            "P=Pen  R=Rect  S=Square  C=Circle  T=R.Tri  G=Eq.Tri  D=Rhombus  E=Eraser  Del=Clear",
            True, (130, 130, 130))
        self.screen.blit(hint, (8, SCREEN_H - 16))

        pygame.display.flip()

    def _draw_size_controls(self):
        """Render the − and + brush-size buttons and the current size label."""
        for rect, label in [(self.size_dec_rect, "−"), (self.size_inc_rect, "+")]:
            pygame.draw.rect(self.screen, (75, 75, 75), rect, border_radius=5)
            pygame.draw.rect(self.screen, (110, 110, 110), rect, 1, border_radius=5)
            t = self.lf.render(label, True, WHITE)
            self.screen.blit(t, t.get_rect(center=rect.center))

        sz  = self.eraser_size if self.tool == TOOL_ERASER else self.brush_size
        lbl = self.lf.render(f"Sz:{sz}", True, (200, 200, 200))
        self.screen.blit(lbl, (self.size_inc_rect.right + 4,
                                self.size_inc_rect.centery - lbl.get_height() // 2))


# ─────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    PaintApp().run()