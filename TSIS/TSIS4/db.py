"""
db.py — PostgreSQL integration via psycopg2.
Handles:
  - Schema creation (players + game_sessions tables)
  - Saving a game result
  - Fetching top-10 leaderboard
  - Fetching a player's personal best
"""

import psycopg2
from psycopg2 import sql
from datetime import datetime
from config import DB_CONFIG

# ── SQL schema ────────────────────────────────────────────────────────────────
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS players (
    id       SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS game_sessions (
    id            SERIAL PRIMARY KEY,
    player_id     INTEGER REFERENCES players(id),
    score         INTEGER   NOT NULL,
    level_reached INTEGER   NOT NULL,
    played_at     TIMESTAMP DEFAULT NOW()
);
"""


def get_connection():
    """Return a new psycopg2 connection using DB_CONFIG."""
    return psycopg2.connect(**DB_CONFIG)


def init_db():
    """
    Create the players and game_sessions tables if they don't exist.
    Called once at startup.
    """
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(SCHEMA_SQL)
            conn.commit()
        return True
    except Exception as e:
        print(f"[DB] init_db error: {e}")
        return False


def get_or_create_player(username: str) -> int:
    """
    Return the player id for `username`.
    If the username doesn't exist yet, insert it first.
    """
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                # Try to find existing player
                cur.execute(
                    "SELECT id FROM players WHERE username = %s", (username,))
                row = cur.fetchone()
                if row:
                    return row[0]
                # Insert new player
                cur.execute(
                    "INSERT INTO players (username) VALUES (%s) RETURNING id",
                    (username,))
                player_id = cur.fetchone()[0]
            conn.commit()
        return player_id
    except Exception as e:
        print(f"[DB] get_or_create_player error: {e}")
        return -1


def save_result(username: str, score: int, level_reached: int):
    """
    Save a completed game session.
    Creates the player row automatically if needed.
    """
    try:
        player_id = get_or_create_player(username)
        if player_id == -1:
            return False
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO game_sessions (player_id, score, level_reached)
                       VALUES (%s, %s, %s)""",
                    (player_id, score, level_reached))
            conn.commit()
        return True
    except Exception as e:
        print(f"[DB] save_result error: {e}")
        return False


def get_leaderboard(limit: int = 10) -> list:
    """
    Return top `limit` all-time scores as a list of dicts:
      [{"rank": 1, "username": "...", "score": 999,
        "level": 5, "date": "2025-01-01"}, ...]
    """
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT p.username, gs.score, gs.level_reached,
                           gs.played_at::date
                    FROM game_sessions gs
                    JOIN players p ON p.id = gs.player_id
                    ORDER BY gs.score DESC
                    LIMIT %s
                """, (limit,))
                rows = cur.fetchall()
        return [
            {
                "rank":     i + 1,
                "username": r[0],
                "score":    r[1],
                "level":    r[2],
                "date":     str(r[3]),
            }
            for i, r in enumerate(rows)
        ]
    except Exception as e:
        print(f"[DB] get_leaderboard error: {e}")
        return []


def get_personal_best(username: str) -> int:
    """
    Return the highest score ever recorded for `username`.
    Returns 0 if no sessions found or on error.
    """
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT MAX(gs.score)
                    FROM game_sessions gs
                    JOIN players p ON p.id = gs.player_id
                    WHERE p.username = %s
                """, (username,))
                row = cur.fetchone()
        return row[0] if row and row[0] is not None else 0
    except Exception as e:
        print(f"[DB] get_personal_best error: {e}")
        return 0