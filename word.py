import random, time
import pygame as pg


class Word:
    def __init__(self, word, screen_width, screen_height):
        self.font = pg.font.Font(None, 32)
        self.text = word
        self.word = self.font.render(self.text, True, (255, 255, 255))
        self.x = random.randrange(50, screen_width - 50)
        self.y = 0
        self.speed = 3 * random.uniform(3, 3.5)
        self.past_time = time.time()
        self.delay_time = random.uniform(0.1, 0.8)
        print("create word : "+word)

    def update(self):
        if self.past_time + self.delay_time < time.time():
            self.past_time = time.time()

            if self.y < 500:
                self.y += self.speed

    def render(self, screen):
        screen.blit(self.word, (self.x, self.y))