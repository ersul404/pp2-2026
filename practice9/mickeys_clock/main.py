import pygame
import sys
from clock import MickeyClock

pygame.init()

screen = pygame.display.set_mode((600, 600))
pygame.display.set_caption("Mickey Clock")

clock = pygame.time.Clock()
mickey = MickeyClock(screen)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill((255, 255, 255))

    mickey.draw()

    pygame.display.flip()
    clock.tick(60)