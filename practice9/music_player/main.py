import pygame
import sys
from player import MusicPlayer

pygame.init()

screen = pygame.display.set_mode((600, 400))
pygame.display.set_caption("Music Player")

font = pygame.font.Font(None, 36)
player = MusicPlayer()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                player.play()

            if event.key == pygame.K_s:
                player.stop()

            if event.key == pygame.K_n:
                player.next()

            if event.key == pygame.K_b:
                player.prev()

            if event.key == pygame.K_q:
                pygame.quit()
                sys.exit()

    screen.fill((255, 255, 255))

    text = font.render(f"Track: {player.current + 1}", True, (0, 0, 0))
    screen.blit(text, (200, 180))

    pygame.display.flip()