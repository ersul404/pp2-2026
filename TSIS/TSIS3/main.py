"""
main.py — Entry point for TSIS 3 Racer.
Manages the flow between screens:
  Main Menu → Name Entry → Game → Game Over → (retry / menu)
  Main Menu → Leaderboard
  Main Menu → Settings
"""

import pygame
import sys
from ui import MainMenu, NameEntry, SettingsScreen, LeaderboardScreen
from racer import RacerGame
from persistence import load_settings

SW, SH = 600, 700
FPS    = 60


def main():
    pygame.init()
    screen = pygame.display.set_mode((SW, SH))
    pygame.display.set_caption("Mercedes Racer — TSIS 3")
    clock  = pygame.time.Clock()

    # Load saved settings once at startup
    settings = load_settings()

    # Player name persists across retries in the same session
    player_name = None

    while True:
        # ── Main Menu ─────────────────────────────────────────────────
        action = MainMenu().run(screen, clock)

        if action == "quit":
            pygame.quit()
            sys.exit()

        elif action == "leaderboard":
            LeaderboardScreen().run(screen, clock)

        elif action == "settings":
            SettingsScreen().run(screen, clock)
            settings = load_settings()   # reload after save

        elif action == "play":
            # Ask for name once per session (or if they haven't set one)
            if player_name is None:
                player_name = NameEntry().run(screen, clock)

            # Game loop — supports retry without re-entering name
            while True:
                settings = load_settings()
                game     = RacerGame(screen, clock, player_name, settings)
                result   = game.run()   # returns "retry" or "menu"

                if result == "retry":
                    continue            # re-create game with same name
                else:
                    player_name = None  # reset name for next play session
                    break               # back to main menu


if __name__ == "__main__":
    main()