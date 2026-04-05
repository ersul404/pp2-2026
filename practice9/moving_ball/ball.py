class Ball:
    def __init__(self, width, height):
        self.x = width // 2
        self.y = height // 2
        self.radius = 25
        self.speed = 20
        self.width = width
        self.height = height

    def move(self, direction):
        if direction == "UP":
            if self.y - self.speed - self.radius >= 0:
                self.y -= self.speed

        if direction == "DOWN":
            if self.y + self.speed + self.radius <= self.height:
                self.y += self.speed

        if direction == "LEFT":
            if self.x - self.speed - self.radius >= 0:
                self.x -= self.speed

        if direction == "RIGHT":
            if self.x + self.speed + self.radius <= self.width:
                self.x += self.speed