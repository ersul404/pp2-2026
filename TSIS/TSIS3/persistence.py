"""
persistence.py — Save / load leaderboard and settings to JSON files.
"""

import json
import os
from datetime import datetime

LEADERBOARD_FILE = "leaderboard.json"
SETTINGS_FILE    = "settings.json"

# ── Default settings ──────────────────────────────────────────────────────────
DEFAULT_SETTINGS = {
    "sound":      False,       # sound toggle (no audio assets, kept for UI)
    "car_color":  [28, 32, 38],# RGB list
    "difficulty": "normal",    # "easy" | "normal" | "hard"
}


# ─────────────────────────────────────────────
#  SETTINGS
# ─────────────────────────────────────────────
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                data = json.load(f)
            # Fill in any missing keys with defaults
            for k, v in DEFAULT_SETTINGS.items():
                data.setdefault(k, v)
            return data
        except Exception:
            pass
    return dict(DEFAULT_SETTINGS)


def save_settings(settings: dict):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)


# ─────────────────────────────────────────────
#  LEADERBOARD
# ─────────────────────────────────────────────
def load_leaderboard():
    """Return list of entry dicts sorted by score descending."""
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, "r") as f:
                data = json.load(f)
            if isinstance(data, list):
                return data
        except Exception:
            pass
    return []


def save_score(name: str, score: int, distance: int, coins: int):
    """Append a new entry and keep only the top 10."""
    board = load_leaderboard()
    entry = {
        "name":     name,
        "score":    score,
        "distance": distance,
        "coins":    coins,
        "date":     datetime.now().strftime("%Y-%m-%d"),
    }
    board.append(entry)
    board.sort(key=lambda e: e["score"], reverse=True)
    board = board[:10]
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(board, f, indent=2)
    return board