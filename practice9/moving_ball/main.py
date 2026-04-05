import pygame
import sys
from ball import Ball

pygame.init()

WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Moving Ball")

clock = pygame.time.Clock()
ball = Ball(WIDTH, HEIGHT)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                ball.move("UP")
            if event.key == pygame.K_DOWN:
                ball.move("DOWN")
            if event.key == pygame.K_LEFT:
                ball.move("LEFT")
            if event.key == pygame.K_RIGHT:
                ball.move("RIGHT")

    screen.fill((255, 255, 255))
    pygame.draw.circle(screen, (255, 0, 0), (ball.x, ball.y), ball.radius)

    pygame.display.flip()
    clock.tick(60)