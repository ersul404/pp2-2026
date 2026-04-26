"""
main.py — Entry point for TSIS 4 Snake.
Flow: Main Menu → Name Entry → Game → Game Over → retry / menu
      Main Menu → Leaderboard
      Main Menu → Settings
"""

import pygame
import sys
from config import WIDTH, HEIGHT, FPS
from db import init_db
from ui import MainMenu, NameEntry, SettingsScreen, LeaderboardScreen
from game import SnakeGame, load_settings


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake — TSIS 4")
    clock  = pygame.time.Clock()

    # Initialise DB (create tables if they don't exist)
    db_ok = init_db()
    if not db_ok:
        print("[WARNING] Could not connect to PostgreSQL. "
              "Leaderboard and score saving will be disabled.")

    settings    = load_settings()
    player_name = None

    while True:
        action = MainMenu().run(screen, clock)

        if action == "quit":
            pygame.quit(); sys.exit()

        elif action == "leaderboard":
            LeaderboardScreen().run(screen, clock)

        elif action == "settings":
            SettingsScreen().run(screen, clock)
            settings = load_settings()

        elif action == "play":
            if player_name is None:
                player_name = NameEntry().run(screen, clock)

            while True:
                settings = load_settings()
                game     = SnakeGame(screen, clock, player_name, settings)
                result   = game.run()   # "retry" or "menu"

                if result == "retry":
                    continue
                else:
                    player_name = None
                    break


if __name__ == "__main__":
    main()