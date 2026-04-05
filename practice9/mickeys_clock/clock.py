import pygame
import datetime
import math


class MickeyClock:
    def __init__(self, screen):
        self.screen = screen
        self.center = (300, 300)
        self.radius = 220

        # Загружаем только руку Микки (как указано в структуре проекта)
        self.hand_img = pygame.image.load("images/mickey_hand.png")

        self.font = pygame.font.SysFont("serif", 28, bold=True)

    def draw_clock_face(self):
        """Рисует циферблат программно — без clock.png"""
        cx, cy = self.center

        # Внешнее кольцо
        pygame.draw.circle(self.screen, (200, 200, 200), (cx, cy), self.radius + 15)
        # Основной циферблат (кремовый)
        pygame.draw.circle(self.screen, (245, 232, 150), (cx, cy), self.radius)
        # Обводка
        pygame.draw.circle(self.screen, (180, 160, 60), (cx, cy), self.radius, 2)

        # Цифры 1–12
        for i in range(1, 13):
            angle = math.radians(i * 30 - 90)
            dist = self.radius - 35
            tx = int(cx + dist * math.cos(angle))
            ty = int(cy + dist * math.sin(angle))
            label = self.font.render(str(i), True, (50, 50, 50))
            rect = label.get_rect(center=(tx, ty))
            self.screen.blit(label, rect)

        # Отметки минут
        for i in range(60):
            angle = math.radians(i * 6 - 90)
            is_major = (i % 5 == 0)
            r_out = self.radius - 45
            r_in  = self.radius - (50 if is_major else 48)
            color = (80, 80, 80) if is_major else (150, 150, 150)
            width = 3 if is_major else 1
            x1 = int(cx + r_out * math.cos(angle))
            y1 = int(cy + r_out * math.sin(angle))
            x2 = int(cx + r_in  * math.cos(angle))
            y2 = int(cy + r_in  * math.sin(angle))
            pygame.draw.line(self.screen, color, (x1, y1), (x2, y2), width)

    def rotate(self, image, angle):
        rotated = pygame.transform.rotate(image, angle)
        rect = rotated.get_rect(center=self.center)
        return rotated, rect

    def draw(self):
        now = datetime.datetime.now()

        seconds = now.second
        minutes = now.minute

        # +90 чтобы 0° = 12 часов (pygame считает от 3 часов)
        sec_angle = -(seconds * 6) + 90
        min_angle = -(minutes * 6) + 90

        # 1. Сначала рисуем циферблат
        self.draw_clock_face()

        # 2. Поверх — руки Микки
        min_img, min_rect = self.rotate(self.hand_img, min_angle)
        sec_img, sec_rect = self.rotate(self.hand_img, sec_angle)

        self.screen.blit(min_img, min_rect)  # правая рука = минуты
        self.screen.blit(sec_img, sec_rect)  # левая рука = секунды