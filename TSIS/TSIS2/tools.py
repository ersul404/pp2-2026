"""
=============================================================
  tools.py — Tool logic for TSIS 2 Paint Application
  Contains:
    - Tool ID constants
    - Geometry helpers for all shapes
    - ToolManager: draw_shape(), flood_fill()
=============================================================
"""

import pygame
import math
from collections import deque

# ─────────────────────────────────────────────
#  TOOL ID CONSTANTS
# ─────────────────────────────────────────────
TOOL_PENCIL  = "pencil"
TOOL_LINE    = "line"
TOOL_RECT    = "rect"
TOOL_SQUARE  = "square"
TOOL_CIRCLE  = "circle"
TOOL_RTRI    = "right_tri"
TOOL_ETRI    = "equil_tri"
TOOL_RHOMBUS = "rhombus"
TOOL_ERASER  = "eraser"
TOOL_FILL    = "fill"
TOOL_TEXT    = "text"

# Tools that require drag interaction (mouse down → drag → mouse up)
DRAG_TOOLS = {
    TOOL_LINE,
    TOOL_RECT,
    TOOL_SQUARE,
    TOOL_CIRCLE,
    TOOL_RTRI,
    TOOL_ETRI,
    TOOL_RHOMBUS,
}


# ─────────────────────────────────────────────
#  GEOMETRY HELPERS
# ─────────────────────────────────────────────

def square_points(x1, y1, x2, y2):
    """
    Four corners of a square.
    Side length = min(|dx|, |dy|) so it stays square regardless of drag direction.
    """
    dx   = x2 - x1
    dy   = y2 - y1
    side = min(abs(dx), abs(dy))
    sx   = side * (1 if dx >= 0 else -1)
    sy   = side * (1 if dy >= 0 else -1)
    return [(x1, y1), (x1 + sx, y1), (x1 + sx, y1 + sy), (x1, y1 + sy)]


def right_triangle_points(x1, y1, x2, y2):
    """
    Right-angle triangle.
    Right angle at bottom-left (x1, y2), apex at (x1, y1), hypotenuse to (x2, y2).
    """
    return [(x1, y1), (x1, y2), (x2, y2)]


def equilateral_triangle_points(x1, y1, x2, y2):
    """
    Equilateral triangle with base along the bottom of the drag rect.
    Height = base * sqrt(3) / 2.
    """
    left   = min(x1, x2)
    right  = max(x1, x2)
    base   = right - left
    height = int(base * math.sqrt(3) / 2)
    bot    = max(y1, y2)
    apex   = (left + base // 2, bot - height)
    return [apex, (left, bot), (right, bot)]


def rhombus_points(x1, y1, x2, y2):
    """
    Rhombus (diamond) inscribed in the bounding rectangle.
    Vertices at midpoints of each side.
    """
    left   = min(x1, x2)
    right  = max(x1, x2)
    top    = min(y1, y2)
    bottom = max(y1, y2)
    cx     = (left + right)  // 2
    cy     = (top  + bottom) // 2
    return [(cx, top), (right, cy), (cx, bottom), (left, cy)]


# ─────────────────────────────────────────────
#  TOOL MANAGER
# ─────────────────────────────────────────────

class ToolManager:
    """
    Handles drawing shapes and flood-fill.
    Used both for live preview (onto screen surface)
    and final commit (onto canvas surface).
    """

    # ── Shape drawing ─────────────────────────────────────────────────────
    def draw_shape(self, surface, tool, start, end, color, thickness):
        """
        Draw the appropriate shape for `tool` onto `surface`.
        `start` and `end` are (x, y) tuples from mouse-down and current/up position.
        `thickness` is the outline stroke width in pixels.
        """
        x1, y1 = start
        x2, y2 = end
        t = max(1, thickness)

        if tool == TOOL_LINE:
            # Straight line between two points
            pygame.draw.line(surface, color, (x1, y1), (x2, y2), t)

        elif tool == TOOL_RECT:
            left   = min(x1, x2)
            top    = min(y1, y2)
            w      = abs(x2 - x1)
            h      = abs(y2 - y1)
            if w > 1 and h > 1:
                pygame.draw.rect(surface, color, (left, top, w, h), t)

        elif tool == TOOL_SQUARE:
            pts = square_points(x1, y1, x2, y2)
            # Only draw if the square has non-zero size
            if abs(x2 - x1) > 2 and abs(y2 - y1) > 2:
                pygame.draw.polygon(surface, color, pts, t)

        elif tool == TOOL_CIRCLE:
            cx     = (x1 + x2) // 2
            cy     = (y1 + y2) // 2
            radius = int(math.hypot(x2 - x1, y2 - y1) / 2)
            if radius > 1:
                pygame.draw.circle(surface, color, (cx, cy), radius, t)

        elif tool == TOOL_RTRI:
            pts = right_triangle_points(x1, y1, x2, y2)
            pygame.draw.polygon(surface, color, pts, t)

        elif tool == TOOL_ETRI:
            pts = equilateral_triangle_points(x1, y1, x2, y2)
            if len(pts) == 3:
                pygame.draw.polygon(surface, color, pts, t)

        elif tool == TOOL_RHOMBUS:
            pts = rhombus_points(x1, y1, x2, y2)
            if abs(x2 - x1) > 2 and abs(y2 - y1) > 2:
                pygame.draw.polygon(surface, color, pts, t)

    # ── Flood Fill ────────────────────────────────────────────────────────
    def flood_fill(self, surface, x, y, fill_color):
        """
        Iterative BFS flood fill using pygame.Surface.get_at() / set_at().
        Fills all connected pixels of the same color as (x, y)
        with fill_color. Stops at boundaries of a different color.

        Parameters:
            surface    — pygame.Surface to fill (the canvas)
            x, y       — starting pixel coordinates (click position)
            fill_color — (R, G, B) tuple of the replacement color
        """
        # Clamp click to surface bounds
        sw, sh = surface.get_size()
        if not (0 <= x < sw and 0 <= y < sh):
            return

        # Get the color we are replacing (target color)
        target = surface.get_at((x, y))[:3]   # ignore alpha

        # Normalise fill color to (R, G, B)
        fc = fill_color[:3]

        # Nothing to do if target already matches fill
        if target == fc:
            return

        # BFS queue — use a deque for O(1) popleft
        queue   = deque()
        queue.append((x, y))
        visited = set()
        visited.add((x, y))

        while queue:
            cx, cy = queue.popleft()

            # Skip if this pixel has drifted from the target color
            # (can happen at shape edges due to anti-aliasing or
            #  if we've already filled it)
            current = surface.get_at((cx, cy))[:3]
            if current != target:
                continue

            # Paint this pixel
            surface.set_at((cx, cy), fc)

            # Check all 4 neighbours (cardinal directions only)
            for nx, ny in ((cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)):
                if (0 <= nx < sw and 0 <= ny < sh
                        and (nx, ny) not in visited):
                    visited.add((nx, ny))
                    queue.append((nx, ny))